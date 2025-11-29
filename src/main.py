import tkinter as tk
from tkinter import ttk
from app_ui import UniversalConverterApp  

if __name__ == "__main__":
    root = tk.Tk()
    
    # Configurazione base dello stile
    style = ttk.Style()
    style.theme_use('clam') 
    
    # Avvio App
    app = UniversalConverterApp(root)
    root.mainloop()