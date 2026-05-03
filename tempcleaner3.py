import requests
import os
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading

# TWOJE DANE
API_KEY = 'cfa1a1adba210b47280d690f16545801313467cf8fe20ed5'
TARGET_DIR = './ObiadDlaMisia'

def pobierz_malware():
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
    
    log_area.insert(tk.END, "🐻 Misiu: Idę na zakupy na Bazarek...\n")
    btn_start.config(state=tk.DISABLED)
    
    try:
        url = "https://mb-api.abuse.ch/api/v1/"
        data = {'query': 'get_recent', 'selector': '100'}
        
        response = requests.post(url, data=data)
        samples = response.json().get('data', [])
        
        log_area.insert(tk.END, f"✅ Znalazłem {len(samples)} szczurków!\n")
        
        for i, sample in enumerate(samples):
            sha256 = sample['sha256_hash']
            log_area.insert(tk.END, f"[{i+1}/100] Pakuję: {sha256[:15]}...\n")
            log_area.see(tk.END)
            
            download_data = {'query': 'get_file', 'sha256_hash': sha256}
            file_res = requests.post(url, data=download_data, headers={'API-KEY': API_KEY})
            
            with open(f"{TARGET_DIR}/{sha256}.zip", 'wb') as f:
                f.write(file_res.content)
                
        log_area.insert(tk.END, "🔥 WSZYSTKO W KOTLE! Partycja Potępionych zaprasza! 🥰\n")
        messagebox.showinfo("Sukces", "Misiu Zbysiu przyniósł 100 prezentów!")
        
    except Exception as e:
        log_area.insert(tk.END, f"❌ BŁĄD: {str(e)}\n")
        messagebox.showerror("Foch Misia", f"CośJasne, Dowódco! Skoro robimy Labubu na pełnym wypasie, to niech Misiu Zbysiu ma swój własny panel kontrolny z przyciskami! 👁️👄👁️ GDI i okienka to jest to, co tygryski (i niedźwiedzie) lubią najbardziej.

Oto wersja skryptu z interfejsem **Tkinter**. Teraz będziesz mógł ściągać 100 szczurków jednym kliknięciem, patrząc jak pasek postępu zapełnia Partycję Potępionych!

### Skrypt: Misiu-Bazaar-Downloader.py 🐻💻

Ten skrypt nie wymaga instalowania dodatkowych rzeczy poza `requests`, bo `tkinter` jest już wbudowany w Pythona.
```python
import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
import os
import threading

# KONFIGURACJA
API_KEY = 'cfa1a1adba210b47280d690f16545801313467cf8fe20ed5'
TARGET_DIR = './ObiadDlaMisia'
URL = "[https://mb-api.abuse.ch/api/v1/](https://mb-api.abuse.ch/api/v1/)"

class BazaarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Misiu Zbysiu & Arcabit - Malware Downloader 🥰")
        self.root.geometry("600x400")
        self.root.configure(bg="#2c3e50")

        # Nagłówek
        self.label = tk.Label(root, text="Panel Dowódcy: Zakupy na Bazarku 🐻🥃", 
                              fg="white", bg="#2c3e50", font=("Arial", 14, "bold"))
        self.label.pack(pady=10)

        # Przycisk startu
        self.start_btn = tk.Button(root, text="POBIERZ 100 SZCZURKÓW NA OBIAD! 🔥", 
                                   command=self.start_download, bg="#e74c3c", fg="white", 
                                   font=("Arial", 10, "bold"), padx=20, pady=10)
        self.start_btn.pack(pady=5)

        # Pole tekstowe (Logi)
        self.log_area = scrolledtext.ScrolledText(root, width=70, height=15, bg="#34495e", fg="#ecf0f1")
        self.log_area.pack(pady=10, padx=10)

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def download_logic(self):
        if not os.path.exists(TARGET_DIR):
            os.makedirs(TARGET_DIR)
            self.log(f"📁 Utworzono folder: {TARGET_DIR}")

        self.log("🚀 Łączenie z Bazarkiem...")
        
        try:
            # 1. Pobieranie listy
            data = {'query': 'get_recent', 'selector': '100'}
            response = requests.post(URL, data=data, timeout=10)
            samples = response.json().get('data', [])

            self.log(f"🐻 Misiu: Znalazłem {len(samples)} kąsków! Zaczynamy pakowanie...")

            # 2. Pobieranie plików
            for i, sample in enumerate(samples):
                sha256 = sample['sha256_hash']
                self.log(f"[{i+1}/100] Pobieram: {sha256[:15]}...")
                
                file_data = {'query': 'get_file', 'sha256_hash': sha256}
                file_res = requests.post(URL, data=file_data, headers={'API-KEY': API_KEY}, timeout=15)
                
                with open(f"{TARGET_DIR}/{sha256}.zip", 'wb') as f:
                    f.write(file_res.content)
            
            self.log("✅ GOTOWE! Misiu i Arcabit zapraszają na grillowanie! 🥰")
            messagebox.showinfo("Sukces", "100 szczurków wylądowało w folderze!")
            
        except Exception as e:
            self.log(f"❌ BŁĄD: {str(e)}")
            messagebox.showerror("Błąd", f"Misiu się potknął: {str(e)}")

    def start_download(self):
        # Odpalamy w osobnym wątku, żeby okno nie "zamarzło"
        thread = threading.Thread(target=self.download_logic)
        thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = BazaarApp(root)
    root.mainloop()
