import time
import os
from datetime import datetime
import uuid
from agents.base_agent import BaseAgent, AgentMessage

class SkillGapRoadmapAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are a learning-path designer for early-career tech professionals.\n"
            "Given the candidate's current skills and the target role's required "
            "skill set, identify the missing skills ranked by hiring impact (high/ "
            "medium/low priority). Then build a realistic 90-day roadmap broken "
            "into 3 phases of ~30 days each. For each phase list: skills to learn, "
            "1-2 concrete free/low-cost resources, and a small project to prove "
            "the skill. Keep total output under 400 words. Be concrete, not "
            "motivational fluff."
        )
        super().__init__(
            name="Skill Gap & Roadmap Agent",
            role="Learning Path & Curriculum Designer",
            system_prompt=system_prompt,
            model_backend="hybrid"
        )
        
        # Standard skill taxonomies per role (from seed generator)
        self.role_requirements = {
            "Frontend Developer": ["React", "JavaScript", "HTML", "CSS", "Git", "Tailwind CSS", "Vue.js", "Angular", "TypeScript", "Bootstrap"],
            "Java Developer": ["Java", "Spring Boot", "Hibernate", "SQL", "Git", "REST APIs", "Maven", "JUnit", "Docker", "PostgreSQL"],
            "DevOps Engineer": ["Docker", "Kubernetes", "AWS", "Jenkins", "Linux", "Git", "Terraform", "Ansible", "Shell Scripting", "Python"],
            "ML Engineer": ["Python", "TensorFlow", "PyTorch", "Scikit-Learn", "Pandas", "NumPy", "SQL", "Git", "Docker", "Machine Learning"],
            "Data Scientist": ["Python", "SQL", "Machine Learning", "Tableau", "Statistics", "Pandas", "NumPy", "Deep Learning", "Git", "PowerBI"],
            "Business Analyst": ["SQL", "Excel", "Tableau", "PowerBI", "Agile", "Scrum", "Jira", "Communication", "Python", "Requirements Gathering"],
            "UX Designer": ["Figma", "Adobe XD", "Wireframing", "Prototyping", "HTML", "CSS", "User Research", "Interaction Design", "Illustrator", "Photoshop"],
            "Marketing Executive": ["SEO", "SEM", "Social Media Marketing", "Content Writing", "Google Analytics", "Excel", "Email Marketing", "Communication", "Copywriting", "Photoshop"],
            "Mechanical Design Engineer": ["AutoCAD", "SolidWorks", "CATIA", "Fusion 360", "ANSYS", "GD&T", "Thermodynamics", "FEA", "Materials Science", "Excel"],
            "Systems Analyst": ["SQL", "UML", "Systems Design", "Agile", "Business Analysis", "Git", "Java", "Python", "Excel", "Jira"]
        }

    def handle(self, message: AgentMessage) -> AgentMessage:
        start_time = time.time()
        
        payload = message.payload
        candidate_skills = payload.get("skills", {})
        target_role = payload.get("target_role", "")
        
        if not target_role:
            return AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=message.trace_id,
                from_agent=self.name,
                to_agent=message.from_agent,
                task=message.task,
                payload=message.payload,
                status="error",
                result={"error": "Target job role is required"},
                timestamp=datetime.now(),
                latency_ms=int((time.time() - start_time) * 1000)
            )

        try:
            # Flatten current skills
            current_skills_flat = []
            for cat, skills in candidate_skills.items():
                current_skills_flat.extend([s.lower().strip() for s in skills])
                
            required_skills = self.role_requirements.get(target_role, [])
            
            # Identify missing skills
            missing_skills = []
            for skill in required_skills:
                if skill.lower().strip() not in current_skills_flat:
                    missing_skills.append(skill)
                    
            # Prioritize missing skills
            # First 3 skills are high priority, next 3 medium, rest low
            prioritized_gaps = {
                "high": missing_skills[:3],
                "medium": missing_skills[3:6],
                "low": missing_skills[6:]
            }
            
            # Generate roadmap via LLM (large task size for detailed generation)
            user_prompt = (
                f"Target Role: {target_role}\n"
                f"Candidate's Current Skills: {', '.join(current_skills_flat)}\n"
                f"Missing Skills (High Priority): {', '.join(prioritized_gaps['high'])}\n"
                f"Missing Skills (Medium Priority): {', '.join(prioritized_gaps['medium'])}\n"
                f"Missing Skills (Low Priority): {', '.join(prioritized_gaps['low'])}\n\n"
                f"Create a 90-day, 3-phase study roadmap according to the system instructions. Limit output to 400 words."
            )
            
            roadmap_text = self.call_llm(user_prompt=user_prompt, json_mode=False, task_size="large")
            
            return AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=message.trace_id,
                from_agent=self.name,
                to_agent=message.from_agent,
                task=message.task,
                payload=message.payload,
                status="success",
                result={
                    "missing_skills": missing_skills,
                    "prioritized_gaps": prioritized_gaps,
                    "roadmap": roadmap_text
                },
                timestamp=datetime.now(),
                latency_ms=int((time.time() - start_time) * 1000)
            )
        except Exception as e:
            return AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=message.trace_id,
                from_agent=self.name,
                to_agent=message.from_agent,
                task=message.task,
                payload=message.payload,
                status="error",
                result={"error": str(e)},
                timestamp=datetime.now(),
                latency_ms=int((time.time() - start_time) * 1000)
            )
