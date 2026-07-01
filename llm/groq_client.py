import os
import logging
from groq import Groq

logger = logging.getLogger(__name__)

def call_groq_api(system_prompt: str, user_prompt: str, model: str, json_mode: bool = False) -> str:
    """
    Sends request to Groq API.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured in environment variables.")
    
    client = Groq(api_key=api_key)
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": 0.1
    }
    
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
        
    logger.info(f"Calling Groq model={model} with json_mode={json_mode}")
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content
