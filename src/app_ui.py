import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import time
import json
import webbrowser
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from urllib.parse import urljoin, urlparse
import fitz  # PyMuPDF

# IMPORT DEI NOSTRI MODULI
from settings import ConfigManager
from utils import clean_filename, get_unique_filepath, heuristic_score
from ai_engine import AIEngine

class UniversalConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Universal Converter Pro (Modular Architecture)")
        self.root.geometry("1100x950")
        
        # Inizializza Moduli
        self.cfg = ConfigManager()
        self.ai = AIEngine()
        
        self.is_running = False
        self.visited_urls = set()
        self.pdf_files_to_convert = []

        # --- UI SETUP ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=10)
        
        self.tab_crawler = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_crawler, text="🌍 Web Crawler")
        
        self.tab_pdf = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_pdf, text="📄 PDF Converter")
        
        self.tab_settings = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_settings, text="⚙️ Impostazioni")
        
        self.setup_settings_tab()
        self.setup_crawler_tab()
        self.setup_pdf_tab()
        self.setup_log_area()
        
        # Load UI state from config
        self.load_ui_from_config()

    # ================= UI HELPERS =================
    def create_icon_button(self, parent, text, command):
        return tk.Button(parent, text=text, font=("Segoe UI Emoji", 11), command=command,
                        relief="flat", bd=0, bg="#f0f0f0", activebackground="#e0e0e0", 
                        cursor="hand2", padx=4, pady=2, overrelief="groove")

    def log(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert("end", msg+"\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def log_discard(self, msg):
        self.discard_text.config(state="normal")
        self.discard_text.insert("end", f"• {msg}\n")
        self.discard_text.see("end")
        self.discard_text.config(state="disabled")

    def clear_logs(self):
        self.log_text.config(state="normal"); self.log_text.delete("1.0", "end"); self.log_text.config(state="disabled")
        self.discard_text.config(state="normal"); self.discard_text.delete("1.0", "end"); self.discard_text.config(state="disabled")

    # ================= SETTINGS TAB =================
    def setup_settings_tab(self):
        main_frame = ttk.Frame(self.tab_settings, padding=20); main_frame.pack(fill="both", expand=True)
        
        # Global AI
        global_frame = ttk.LabelFrame(main_frame, text="🌎 Configurazione Motore AI", padding=15)
        global_frame.pack(fill="x", pady=10); global_frame.columnconfigure(1, weight=1)
        
        ttk.Label(global_frame, text="Provider AI:").grid(row=0, column=0, sticky="w")
        self.provider_combo = ttk.Combobox(global_frame, values=["Google Gemini", "OpenAI (GPT)"], state="readonly", width=25)
        self.provider_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.provider_combo.bind("<<ComboboxSelected>>", self.update_provider_ui)

        ttk.Label(global_frame, text="API Key:").grid(row=1, column=0, sticky="w")
        self.key_entry = ttk.Entry(global_frame, show="*"); self.key_entry.grid(row=1, column=1, sticky="ew", padx=5)
        
        ctrl_frame = ttk.Frame(global_frame); ctrl_frame.grid(row=1, column=2, padx=5, sticky="e")
        self.show_key_var = tk.BooleanVar()
        ttk.Checkbutton(ctrl_frame, text="Show", variable=self.show_key_var, 
                       command=lambda: self.key_entry.config(show="" if self.show_key_var.get() else "*")).pack(side="left")
        self.create_icon_button(ctrl_frame, "🔑", self.open_api_link).pack(side="left", padx=5)

        ttk.Label(global_frame, text="Modello Attivo:").grid(row=2, column=0, sticky="w", pady=10)
        self.model_combo = ttk.Combobox(global_frame, state="normal"); self.model_combo.grid(row=2, column=1, sticky="ew", padx=5)
        self.create_icon_button(global_frame, "🔄", self.fetch_models_ui).grid(row=2, column=2, sticky="e", padx=5)

        # Web & PDF Buttons
        web_frame = ttk.LabelFrame(main_frame, text="🌍 Web Config", padding=15); web_frame.pack(fill="x", pady=10)
        web_frame.columnconfigure(1, weight=1); web_frame.columnconfigure(3, weight=1)
        ttk.Label(web_frame, text="Filtro Smart:").grid(row=0, column=0, sticky="w")
        self.create_icon_button(web_frame, "📝", lambda: self.open_list_editor("web")).grid(row=0, column=1, sticky="w", padx=10)
        ttk.Label(web_frame, text="Prompt AI:").grid(row=0, column=2, sticky="e")
        self.create_icon_button(web_frame, "🧠", lambda: self.open_prompt_editor("web")).grid(row=0, column=3, sticky="w", padx=5)

        pdf_frame = ttk.LabelFrame(main_frame, text="📄 PDF Config", padding=15); pdf_frame.pack(fill="x", pady=5)
        pdf_frame.columnconfigure(1, weight=1); pdf_frame.columnconfigure(3, weight=1)
        ttk.Label(pdf_frame, text="Filtro Smart:").grid(row=0, column=0, sticky="w")
        self.create_icon_button(pdf_frame, "📝", lambda: self.open_list_editor("pdf")).grid(row=0, column=1, sticky="w", padx=10)
        ttk.Label(pdf_frame, text="Prompt AI:").grid(row=0, column=2, sticky="e")
        self.create_icon_button(pdf_frame, "🧠", lambda: self.open_prompt_editor("pdf")).grid(row=0, column=3, sticky="w", padx=5)

        tk.Button(main_frame, text="💾 SALVA IMPOSTAZIONI", font=("Segoe UI", 10), relief="groove", bg="#f0f0f0", command=self.save_all_config).pack(pady=20, fill="x")

    def setup_log_area(self):
        log_frame = ttk.LabelFrame(self.root, text="Monitoraggio Attività", padding=10, labelanchor='n')
        log_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        log_tools = ttk.Frame(log_frame); log_tools.pack(fill="x", pady=(0, 5))
        ttk.Label(log_tools, text="").pack(side="left") 
        self.create_icon_button(log_tools, "🧹", self.clear_logs).pack(side="right")

        nb = ttk.Notebook(log_frame); nb.pack(fill="both", expand=True)
        t1 = ttk.Frame(nb); nb.add(t1, text="📜 Processo")
        self.log_text = tk.Text(t1, height=10, state="disabled", font=("Consolas", 9), bg="#f0f0f0", bd=0); self.log_text.pack(fill="both", expand=True)
        t2 = ttk.Frame(nb); nb.add(t2, text="🗑️ Scartati")
        self.discard_text = tk.Text(t2, height=10, state="disabled", font=("Consolas", 9), bg="#fff0f0", bd=0, fg="#c0392b"); self.discard_text.pack(fill="both", expand=True)
        
        self.status_var = tk.StringVar(value="Pronto")
        ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w").pack(fill="x", side="bottom")

    # ================= LOGICA UI =================
    def save_all_config(self):
        # Update config object from UI
        self.cfg.set("ai_provider", self.provider_combo.get())
        
        provider = self.provider_combo.get()
        key = self.key_entry.get().strip()
        if "Gemini" in provider: self.cfg.set("api_key_gemini", key); self.cfg.set("pref_model_gemini", self.model_combo.get())
        else: self.cfg.set("api_key_openai", key); self.cfg.set("pref_model_openai", self.model_combo.get())
        
        # Save other tabs settings
        self.cfg.set("last_url", self.url_entry.get().strip())
        self.cfg.set("mode_web", self.crawler_mode_combo.get())
        self.cfg.set("verb_web", self.crawler_verb_combo.get())
        self.cfg.set("mode_pdf", self.pdf_mode_combo.get())
        self.cfg.set("verb_pdf", self.pdf_verb_combo.get())
        
        self.cfg.save()
        self.log("Impostazioni salvate.")

    def load_ui_from_config(self):
        self.provider_combo.set(self.cfg.get("ai_provider"))
        self.update_provider_ui() # Sets Key and Model from config
        
        self.url_entry.delete(0, tk.END); self.url_entry.insert(0, self.cfg.get("last_url"))
        self.crawler_mode_combo.set(self.cfg.get("mode_web"))
        self.crawler_verb_combo.set(self.cfg.get("verb_web"))
        self.pdf_mode_combo.set(self.cfg.get("mode_pdf"))
        self.pdf_verb_combo.set(self.cfg.get("verb_pdf"))

    def update_provider_ui(self, event=None):
        provider = self.provider_combo.get()
        if "Gemini" in provider:
            self.key_entry.delete(0, tk.END); self.key_entry.insert(0, self.cfg.get("api_key_gemini"))
            self.model_combo.set(self.cfg.get("pref_model_gemini"))
        else:
            self.key_entry.delete(0, tk.END); self.key_entry.insert(0, self.cfg.get("api_key_openai"))
            self.model_combo.set(self.cfg.get("pref_model_openai"))

    def fetch_models_ui(self):
        provider = self.provider_combo.get()
        key = self.key_entry.get().strip()
        self.log(f"Recupero modelli {provider}...")
        models = self.ai.get_available_models(provider, key)
        if models:
            self.model_combo['values'] = models
            self.model_combo.current(0)
            messagebox.showinfo("OK", f"Trovati {len(models)} modelli")
        else:
            self.log(f"Errore: {self.ai.last_error}")
            messagebox.showerror("Errore", self.ai.last_error)

    def open_api_link(self):
        url = "https://aistudio.google.com/app/apikey" if "Gemini" in self.provider_combo.get() else "https://platform.openai.com/api-keys"
        webbrowser.open(url, new=2)

    # ================= PROCESS CRAWLER =================
    def setup_crawler_tab(self):
        f = ttk.Frame(self.tab_crawler, padding=20); f.pack(fill="both", expand=True); f.columnconfigure(0, weight=1)
        input_frame = ttk.LabelFrame(f, text="Target", padding=15); input_frame.grid(row=0, column=0, sticky="ew", pady=10); input_frame.columnconfigure(1, weight=1)
        ttk.Label(input_frame, text="URL:").grid(row=0, column=0, sticky="w")
        self.url_entry = ttk.Entry(input_frame); self.url_entry.grid(row=0, column=1, sticky="ew", padx=10)
        
        conf_frame = ttk.LabelFrame(f, text="Configurazione", padding=15); conf_frame.grid(row=1, column=0, sticky="ew", pady=10); conf_frame.columnconfigure(1, weight=1); conf_frame.columnconfigure(3, weight=1)
        ttk.Label(conf_frame, text="Metodo:").grid(row=0, column=0, sticky="w")
        self.crawler_mode_combo = ttk.Combobox(conf_frame, values=["Smart Filter", "AI Engine"], state="readonly", width=20); self.crawler_mode_combo.grid(row=0, column=1, sticky="w", padx=10)
        ttk.Label(conf_frame, text="Log:").grid(row=0, column=2, sticky="e")
        self.crawler_verb_combo = ttk.Combobox(conf_frame, values=["Normale", "Dettagliato"], state="readonly", width=15); self.crawler_verb_combo.grid(row=0, column=3, sticky="w", padx=10)
        ttk.Label(conf_frame, text="Profondità:").grid(row=1, column=0, sticky="w", pady=15)
        self.depth_spinbox = ttk.Spinbox(conf_frame, from_=1, to=10, width=5); self.depth_spinbox.set(2); self.depth_spinbox.grid(row=1, column=1, sticky="w", padx=10)
        self.restrict_var = tk.BooleanVar(value=True); ttk.Checkbutton(conf_frame, text="Resta nel dominio", variable=self.restrict_var).grid(row=1, column=2, columnspan=2, sticky="w")
        
        out_frame = ttk.LabelFrame(f, text="Output", padding=15); out_frame.grid(row=2, column=0, sticky="ew", pady=10); out_frame.columnconfigure(0, weight=1)
        self.crawl_path_var = tk.StringVar(value=os.path.join(os.getcwd(), "docs_web")); ttk.Entry(out_frame, textvariable=self.crawl_path_var).grid(row=0, column=0, sticky="ew")
        self.create_icon_button(out_frame, "📂", lambda: self.choose_directory(self.crawl_path_var)).grid(row=0, column=1, padx=10)
        
        act_frame = ttk.Frame(f, padding=10); act_frame.grid(row=3, column=0, sticky="ew", pady=10); act_frame.columnconfigure(0, weight=1); act_frame.columnconfigure(1, weight=1)
        tk.Button(act_frame, text="▶️  AVVIA", font=("Segoe UI", 11), height=2, command=self.start_crawling).grid(row=0, column=0, sticky="ew", padx=10)
        tk.Button(act_frame, text="⏹️  STOP", font=("Segoe UI", 11), height=2, command=self.stop_process).grid(row=0, column=1, sticky="ew", padx=10)

    def start_crawling(self):
        self.save_all_config(); self.is_running = True
        threading.Thread(target=self.run_crawler, daemon=True).start()

    def run_crawler(self):
        url = self.url_entry.get().strip()
        out = self.crawl_path_var.get()
        if not os.path.exists(out): os.makedirs(out, exist_ok=True)
        
        queue = [(url, 0)]; self.visited_urls.clear(); self.visited_urls.add(url.split("#")[0])
        use_ai = "AI" in self.crawler_mode_combo.get()
        verbose = "Dettagliato" in self.crawler_verb_combo.get()
        
        self.log(f"--- START CRAWLER ({'AI' if use_ai else 'Smart'}) ---")
        
        while queue and self.is_running:
            curr, depth = queue.pop(0)
            self.status_var.set(f"Crawling: {curr}")
            
            try:
                res = requests.get(curr, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    for t in soup(['nav', 'footer', 'script', 'style']): t.decompose()
                    content = soup.body
                    if content:
                        fname = clean_filename(soup.title.string or "page") + ".md"
                        with open(get_unique_filepath(out, fname), "w", encoding="utf-8") as f:
                            f.write(f"# {curr}\n\n{md(str(content))}")
                        self.log(f"[OK] Salvato: {fname}")
                        
                        if depth < int(self.depth_spinbox.get()):
                            links = [{"text": a.get_text(strip=True)[:50], "href": urljoin(curr, a['href']).split("#")[0]} 
                                     for a in content.find_all('a', href=True)]
                            # Filtering Logic
                            valid_links = []
                            if use_ai:
                                if verbose: self.log(f"   ⬆️ AI Analisi {len(links)} link...")
                                prompt = self.cfg.get("prompt_web").replace("{context_url}", curr).replace("{links_text}", json.dumps(links[:80]))
                                provider = self.provider_combo.get()
                                key = self.key_entry.get()
                                model = self.model_combo.get()
                                
                                resp = self.ai.ask_ai(provider, key, model, prompt)
                                if resp:
                                    try:
                                        # Clean JSON
                                        if "```json" in resp: resp = resp.split("```json")[1].split("```")[0]
                                        selected = json.loads(resp)
                                        # Find matching objs
                                        for l in links:
                                            if l['href'] in selected or l['text'] in selected:
                                                valid_links.append(l)
                                            else:
                                                self.log_discard(f"[AI] Scartato: {l['text']}")
                                    except: self.log("Errore JSON AI")
                            else:
                                for l in links:
                                    score = heuristic_score(l['text'], l['href'], self.cfg.get("kw_web_good"), self.cfg.get("kw_web_bad"))
                                    if score > 0: valid_links.append(l)
                                    else: self.log_discard(f"[Smart] Scartato: {l['text']} (Score: {score})")
                            
                            # Enqueue
                            for l in valid_links:
                                if l['href'] not in self.visited_urls:
                                    # Domain check
                                    if self.restrict_var.get() and urlparse(l['href']).netloc != urlparse(url).netloc: continue
                                    self.visited_urls.add(l['href']); queue.append((l['href'], depth + 1))
                            
                            if use_ai: time.sleep(2)

            except Exception as e: self.log(f"Err: {e}")
        self.log("--- CRAWLER FINITO ---"); self.is_running = False

    # ================= PROCESS PDF =================
    def setup_pdf_tab(self):
        f = ttk.Frame(self.tab_pdf, padding=20); f.pack(fill="both", expand=True); f.columnconfigure(0, weight=1)
        input_frame = ttk.LabelFrame(f, text="Files PDF", padding=15); input_frame.grid(row=0, column=0, sticky="ew", pady=10); input_frame.columnconfigure(0, weight=1)
        self.pdf_listbox = tk.Listbox(input_frame, height=6); self.pdf_listbox.grid(row=0, column=0, sticky="ew", padx=5)
        btn_box = ttk.Frame(input_frame); btn_box.grid(row=1, column=0, sticky="w", pady=5)
        self.create_icon_button(btn_box, "➕", self.add_pdfs).pack(side="left")
        self.create_icon_button(btn_box, "🗑️", self.clear_pdfs).pack(side="left", padx=5)
        
        conf_frame = ttk.LabelFrame(f, text="Configurazione", padding=15); conf_frame.grid(row=1, column=0, sticky="ew", pady=10); conf_frame.columnconfigure(1, weight=1); conf_frame.columnconfigure(3, weight=1)
        ttk.Label(conf_frame, text="Metodo:").grid(row=0, column=0, sticky="w")
        self.pdf_mode_combo = ttk.Combobox(conf_frame, values=["Raw Text", "Smart Filter", "AI Engine"], state="readonly", width=20); self.pdf_mode_combo.grid(row=0, column=1, sticky="w", padx=10)
        ttk.Label(conf_frame, text="Log:").grid(row=0, column=2, sticky="e")
        self.pdf_verb_combo = ttk.Combobox(conf_frame, values=["Normale", "Dettagliato"], state="readonly", width=15); self.pdf_verb_combo.grid(row=0, column=3, sticky="w", padx=10)
        
        out_frame = ttk.LabelFrame(f, text="Output", padding=15); out_frame.grid(row=2, column=0, sticky="ew", pady=10); out_frame.columnconfigure(0, weight=1)
        self.pdf_path_var = tk.StringVar(value=os.path.join(os.getcwd(), "docs_pdf")); ttk.Entry(out_frame, textvariable=self.pdf_path_var).grid(row=0, column=0, sticky="ew")
        self.create_icon_button(out_frame, "📂", lambda: self.choose_directory(self.pdf_path_var)).grid(row=0, column=1, padx=10)
        
        act_frame = ttk.Frame(f, padding=10); act_frame.grid(row=3, column=0, sticky="ew", pady=10); act_frame.columnconfigure(0, weight=1); act_frame.columnconfigure(1, weight=1)
        tk.Button(act_frame, text="▶️  CONVERTI", font=("Segoe UI", 11), height=2, command=self.start_pdf).grid(row=0, column=0, sticky="ew", padx=10)
        tk.Button(act_frame, text="⏹️  STOP", font=("Segoe UI", 11), height=2, command=self.stop_process).grid(row=0, column=1, sticky="ew", padx=10)

    def start_pdf(self):
        self.save_all_config(); self.is_running = True
        threading.Thread(target=self.run_pdf, daemon=True).start()

    def run_pdf(self):
        out = self.pdf_path_var.get(); 
        if not os.path.exists(out): os.makedirs(out, exist_ok=True)
        mode = self.pdf_mode_combo.get(); use_ai = "AI" in mode
        verbose = "Dettagliato" in self.pdf_verb_combo.get()
        
        for path in self.pdf_files_to_convert:
            if not self.is_running: break
            name = os.path.basename(path); self.log(f"--- PDF: {name} ({mode}) ---")
            try:
                doc = fitz.open(path)
                with open(get_unique_filepath(out, name+".md"), "w", encoding="utf-8") as f:
                    f.write(f"# {name}\n\n")
                    for i, page in enumerate(doc):
                        if not self.is_running: break
                        raw = page.get_text()
                        write = True; final = raw
                        
                        if "Smart" in mode:
                            score = heuristic_score(raw, "", self.cfg.get("kw_pdf_good"), self.cfg.get("kw_pdf_bad"))
                            if score < 0: write=False; self.log_discard(f"Pagina {i+1} scartata")
                        elif use_ai:
                            if verbose: self.log(f"   🤖 AI Pag {i+1}...")
                            prompt = self.cfg.get("prompt_pdf").replace("{page_num}", str(i+1)).replace("{raw_text}", raw)
                            resp = self.ai.ask_ai(self.provider_combo.get(), self.key_entry.get(), self.model_combo.get(), prompt)
                            if resp: final = resp
                            else: self.log_discard(f"AI fallita pag {i+1}, uso raw")
                            time.sleep(3)
                        
                        if write: f.write(f"\n\n## Pagina {i+1}\n{final}")
                self.log(f"[OK] Creato: {name}.md")
            except Exception as e: self.log(f"Err: {e}")
        self.is_running = False

    # ================= EDITOR POPUPS =================
    def open_list_editor(self, mode):
        t = tk.Toplevel(self.root); t.title(f"Editor Keywords ({mode})"); t.geometry("600x500")
        k_good = "kw_web_good" if mode == "web" else "kw_pdf_good"
        k_bad = "kw_web_bad" if mode == "web" else "kw_pdf_bad"
        
        ttk.Label(t, text="Parole UTILI (+):").pack(anchor="w", padx=10)
        txt1 = tk.Text(t, height=8); txt1.pack(padx=10); txt1.insert("1.0", ", ".join(self.cfg.get(k_good)))
        ttk.Label(t, text="Parole SPAM (-):").pack(anchor="w", padx=10)
        txt2 = tk.Text(t, height=8); txt2.pack(padx=10); txt2.insert("1.0", ", ".join(self.cfg.get(k_bad)))
        
        def save():
            self.cfg.set(k_good, [x.strip() for x in txt1.get("1.0", "end").split(",") if x.strip()])
            self.cfg.set(k_bad, [x.strip() for x in txt2.get("1.0", "end").split(",") if x.strip()])
            self.cfg.save(); t.destroy()
        tk.Button(t, text="Salva", command=save).pack(pady=10)

    def open_prompt_editor(self, mode):
        t = tk.Toplevel(self.root); t.title(f"Editor Prompt ({mode})"); t.geometry("700x600")
        key = "prompt_web" if mode == "web" else "prompt_pdf"
        txt = tk.Text(t, height=20); txt.pack(padx=10, pady=10); txt.insert("1.0", self.cfg.get(key))
        def save():
            self.cfg.set(key, txt.get("1.0", "end").strip()); self.cfg.save(); t.destroy()
        tk.Button(t, text="Salva", command=save).pack(pady=10)

    def choose_directory(self, v): d = filedialog.askdirectory(); 
    def add_pdfs(self):
        fs = filedialog.askopenfilenames(filetypes=[("PDF", "*.pdf")])
        self.pdf_files_to_convert.extend(fs)
        for f in fs: self.pdf_listbox.insert("end", os.path.basename(f))
    def clear_pdfs(self): self.pdf_files_to_convert = []; self.pdf_listbox.delete(0, "end")
    def stop_process(self): self.is_running = False; self.log("!!! STOP RICHIESTO !!!")

# ================= 5. src/main.py =================
# Basta importare ed eseguire
from app_ui import UniversalConverterApp
if __name__ == "__main__":
    root = tk.Tk()
    # Tema opzionale per renderlo più bello su Windows
    try:
        root.tk.call("source", "azure.tcl") # Se hai un tema
        root.tk.call("set_theme", "light")
    except: pass
    
    style = ttk.Style()
    style.theme_use('clam') 
    app = UniversalConverterApp(root)
    root.mainloop()