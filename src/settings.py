import json
import os

class ConfigManager:
    def __init__(self):
        # File pubblici (Configurazione UI, Prompt, Keywords) -> VA SU GITHUB
        self.settings_file = "settings.json"
        
        # File privati (API Keys) -> NON VA SU GITHUB (va in .gitignore)
        self.secrets_file = ".secrets.json"
        
        # DEFAULTS (Configurazione Base)
        self.defaults = {
            "ai_provider": "Google Gemini",
            "pref_model_gemini": "gemini-2.0-flash",
            "pref_model_openai": "gpt-4o",
            "last_url": "",
            "mode_web": "Smart Filter",
            "mode_pdf": "Raw Text",
            "verb_web": "Normale",
            "verb_pdf": "Normale",
            "kw_web_good": ["manual", "guide", "docs", "api", "reference", "datasheet", "chapter"],
            "kw_web_bad": ["login", "signup", "facebook", "privacy", "cart", "shop", "price", "twitter"],
            "kw_pdf_good": ["chapter", "capitolo", "introduction", "overview", "technical", "specifications"],
            "kw_pdf_bad": ["copyright", "all rights reserved", "blank page", "advertisement", "indice", "index"],
            "prompt_web": """Sei un crawler tecnico. Pagina corrente: {context_url}.
Link trovati: {links_text}
OBIETTIVO: Seleziona SOLO i link per scaricare Documentazione Tecnica, Manuali, API.
IGNORA: Login, Social, Home, Privacy.
RISPOSTA: Array JSON di stringhe (URL). Esempio: ["/docs/intro", "/manual.pdf"]""",
            "prompt_pdf": """Sei un esperto formattatore. Pulisci questo testo estratto da un PDF (Pagina {page_num}).
COMPITI:
1. Formatta in Markdown pulito.
2. Rimuovi intestazioni e piè di pagina ripetuti.
3. Unisci frasi spezzate.
4. Restituisci SOLO il markdown.
TESTO:
{raw_text}"""
        }
        
        # DEFAULTS SECRETS (Chiavi vuote)
        self.defaults_secrets = {
            "api_key_gemini": "",
            "api_key_openai": ""
        }
        
        # Dizionario in memoria che unisce tutto
        self.data = {}
        self.load()

    def load(self):
        # 1. Carica Settings Pubblici
        self.data = self.defaults.copy()
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r") as f:
                    self.data.update(json.load(f))
            except Exception as e:
                print(f"Errore caricamento settings: {e}")

        # 2. Carica Segreti (Se esistono)
        secrets_data = self.defaults_secrets.copy()
        if os.path.exists(self.secrets_file):
            try:
                with open(self.secrets_file, "r") as f:
                    secrets_data.update(json.load(f))
            except Exception as e:
                print(f"Errore caricamento secrets: {e}")
        
        # Unisci i segreti nei dati in memoria
        self.data.update(secrets_data)

    def save(self):
        # Separa i dati in due dizionari prima di salvare
        settings_to_save = {k: v for k, v in self.data.items() if k not in ["api_key_gemini", "api_key_openai"]}
        secrets_to_save = {
            "api_key_gemini": self.data.get("api_key_gemini", ""),
            "api_key_openai": self.data.get("api_key_openai", "")
        }

        try:
            # Salva settings.json (Pubblico)
            with open(self.settings_file, "w") as f:
                json.dump(settings_to_save, f, indent=4)
            
            # Salva .secrets.json (Privato)
            with open(self.secrets_file, "w") as f:
                json.dump(secrets_to_save, f, indent=4)
                
        except Exception as e:
            print(f"Errore salvataggio config: {e}")

    def get(self, key):
        return self.data.get(key, self.defaults.get(key, ""))

    def set(self, key, value):
        self.data[key] = value