import time
import os
import re
import joblib
import numpy as np
from datetime import datetime
import uuid
from scipy.sparse import hstack

from config.settings import MODEL_DIR
from agents.base_agent import BaseAgent, AgentMessage
from ml.preprocessing import lemmatize_light

class JobPredictionAgent(BaseAgent):
    def __init__(self):
        system_prompt = (
            "You are a career-fit analyst. Given a candidate's top predicted job "
            "roles with confidence scores and the specific skills/experience that "
            "drove each prediction (from Random Forest feature importances), write "
            "a 2-3 sentence plain-English explanation per role. Be specific — cite "
            "the actual skills, not generic praise. If confidence is below 0.5, "
            "say so plainly instead of hedging vaguely."
        )
        super().__init__(
            name="Job Prediction Agent",
            role="Machine Learning Career Predictor",
            system_prompt=system_prompt,
            model_backend="sklearn"
        )
        
        # Load ML artifacts
        try:
            self.vectorizer = joblib.load(MODEL_DIR / "tfidf_vectorizer.pkl")
            self.nb_model = joblib.load(MODEL_DIR / "job_category_nb.pkl")
            self.rf_model = joblib.load(MODEL_DIR / "job_role_rf.pkl")
            self.artifacts_loaded = True
        except Exception as e:
            self.artifacts_loaded = False
            print(f"Error loading Job Prediction Agent models: {str(e)}")

    def _estimate_experience_years(self, experience_list) -> int:
        if not experience_list:
            return 0
        total_years = 0.0
        for exp in experience_list:
            duration = str(exp.get("duration", "")).lower()
            years_match = re.search(r'(\d+(?:\.\d+)?)\s*yr|year', duration)
            months_match = re.search(r'(\d+(?:\.\d+)?)\s*mo|month', duration)
            if years_match:
                total_years += float(years_match.group(1))
            elif months_match:
                total_years += float(months_match.group(1)) / 12.0
            else:
                total_years += 1.0  # Fallback: assume 1 year per listed role
        return max(0, int(round(total_years)))

    def _map_education(self, education_list) -> int:
        if not education_list:
            return 2  # default to B.Tech
        edu_str = " ".join([str(e) for e in education_list]).lower()
        if "m.tech" in edu_str or "mtech" in edu_str:
            return 5
        elif "mca" in edu_str:
            return 4
        elif "m.sc" in edu_str or "msc" in edu_str:
            return 3
        elif "b.tech" in edu_str or "btech" in edu_str or "b.e" in edu_str or "be" in edu_str:
            return 2
        elif "b.sc" in edu_str or "bsc" in edu_str:
            return 1
        return 2

    def handle(self, message: AgentMessage) -> AgentMessage:
        start_time = time.time()
        
        if not self.artifacts_loaded:
            return AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=message.trace_id,
                from_agent=self.name,
                to_agent=message.from_agent,
                task=message.task,
                payload=message.payload,
                status="error",
                result={"error": "ML model pickle files not found or loaded"},
                timestamp=datetime.now(),
                latency_ms=int((time.time() - start_time) * 1000)
            )

        payload = message.payload
        skills_dict = payload.get("skills", {})
        parsed_resume = payload.get("parsed_resume", {})
        
        # Flatten all skills to text for TF-IDF
        all_skills_flat = []
        for cat, skills in skills_dict.items():
            all_skills_flat.extend(skills)
        skills_text = " ".join(all_skills_flat)
        
        # Build text string matching what was trained on
        projects_text = " ".join([str(p) for p in parsed_resume.get("projects", [])])
        certs_text = " ".join([str(c) for c in parsed_resume.get("certifications", [])])
        
        # Clean text
        raw_text_combined = f"Skills: {skills_text} Projects: {projects_text} Certs: {certs_text}"
        cleaned_text = lemmatize_light(raw_text_combined)
        
        try:
            # 1. Transform via TF-IDF
            X_tfidf = self.vectorizer.transform([cleaned_text])
            
            # 2. Extract numeric features
            exp_years = self._estimate_experience_years(parsed_resume.get("experience", []))
            num_skills = len(all_skills_flat)
            num_certs = len(parsed_resume.get("certifications", []))
            edu_encoded = self._map_education(parsed_resume.get("education", []))
            
            X_numeric = np.array([[exp_years, num_skills, num_certs, edu_encoded]])
            
            # 3. Stack features
            X_combined = hstack([X_tfidf, X_numeric])
            
            # 4. Predict job category (Naive Bayes)
            nb_pred = self.nb_model.predict(X_tfidf)[0]
            
            # 5. Predict job role probabilities (Random Forest)
            rf_probs = self.rf_model.predict_proba(X_combined)[0]
            classes = self.rf_model.classes_
            
            # Sort roles by confidence
            sorted_indices = np.argsort(rf_probs)[::-1]
            top_roles = []
            
            # Get Top 3 roles
            for i in sorted_indices[:3]:
                role_name = classes[i]
                confidence = float(rf_probs[i])
                top_roles.append({"role": role_name, "raw_confidence": confidence})
                
            # Cross-reference with NB category for category match boost
            # Load metadata for categories of roles
            # Let's map roles to category for validation
            role_to_cat = {
                "Frontend Developer": "Software Development",
                "Java Developer": "Software Development",
                "DevOps Engineer": "Software Development",
                "ML Engineer": "Data & Analytics",
                "Data Scientist": "Data & Analytics",
                "Business Analyst": "Data & Analytics",
                "UX Designer": "Design",
                "Marketing Executive": "Marketing",
                "Mechanical Design Engineer": "Core/Mechanical",
                "Systems Analyst": "Business/Ops"
            }
            
            for role_info in top_roles:
                role_cat = role_to_cat.get(role_info["role"], "Unknown")
                category_match = (role_cat == nb_pred)
                role_info["category"] = role_cat
                role_info["category_match"] = category_match
                # Apply 10% boost if category matches, cap at 1.0
                boost = 1.1 if category_match else 1.0
                role_info["confidence"] = min(1.0, role_info["raw_confidence"] * boost)
            
            # Expose Feature Importances for explainability
            # TF-IDF vocabulary mapping + 4 numeric feature names
            vocab = {v: k for k, v in self.vectorizer.vocabulary_.items()}
            feature_names = [vocab.get(i, f"term_{i}") for i in range(len(vocab))]
            feature_names.extend(["Years Experience", "Skills Count", "Certifications Count", "Education Level"])
            
            # Get overall RF importances
            importances = self.rf_model.feature_importances_
            
            # Active features in candidate vector
            dense_vector = X_combined.toarray()[0]
            active_indices = np.where(dense_vector > 0)[0]
            
            candidate_features = []
            for idx in active_indices:
                feat_name = feature_names[idx]
                feat_imp = float(importances[idx])
                candidate_features.append({"feature": feat_name, "importance": feat_imp})
                
            # Sort candidate active features by importance
            candidate_features = sorted(candidate_features, key=lambda x: x["importance"], reverse=True)[:10]
            
            # 6. Generate natural language explanation using LLM router
            roles_summary = "\n".join([
                f"- Role: {r['role']}, Confidence: {r['confidence']:.2f}, Category Match: {r['category_match']}"
                for r in top_roles
            ])
            features_summary = ", ".join([f"{f['feature']} (imp: {f['importance']:.3f})" for f in candidate_features])
            
            user_prompt = (
                f"Candidate's top predicted roles:\n{roles_summary}\n\n"
                f"Top contributing features from candidate's profile:\n{features_summary}\n\n"
                f"Please generate a structured JSON explanation. Return a dictionary mapping each role "
                f"to its 2-3 sentence explanation. Output format: "
                f'{{"explanations": {{"Role 1": "Explanation 1", "Role 2": "Explanation 2", "Role 3": "Explanation 3"}}}}'
            )
            
            llm_explanations = self.call_llm(user_prompt=user_prompt, json_mode=True, task_size="small")
            
            # Merge explanation texts with roles lists
            explanations_dict = llm_explanations.get("explanations", {})
            for r in top_roles:
                r["explanation"] = explanations_dict.get(
                    r["role"], 
                    f"Fit based on key skills including {', '.join([f['feature'] for f in candidate_features if f['feature'] not in ['Years Experience', 'Skills Count', 'Certifications Count', 'Education Level']][:3])}."
                )
                
            return AgentMessage(
                message_id=str(uuid.uuid4()),
                trace_id=message.trace_id,
                from_agent=self.name,
                to_agent=message.from_agent,
                task=message.task,
                payload=message.payload,
                status="success",
                result={
                    "coarse_category": nb_pred,
                    "top_roles": top_roles,
                    "candidate_features": candidate_features,
                    "experience_years": exp_years,
                    "education_encoded": edu_encoded
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
