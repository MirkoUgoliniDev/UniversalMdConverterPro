import google.generativeai as genai
from openai import OpenAI
import time

class AIEngine:
    def __init__(self):
        self.last_error = ""

    def get_available_models(self, provider, api_key):
        """Restituisce la lista dei modelli per il provider specificato"""
        if not api_key: return []
        
        try:
            if provider == "Google Gemini":
                genai.configure(api_key=api_key)
                models = [m.name.replace("models/","") for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
                return sorted(models, reverse=True)
            
            elif provider == "OpenAI (GPT)":
                client = OpenAI(api_key=api_key)
                models = [m.id for m in client.models.list() if "gpt" in m.id]
                return sorted(models, reverse=True)
                
        except Exception as e:
            self.last_error = str(e)
            return []
        return []

    def ask_ai(self, provider, api_key, model_name, prompt):
        """Chiamata generica all'AI"""
        if not api_key: 
            self.last_error = "API Key mancante"
            return None

        try:
            if provider == "Google Gemini":
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text.strip()
                
            elif provider == "OpenAI (GPT)":
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )
                return response.choices[0].message.content.strip()
                
        except Exception as e:
            self.last_error = str(e)
            if "429" in self.last_error:
                time.sleep(15) # Auto-wait on rate limit
            return None