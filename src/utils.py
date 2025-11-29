import re
import os

def clean_filename(title):
    # Rimuove versioni tipo v5.5.1 e caratteri illegali
    title = re.sub(r'v\d+[\._]\d+', '', title) 
    clean = re.sub(r'[^a-zA-Z0-9]+', '_', title)
    clean = re.sub(r'_+', '_', clean).strip('_')
    if not clean: clean = "doc_page"
    return clean[:80]

def get_unique_filepath(folder, filename):
    base_name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(folder, new_filename)):
        new_filename = f"{base_name}_{counter}{ext}"
        counter += 1
    return os.path.join(folder, new_filename)

def heuristic_score(text, href, good_list, bad_list):
    """Calcola il punteggio basato sulle keyword"""
    score = 0
    text_lower = text.lower()
    href_lower = href.lower() if href else ""
    
    for w in good_list: 
        if w.lower() in text_lower: score += 10
        if href_lower and w.lower() in href_lower: score += 5
        
    for w in bad_list: 
        if w.lower() in text_lower: score -= 50
        if href_lower and w.lower() in href_lower: score -= 20
        
    return score