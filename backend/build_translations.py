import os
import json
import time
from deep_translator import GoogleTranslator

def build_cache():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    exercises_dir = os.path.join(parent_dir, "cwiczenia", "exercises")
    
    texts_to_translate = set()
    
    print("Zbieranie unikalnych tekstów do przetłumaczenia...")
    for filename in os.listdir(exercises_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(exercises_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                texts_to_translate.add(data.get("name", ""))
                instructions = data.get("instructions", [])
                for instr in instructions[:3]:
                    texts_to_translate.add(instr)
                    
    # Dodaj gify z gif_data.py
    from gif_data import GIF_EXERCISES
    for item in GIF_EXERCISES:
        texts_to_translate.add(item.get("name", ""))
        for instr in item.get("instructions", [])[:3]:
            texts_to_translate.add(instr)
            
    # Filtruj puste
    texts_to_translate = [t for t in texts_to_translate if t and len(t) > 2]
    
    print(f"Znaleziono {len(texts_to_translate)} unikalnych tekstów.")
    
    cache_path = os.path.join(current_dir, "translation_cache.json")
    
    # Załaduj istniejący cache żeby nie tłumaczyć drugi raz tego samego
    cache = {}
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache = json.load(f)
            
    texts_to_translate = [t for t in texts_to_translate if t not in cache]
    print(f"Do przetłumaczenia pozostało: {len(texts_to_translate)}")
    
    if not texts_to_translate:
        return
        
    translator = GoogleTranslator(source='en', target='pl')
    
    BATCH_SIZE = 4000 # Znaków
    current_batch = []
    current_len = 0
    
    print("Rozpoczynam tłumaczenie w tle...")
    for idx, text in enumerate(texts_to_translate):
        text_len = len(text)
        if current_len + text_len + 3 > BATCH_SIZE and current_batch:
            # Tłumacz paczkę
            batch_text = " ||| ".join(current_batch)
            try:
                translated_batch = translator.translate(batch_text)
                translated_items = translated_batch.split(" ||| ")
                for i, orig in enumerate(current_batch):
                    if i < len(translated_items):
                        cache[orig] = translated_items[i].strip()
            except Exception as e:
                print(f"Błąd tłumaczenia: {e}")
                time.sleep(2)
            
            # Zapisz częściowy progres
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
                
            current_batch = []
            current_len = 0
            time.sleep(0.5) # Ograniczenie API
            
        current_batch.append(text)
        current_len += text_len + 5
        
    # Ostatnia paczka
    if current_batch:
        batch_text = " ||| ".join(current_batch)
        try:
            translated_batch = translator.translate(batch_text)
            translated_items = translated_batch.split(" ||| ")
            for i, orig in enumerate(current_batch):
                if i < len(translated_items):
                    cache[orig] = translated_items[i].strip()
        except Exception as e:
            print(f"Błąd tłumaczenia: {e}")
            
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
        
    print("Tłumaczenie zakończone i zapisane do cache!")

if __name__ == "__main__":
    build_cache()