import re
import json
import time
import logging
from datetime import datetime
from config.settings import MODEL_CONFIGS
from llm.groq_client import call_groq_api
from llm.gemini_client import call_gemini_api

logger = logging.getLogger(__name__)

# Global list of LLM calls for visualization in Settings/Activity pages
llm_call_history = []

def clean_json_text(text: str) -> str:
    """
    Cleans markdown code block wraps (like ```json ... ```) from strings
    to ensure it can be parsed by json.loads().
    """
    cleaned = text.strip()
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', cleaned, re.IGNORECASE)
    if match:
        cleaned = match.group(1).strip()
    return cleaned

def call_llm(system_prompt: str, user_prompt: str, json_mode: bool = False, task_size: str = "small") -> dict | str:
    """
    Calls LLM with fallback mechanism.
    Primary: Groq
    Fallback: Gemini
    """
    start_time = time.time()
    
    models = MODEL_CONFIGS.get(task_size, MODEL_CONFIGS["small"])
    groq_model = models["groq"]
    gemini_model = models["gemini"]
    
    backend_used = "groq"
    model_used = groq_model
    status = "success"
    error_msg = None
    response_text = ""
    
    try:
        # Try Groq primary
        response_text = call_groq_api(system_prompt, user_prompt, groq_model, json_mode=json_mode)
    except Exception as e:
        logger.warning(f"Groq API call failed, falling back to Gemini. Error: {str(e)}")
        backend_used = "gemini"
        model_used = gemini_model
        try:
            # Fallback to Gemini
            response_text = call_gemini_api(system_prompt, user_prompt, gemini_model, json_mode=json_mode)
            status = "fallback_success"
        except Exception as gemini_err:
            status = "error"
            error_msg = str(gemini_err)
            logger.error(f"Gemini API call failed as well. Error: {str(gemini_err)}")
            raise gemini_err
            
    latency_ms = int((time.time() - start_time) * 1000)
    
    # Record call metadata
    call_record = {
        "timestamp": datetime.now().isoformat(),
        "task_size": task_size,
        "primary_backend": "groq",
        "primary_model": groq_model,
        "actual_backend": backend_used,
        "actual_model": model_used,
        "status": status,
        "latency_ms": latency_ms,
        "error_message": error_msg,
        "json_mode": json_mode
    }
    llm_call_history.append(call_record)
    
    # If json_mode is requested, clean and parse the output
    if json_mode:
        cleaned_text = clean_json_text(response_text)
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError as je:
            logger.error(f"Failed to parse JSON from response. Cleaned text was: {cleaned_text}")
            # Try to return raw text or build an error dict
            return {"error": "Failed to parse JSON", "raw_response": response_text}
            
    return response_text
