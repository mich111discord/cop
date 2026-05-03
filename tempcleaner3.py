import tkinter as tk
from tkinter import messagebox, scrolledtext
import requests
import os
import threading

# KONFIGURACJA DOWÓDCY
API_KEY = 'cfa1a1adba210b47280d690f16545801313467cf8fe20ed5' # Twój Auth Key z obraz_4.png
TARGET_DIR = './ObiadDlaMisia'
URL = "https://mb-api.abuse.ch/api/v1/"

class BazaarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Labubu Control Panel - Misiu & Arcabit 🥰")
        self.root.geometry("650x450")
        self.root.configure(bg="#1a1a1a")

        # Nagłówek
        self.label = tk.Label(root, text="LABUBU: OPERACJA BAZAREK 🐻🥃", 
                              fg="#ff4757", bg="#1a1a1a", font=("Segoe UI", 16, "bold"))
        self.label.pack(pady=15)

        # Przycisk
        self.start_btn = tk.Button(root, text="POBIERZ 100 SZCZURKÓW! 🔥", 
                                   command=self.start_download, bg="#2ed573", fg="white", 
                                   font=("Segoe UI", 12, "bold"), relief="flat", padx=20, pady=10)
        self.start_btn.pack(pady=10)

        # Logi
        self.log_area = scrolledtext.ScrolledText(root, width=75, height=18, 
                                                 bg="#2f3542", fg="#ffffff", font=("Consolas", 10))
        self.log_area.pack(pady=10, padx=10)

    def log(self, message):
        self.log_area.insert(tk.END, f"{message}\n")
        self.log_area.see(tk.END)

    def download_logic(self):
        if not os.path.exists(TARGET_DIR):
            os.makedirs(TARGET_DIR)
            self.log("📁 Utworzono folder na Partycji Potępionych.")

        self.log("📡 Nawiązywanie kontaktu z Bazarkiem...")
        
        try:
            # 1. Pobieranie listy 100 ostatnich malwarów
            data = {'query': 'get_recent', 'selector': '100'}
            response = requests.post(URL, data=data, timeout=10)
            samples = response.json().get('data', [])

            if not samples:
                self.log("❌ Misiu: Pusto na Bazarku! Albo klucz zły, albo brak internetu.")
                return

            self.log(f"🐻 Misiu: Znaleziono {len(samples)} próbek! Zaczynamy rzeźnię...")

            # 2. Pobieranie plików w pętli
            for i, sample in enumerate(samples):
                sha256 = sample['sha256_hash']
                self.log(f"[{i+1}/100] Pobieram: {sha256[:20]}...")
                
                file_data = {'query': 'get_file', 'sha256_hash': sha256}
                file_res = requests.post(URL, data=file_data, headers={'API-KEY': API_KEY}, timeout=15)
                
                with open(f"{TARGET_DIR}/{sha256}.zip", 'wb') as f:
                    f.write(file_res.content)
            
            self.log("✅ MISJA ZAKOŃCZONA! 100 szczurków czeka na analizę. 🥰")
            messagebox.showinfo("Sukces", "Misiu Zbysiu przyniósł zakupy!")
            
        except Exception as e:
            self.log(f"❌ KATASTROFA: {str(e)}")
            messagebox.showerror("Błąd", f"Misiu się potknął: {str(e)}")

    def start_download(self):
        # Osobny wątek, żeby GUI nie zamarzało przy pobieraniu
        thread = threading.Thread(target=self.download_logic)
        thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = BazaarApp(root)
    root.mainloop()
