import json
import os

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        
        # DEFAULTS
        self.defaults = {
            "ai_provider": "Google Gemini",
            "api_key_gemini": "",
            "api_key_openai": "",
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
        
        # Dati correnti
        self.data = self.defaults.copy()
        self.load()

    def load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    loaded = json.load(f)
                    # Aggiorna i default con i dati caricati (mantiene chiavi nuove se aggiunte in futuro)
                    self.data.update(loaded)
            except Exception as e:
                print(f"Errore caricamento config: {e}")

    def save(self):
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Errore salvataggio config: {e}")

    def get(self, key):
        return self.data.get(key, self.defaults.get(key))

    def set(self, key, value):
        self.data[key] = value