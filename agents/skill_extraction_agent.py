import time
import os
import csv
from datetime import datetime
import uuid
import re
from config.settings import ML_DIR
from agents.base_agent import BaseAgent, AgentMessage

class SkillExtractionAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are a skills-extraction specialist. Given resume text and a list "
            "of candidate keyword matches already found via TF-IDF, identify any "
            "ADDITIONAL skills implied by context (e.g. 'led a team of 5' implies "
            "leadership) that the keyword matcher missed. Categorize every skill "
            "as technical, tool, soft, or domain. Return JSON: {technical: [], "
            "tools: [], soft: [], domain: [], confidence: 0-1 per skill}. Do not "
            "hallucinate skills with no textual evidence."
        )
        super().__init__(
            name="Skill Extraction Agent",
            role="Skill Profiler & Tagging Specialist",
            system_prompt=system_prompt,
            model_backend="hybrid"
        )
        self.taxonomy_path = ML_DIR / "skills_taxonomy.csv"
        self.default_taxonomy = {
            "python": "technical", "java": "technical", "javascript": "technical", "sql": "technical",
            "c++": "technical", "machine learning": "technical", "data science": "technical",
            "react": "tools", "node.js": "tools", "docker": "tools", "git": "tools", "aws": "tools",
            "tableau": "tools", "powerbi": "tools", "excel": "tools",
            "communication": "soft", "leadership": "soft", "teamwork": "soft", "problem solving": "soft",
            "agile": "domain", "scrum": "domain", "project management": "domain", "product management": "domain"
        }

    def _load_taxonomy(self) -> dict:
        taxonomy = {}
        if os.path.exists(self.taxonomy_path):
            try:
                with open(self.taxonomy_path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    next(reader, None)  # Skip header
                    for row in reader:
                        if len(row) >= 2:
                            taxonomy[row[0].strip().lower()] = row[1].strip().lower()
            except Exception as e:
                pass
        
        if not taxonomy:
            taxonomy = self.default_taxonomy
        return taxonomy

    def _keyword_match(self, text: str, taxonomy: dict) -> dict:
        found = {"technical": [], "tools": [], "soft": [], "domain": []}
        text_lower = text.lower()
        
        for skill, category in taxonomy.items():
            # Use boundary regex to avoid matching substrings incorrectly
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                cat_key = category if category in found else "technical"
                if skill.title() not in found[cat_key]:
                    found[cat_key].append(skill.title())
                    
        return found

    def handle(self, message: AgentMessage) -> AgentMessage:
        start_time = time.time()
        resume_text = message.payload.get("resume_text", "")
        
        if not resume_text:
            return AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=message.trace_id,
                from_agent=self.name,
                to_agent=message.from_agent,
                task=message.task,
                payload=message.payload,
                status="error",
                result={"error": "Empty resume text"},
                timestamp=datetime.now(),
                latency_ms=int((time.time() - start_time) * 1000)
            )

        try:
            taxonomy = self._load_taxonomy()
            matched_skills = self._keyword_match(resume_text, taxonomy)
            
            # String representation of matched skills for prompt
            matched_str = ", ".join([f"{k}: {', '.join(v)}" for k, v in matched_skills.items() if v])
            
            user_prompt = (
                f"Resume text:\n{resume_text}\n\n"
                f"Taxonomy skills already matched:\n{matched_str}\n\n"
                f"Please find additional implicit skills and return JSON structured as requested."
            )
            
            llm_result = self.call_llm(user_prompt=user_prompt, json_mode=True, task_size="small")
            
            def clean_skills(raw_list):
                if not isinstance(raw_list, list):
                    return []
                res = []
                for item in raw_list:
                    if isinstance(item, str):
                        res.append(item.strip())
                    elif isinstance(item, dict):
                        for k in ["skill", "name", "title"]:
                            if k in item and isinstance(item[k], str):
                                res.append(item[k].strip())
                                break
                return res

            llm_tech = clean_skills(llm_result.get("technical", []))
            llm_tools = clean_skills(llm_result.get("tools", []))
            llm_soft = clean_skills(llm_result.get("soft", []))
            llm_domain = clean_skills(llm_result.get("domain", []))

            # Merge taxonomical matches and LLM extracted matches
            final_skills = {
                "technical": list(set(matched_skills["technical"] + llm_tech)),
                "tools": list(set(matched_skills["tools"] + llm_tools)),
                "soft": list(set(matched_skills["soft"] + llm_soft)),
                "domain": list(set(matched_skills["domain"] + llm_domain))
            }
            
            # Re-capitalize properly
            for key in final_skills:
                final_skills[key] = [str(x).strip().title() for x in final_skills[key] if str(x).strip()]
                
            confidence_scores = llm_result.get("confidence", {})
            # Make sure we have a confidence value for all skills
            all_confidence = {}
            for category, skills in final_skills.items():
                for skill in skills:
                    all_confidence[skill] = confidence_scores.get(skill, 0.9 if skill in matched_skills[category] else 0.75)
                    
            return AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=message.trace_id,
                from_agent=self.name,
                to_agent=message.from_agent,
                task=message.task,
                payload=message.payload,
                status="success",
                result={
                    "skills": final_skills,
                    "confidence": all_confidence
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
