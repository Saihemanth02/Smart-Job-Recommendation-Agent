import os
import logging
# pyrefly: ignore [missing-import]
import google.generativeai as genai

logger = logging.getLogger(__name__)

def call_gemini_api(system_prompt: str, user_prompt: str, model: str, json_mode: bool = False) -> str:
    """
    Sends request to Gemini API.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured in environment variables.")
        
    genai.configure(api_key=api_key)
    
    generation_config = {
        "temperature": 0.1
    }
    if json_mode:
        generation_config["response_mime_type"] = "application/json"
        
    logger.info(f"Calling Gemini model={model} with json_mode={json_mode}")
    
    model_instance = genai.GenerativeModel(
        model_name=model,
        system_instruction=system_prompt
    )
    
    response = model_instance.generate_content(
        user_prompt,
        generation_config=generation_config
    )
    
    return response.text
