import os
import sys
import shutil
import ctypes
import subprocess
import requests
import json

try:
    import winreg
except ImportError:
    import _winreg as winreg

from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QMessageBox,
    QVBoxLayout, QHBoxLayout, QCheckBox, QListWidget, QStackedWidget
)
from PySide6.QtCore import Qt

# Wersja i linki
LOCAL_VERSION = "6.0"
VERSION_URL = "https://raw.githubusercontent.com/mich111discord/updaterapps/main/updver.txt"
UPDATER_LINK_FILE_URL = "https://raw.githubusercontent.com/mich111discord/updaterapps/main/updlink.txt"
PRODUCT_URL = "https://wbb2fo.webwave.dev/software/tempcleaner/pl"
SETTINGS_FILE = "temp_cleaner_settings.json"
default_settings = {"auto_clean": False}

# Globalne zmienne
settings = default_settings

def is_admin():
    """Sprawdź czy aplikacja ma uprawnienia administratora"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def request_admin():
    """Poproś o uprawnienia administratora"""
    try:
        if not is_admin():
            script = os.path.abspath(sys.argv[0])
            params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]] + ['--elevated'])
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, f'"{script}" {params}', None, 1
            )
            return False
        return True
    except Exception as e:
        print(f"Błąd uprawnień: {e}")
        return True  # Kontynuuj bez uprawnień admin

def load_settings():
    """Wczytaj ustawienia z pliku"""
    global settings
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding='utf-8') as f:
                settings = json.load(f)
        else:
            settings = default_settings.copy()
    except Exception as e:
        print(f"Błąd wczytywania ustawień: {e}")
        settings = default_settings.copy()

def save_settings():
    """Zapisz ustawienia do pliku"""
    try:
        with open(SETTINGS_FILE, "w", encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Błąd zapisywania ustawień: {e}")
        return False

def safe_remove_file(file_path):
    """Bezpieczne usuwanie pliku"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except:
        pass
    return False

def safe_remove_dir(dir_path):
    """Bezpieczne usuwanie katalogu"""
    try:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path, ignore_errors=True)
            return True
    except:
        pass
    return False

def clean_folder(folder_path):
    """Wyczyść folder"""
    if not os.path.exists(folder_path):
        QMessageBox.information(None, "TempCleaner", f"Folder {folder_path} nie istnieje.")
        return
    
    deleted_count = 0
    
    try:
        items = os.listdir(folder_path)
        for item in items:
            item_path = os.path.join(folder_path, item)
            try:
                if os.path.isfile(item_path):
                    if safe_remove_file(item_path):
                        deleted_count += 1
                elif os.path.isdir(item_path):
                    if safe_remove_dir(item_path):
                        deleted_count += 1
            except:
                continue
        
        QMessageBox.information(None, "TempCleaner", 
            f"Usunięto {deleted_count} elementów z folderu.")
            
    except Exception as e:
        QMessageBox.critical(None, "Błąd", f"Nie można wyczyścić folderu: {str(e)}")

def clean_junk_files():
    """Usuń pliki śmieciowe"""
    extensions = [".tmp", ".log", ".bak", ".old"]
    base_paths = [
        os.path.expanduser("~\\AppData\\Local\\Temp"),
        "C:\\Windows\\Temp"
    ]
    
    deleted = 0
    
    for base_path in base_paths:
        if not os.path.exists(base_path):
            continue
            
        try:
            for item in os.listdir(base_path):
                item_path = os.path.join(base_path, item)
                if os.path.isfile(item_path):
                    for ext in extensions:
                        if item.lower().endswith(ext):
                            if safe_remove_file(item_path):
                                deleted += 1
                            break
        except:
            continue
    
    QMessageBox.information(None, "Niepotrzebne pliki", f"Usunięto {deleted} plików.")

def clean_registry_safe():
    """Bezpieczne czyszczenie rejestru - tylko puste klucze"""
    try:
        deleted = 0
        key_path = r"SOFTWARE"
        
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as main_key:
            subkeys = []
            i = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(main_key, i)
                    subkeys.append(subkey_name)
                    i += 1
                except OSError:
                    break
        
        # Sprawdź i usuń puste klucze
        for subkey_name in subkeys:
            try:
                subkey_path = f"{key_path}\\{subkey_name}"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, subkey_path, 0, winreg.KEY_READ) as subkey:
                    info = winreg.QueryInfoKey(subkey)
                    if info[0] == 0 and info[1] == 0:  # Brak podkluczy i wartości
                        try:
                            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, subkey_path)
                            deleted += 1
                        except:
                            pass
            except:
                continue
        
        QMessageBox.information(None, "Rejestr", f"Usunięto {deleted} pustych kluczy.")
        
    except Exception as e:
        QMessageBox.critical(None, "Błąd", f"Błąd czyszczenia rejestru: {str(e)}")

