import os
import requests
import json
from typing import Dict, List, Optional
import yaml
from dotenv import load_dotenv

load_dotenv()

class FreeLLMClient:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        self.providers = self.config['llm']['providers']
        self.current_provider = 0
        
    def _get_openrouter_response(self, prompt: str, model: str) -> str:
        """Use OpenRouter's free tier models"""
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("OpenRouter API key not found")
            
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501",  # For Streamlit
            "X-Title": "CV Sorting System"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
            "temperature": 0.3
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            raise Exception(f"API call failed: {response.status_code}")
    
    def _get_huggingface_response(self, prompt: str, model: str) -> str:
        """Use Hugging Face's free inference API"""
        api_key = os.getenv('HUGGINGFACE_API_KEY')
        if not api_key:
            raise ValueError("Hugging Face API key not found")
            
        headers = {"Authorization": f"Bearer {api_key}"}
        
        data = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.3,
                "return_full_text": False
            }
        }
        
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{model}",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get('generated_text', '')
            return str(result)
        else:
            raise Exception(f"HF API call failed: {response.status_code}")
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using available free models"""
        for provider in self.providers:
            try:
                if provider['name'] == 'openrouter':
                    model = provider['models'][0]  # Use first available free model
                    return self._get_openrouter_response(prompt, model)
                elif provider['name'] == 'huggingface':
                    model = provider['models'][0]
                    return self._get_huggingface_response(prompt, model)
            except Exception as e:
                print(f"Failed with provider {provider['name']}: {e}")
                continue
        
        raise Exception("All LLM providers failed")