def check_for_update():
    """Sprawdź dostępność aktualizacji"""
    try:
        response = requests.get(VERSION_URL, timeout=10)
        response.raise_for_status()
        latest_version = response.text.strip()
        
        # Sprawdź czy wersje się różnią (bez porównywania która większa)
        if latest_version != LOCAL_VERSION:
            reply = QMessageBox.question(None, "Aktualizacja dostępna", 
                f"Dostępna wersja: {latest_version}\nTwoja wersja: {LOCAL_VERSION}\n\nWersje się różnią. Czy chcesz pobrać aktualizację?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                download_updater()
        else:
            QMessageBox.information(None, "Aktualizacja", "Masz najnowszą wersję!")
            
    except Exception as e:
        QMessageBox.critical(None, "Błąd", f"Nie można sprawdzić aktualizacji: {str(e)}")

def download_updater():
    """Pobierz i uruchom aktualizator"""
    try:
        # Pobierz link do aktualizatora
        QMessageBox.information(None, "Pobieranie", "Pobieranie linku do aktualizatora...")
        
        response = requests.get(UPDATER_LINK_FILE_URL, timeout=10)
        response.raise_for_status()
        updater_url = response.text.strip()
        
        if not updater_url.startswith("https://"):
            QMessageBox.critical(None, "Błąd", "Nieprawidłowy link do aktualizatora!")
            return
        
        # Stwórz folder upd jeśli nie istnieje
        upd_folder = "upd"
        if not os.path.exists(upd_folder):
            os.makedirs(upd_folder)
        
        updater_path = os.path.join(upd_folder, "updater.exe")
        
        # Pobierz aktualizator
        QMessageBox.information(None, "Pobieranie", "Pobieranie aktualizatora...")
        
        response = requests.get(updater_url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(updater_path, "wb") as file:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
        
        # Sprawdź czy plik został pobrany
        if os.path.exists(updater_path) and os.path.getsize(updater_path) > 0:
            QMessageBox.information(None, "Sukces", "Aktualizator został pobrany!\nUruchamianie...")
            
            # Uruchom aktualizator
            try:
                os.startfile(updater_path)
                # Zamknij aplikację po uruchomieniu aktualizatora
                sys.exit(0)
            except Exception as start_e:
                subprocess.Popen([updater_path])
                sys.exit(0)
        else:
            QMessageBox.critical(None, "Błąd", "Nie udało się pobrać aktualizatora!")
            
    except requests.exceptions.Timeout:
        QMessageBox.critical(None, "Błąd", "Przekroczono czas oczekiwania podczas pobierania!")
    except requests.exceptions.RequestException as e:
        QMessageBox.critical(None, "Błąd", f"Błąd połączenia: {str(e)}")
    except Exception as e:
        QMessageBox.critical(None, "Błąd", f"Nie udało się pobrać aktualizatora: {str(e)}")

class TempCleanerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("TempCleaner Pro — Ineo Edition")
        self.setFixedSize(600, 500)
        
        # Style - Żółty motyw
        self.setStyleSheet("""
            QWidget { 
                background-color: #fffbe6; 
                color: #333; 
                font-family: Arial, sans-serif; 
            }
            QPushButton { 
                background-color: #ffd700; 
                color: #000; 
                border: none; 
                padding: 10px; 
                font-weight: bold; 
                border-radius: 5px;
            }
            QPushButton:hover { 
                background-color: #ffec8b; 
            }
            QListWidget { 
                background-color: #fffacd; 
                border: 1px solid #ffd700;
                selection-background-color: #ffd700;
                selection-color: #000;
            }
            QLabel {
                color: #333;
            }
            QCheckBox {
                color: #333;
            }
        """)
        
        # Layout główny
        main_layout = QHBoxLayout()
        
        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.addItems([
            "Czyszczenie TEMP",
            "Czyszczenie PREFETCH", 
            "Pliki śmieciowe",
            "Rejestr (bezpieczny)",
            "Ustawienia",
            "Aktualizacje",
            "Informacje"
        ])
        self.sidebar.setFixedWidth(180)
        self.sidebar.currentRowChanged.connect(self.change_page)
        
        # Stack widget
        self.stack = QStackedWidget()
        
        # Tworzenie stron
        self.create_pages()
        
        # Layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)
        
        # Domyślna strona
        self.sidebar.setCurrentRow(0)
    
    def create_pages(self):
        """Tworzenie wszystkich stron"""
        
        # Strona TEMP
        temp_page = self.create_simple_page(
            "Czyszczenie folderu TEMP",
            "Usuń pliki TEMP",
            lambda: clean_folder(r"C:\Windows\Temp")
        )
        self.stack.addWidget(temp_page)
        
        # Strona PREFETCH
        prefetch_page = self.create_simple_page(
            "Czyszczenie folderu PREFETCH", 
            "Usuń pliki PREFETCH",
            lambda: clean_folder(r"C:\Windows\Prefetch")
        )
        self.stack.addWidget(prefetch_page)
        
        # Strona plików śmieciowych
        junk_page = self.create_simple_page(
            "Usuwanie plików śmieciowych",
            "Usuń pliki śmieciowe", 
            clean_junk_files
        )
        self.stack.addWidget(junk_page)
        
        # Strona rejestru
        registry_page = self.create_simple_page(
            "Bezpieczne czyszczenie rejestru",
            "Usuń puste klucze rejestru",
            clean_registry_safe
        )
        self.stack.addWidget(registry_page)
        
        # Strona ustawień
        settings_page = self.create_settings_page()
        self.stack.addWidget(settings_page)
        
        # Strona aktualizacji
        update_page = self.create_simple_page(
            "Sprawdzanie aktualizacji",
            "Sprawdź aktualizacje",
            check_for_update
        )
        self.stack.addWidget(update_page)
        
        # Strona informacji
        info_page = self.create_info_page()
        self.stack.addWidget(info_page)
    
    def create_simple_page(self, title, button_text, action):
        """Tworzenie prostej strony z przyciskiem"""
        page = QWidget()
        layout = QVBoxLayout()
        
        # Tytuł
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 20px;")
        layout.addWidget(title_label)
        
        # Przycisk
        button = QPushButton(button_text)
        button.clicked.connect(action)
        button.setFixedHeight(40)
        layout.addWidget(button)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def create_settings_page(self):
        """Tworzenie strony ustawień"""
        page = QWidget()
        layout = QVBoxLayout()
        
        title_label = QLabel("Ustawienia")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 20px;")
        layout.addWidget(title_label)
        
        # Checkbox auto-clean
        self.auto_clean_cb = QCheckBox("Automatyczne czyszczenie przy starcie")
        self.auto_clean_cb.setChecked(settings.get("auto_clean", False))
        layout.addWidget(self.auto_clean_cb)
        
        # Przycisk zapisu
        save_btn = QPushButton("Zapisz ustawienia")
        save_btn.clicked.connect(self.save_settings_action)
        save_btn.setFixedHeight(40)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def create_info_page(self):
        """Tworzenie strony informacji"""
        page = QWidget()
        layout = QVBoxLayout()
        
        info_text = f"""
        <h2>TempCleaner Pro — Ineo Edition</h2>
        <p><b>Wersja:</b> {LOCAL_VERSION}</p>
        <p><b>Opis:</b> Narzędzie do czyszczenia plików tymczasowych</p>
        <p><b>Strona:</b> <a href='{PRODUCT_URL}'>{PRODUCT_URL}</a></p>
        """
        
        info_label = QLabel(info_text)
        info_label.setOpenExternalLinks(True)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def change_page(self, index):
        """Zmiana aktywnej strony"""
        if 0 <= index < self.stack.count():
            self.stack.setCurrentIndex(index)
    
    def save_settings_action(self):
        """Akcja zapisu ustawień"""
        global settings
        settings["auto_clean"] = self.auto_clean_cb.isChecked()
        
        if save_settings():
            QMessageBox.information(self, "Ustawienia", "Ustawienia zostały zapisane!")
        else:
            QMessageBox.warning(self, "Błąd", "Nie udało się zapisać ustawień.")

def main():
    """Główna funkcja aplikacji"""
    
    # Sprawdzenie uprawnień (opcjonalne)
    if "--elevated" not in sys.argv:
        if not request_admin():
            sys.exit(0)
    
    # Wczytanie ustawień
    load_settings()
    
    # Auto-clean jeśli włączony
    if settings.get("auto_clean", False):
        try:
            # W tle, bez okienek
            if os.path.exists(r"C:\Windows\Temp"):
                for item in os.listdir(r"C:\Windows\Temp"):
                    safe_remove_file(os.path.join(r"C:\Windows\Temp", item))
        except:
            pass
    
    # Uruchomienie GUI
    app = QApplication(sys.argv)
    
    # Ustawienie ikony aplikacji (opcjonalne)
    app.setApplicationName("TempCleaner Pro")
    app.setApplicationVersion(LOCAL_VERSION)
    
    # Główne okno
    window = TempCleanerApp()
    window.show()
    
    # Uruchomienie pętli aplikacji
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
