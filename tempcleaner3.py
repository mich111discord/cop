import sys, os, subprocess, ctypes, json, urllib.request
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, \
    QTreeWidget, QTreeWidgetItem, QLabel, QPushButton, QLineEdit, QMessageBox, QMenuBar, QTextEdit
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt
import winreg

APP_NAME = "Ineo WinDebload Pro"
VERSION = "1.0.0"

# ------------------------- Admin -------------------------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def ensure_admin():
    if not is_admin():
        params = " ".join([f'"{arg}"' for arg in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(None,"runas",sys.executable,params,None,1)
        sys.exit(0)

# ------------------------- Apps -------------------------
def _regval(sk,name):
    try: return winreg.QueryValueEx(sk,name)[0]
    except: return None

def enum_uninstall_keys():
    roots = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", winreg.KEY_READ | winreg.KEY_WOW64_64KEY),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", winreg.KEY_READ | winreg.KEY_WOW64_32KEY),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", winreg.KEY_READ)
    ]
    apps=[]
    for root,subkey,access in roots:
        try:
            with winreg.OpenKey(root,subkey,0,access) as hk:
                for i in range(winreg.QueryInfoKey(hk)[0]):
                    try:
                        sk_name = winreg.EnumKey(hk,i)
                        with winreg.OpenKey(hk,sk_name) as sk:
                            name=_regval(sk,"DisplayName")
                            if not name: continue
                            uninstall=_regval(sk,"UninstallString")
                            apps.append({"type":"win32","name":name,"uninstall":uninstall})
                    except: continue
        except: continue
    return apps

def enum_appx_packages():
    try:
        ps = "Get-AppxPackage | Select Name,PackageFullName | ConvertTo-Json -Depth 2"
        c = subprocess.run(["powershell","-NoProfile","-Command",ps],capture_output=True,text=True,timeout=20)
        data=json.loads(c.stdout.strip())
        items = data if isinstance(data,list) else [data]
        res=[]
        for p in items:
            name=p.get("Name")
            pkg=p.get("PackageFullName")
            if name and pkg: res.append({"type":"appx","name":name,"package":pkg})
        return res
    except: return []

# ------------------------- Uninstall -------------------------
def uninstall_win32(cmd):
    try:
        if cmd:
            subprocess.Popen(cmd,shell=True)
            return True,"Uruchomiono deinstalator."
        else:
            return False,"Brak ścieżki do deinstalatora."
    except Exception as e:
        return False,str(e)

def uninstall_appx(pkg):
    try:
        cmd = f'Remove-AppxPackage -Package "{pkg}"'
        res = subprocess.run(["powershell","-NoProfile","-Command",cmd],capture_output=True,text=True,timeout=60)
        if res.returncode==0: return True,"Usunięto pakiet."
        return False,res.stderr or res.stdout
    except Exception as e:
        return False,str(e)

# ------------------------- Updater -------------------------
def check_update():
    try:
        url_version = "https://raw.githubusercontent.com/mich111discord/updaterapps/main/debloaderver.txt"
        url_updater = "https://raw.githubusercontent.com/mich111discord/updaterapps/main/debloaderupd.txt"
        latest_version = urllib.request.urlopen(url_version).read().decode().strip()
        updater_link = urllib.request.urlopen(url_updater).read().decode().strip()

        if not updater_link:
            return False, "Brak linku do aktualizatora (plik debloaderupd.txt jest pusty)."

        if latest_version != VERSION:
            folder = os.path.join(os.getcwd(),"upd")
            os.makedirs(folder, exist_ok=True)
            file_path = os.path.join(folder, os.path.basename(updater_link))
            urllib.request.urlretrieve(updater_link, file_path)
            return True, f"Pobrano nowy updater: {file_path}"
        return False, "Program jest aktualny."
    except Exception as e:
        return False, f"Błąd aktualizacji: {str(e)}"

# ------------------------- Main Window -------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1000,600)

        # --- Menu ---
        menubar = QMenuBar(self)
        # Plik
        file_menu = menubar.addMenu("Plik")
        exit_action = QAction("Zamknij", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Ustawienia
        settings_menu = menubar.addMenu("Ustawienia")
        settings_action = QAction("Opcje", self)
        settings_action.triggered.connect(self.show_settings)
        settings_menu.addAction(settings_action)

        # Dezinstalator
        uninstall_menu = menubar.addMenu("Dezinstalator")
        uninstall_action = QAction("Lista aplikacji", self)
        uninstall_action.triggered.connect(self.show_uninstall)
        uninstall_menu.addAction(uninstall_action)

        # Logi
        log_menu = menubar.addMenu("Logi")
        log_action = QAction("Pokaż logi", self)
        log_action.triggered.connect(self.show_logs)
        log_menu.addAction(log_action)

        # Pomoc
        help_menu = menubar.addMenu("Pomoc")
        about_action = QAction("O programie", self)
        about_action.triggered.connect(lambda: QMessageBox.information(self,"O programie",f"{APP_NAME} v{VERSION}"))
        help_menu.addAction(about_action)

        self.setMenuBar(menubar)

        # Central widget i layout
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.main_layout = QVBoxLayout(self.central)

        # Widgets dla każdej sekcji (ukryte na start)
        self.widget_uninstall = QWidget()
        self.widget_settings = QWidget()
        self.widget_logs = QWidget()

        self.init_uninstall_widget()
        self.init_settings_widget()
        self.init_logs_widget()

        # Domyślnie pokaż dezinstalator
        self.show_uninstall()

    # --- Dezinstalator ---
    def init_uninstall_widget(self):
        layout = QVBoxLayout(self.widget_uninstall)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Szukaj aplikacji...")
        self.search_box.textChanged.connect(self.filter_list)
        layout.addWidget(self.search_box)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Aplikacja"])
        layout.addWidget(self.tree)

        btn_layout = QHBoxLayout()
        btn_reload = QPushButton("Odśwież listę")
        btn_reload.clicked.connect(self.reload_list)
        btn_toggle = QPushButton("Zaznacz/odznacz wszystkie")
        btn_toggle.clicked.connect(self.toggle_all)
        btn_un = QPushButton("Odinstaluj wybrane")
        btn_un.clicked.connect(self.uninstall_selected)
        btn_update = QPushButton("Sprawdź aktualizacje")
        btn_update.clicked.connect(self.do_update)

        btn_un.setStyleSheet("background:#FFD700;color:black;font-weight:bold;")

        btn_layout.addWidget(btn_reload)
        btn_layout.addWidget(btn_toggle)
        btn_layout.addWidget(btn_un)
        btn_layout.addWidget(btn_update)
        layout.addLayout(btn_layout)

        self.detail = QLabel("Wybierz aplikację po lewej.")
        self.detail.setWordWrap(True)
        layout.addWidget(self.detail)

        self.log = QLabel("")
        self.log.setWordWrap(True)
        layout.addWidget(self.log)

    # --- Ustawienia ---
    def init_settings_widget(self):
        layout = QVBoxLayout(self.widget_settings)
        lbl = QLabel("Tutaj będą ustawienia programu.")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)

    # --- Logi ---
    def init_logs_widget(self):
        layout = QVBoxLayout(self.widget_logs)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

    # --- Pokaż sekcje ---
    def show_uninstall(self):
        self.clear_main_layout()
        self.main_layout.addWidget(self.widget_uninstall)
        self.reload_list()

    def show_settings(self):
        self.clear_main_layout()
        self.main_layout.addWidget(self.widget_settings)

    def show_logs(self):
        self.clear_main_layout()
        self.main_layout.addWidget(self.widget_logs)

    def clear_main_layout(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def reload_list(self):
        self.tree.clear()
        self.apps = enum_uninstall_keys() + enum_appx_packages()
        for app in self.apps:
            item = QTreeWidgetItem([app["name"]])
            item.setCheckState(0, Qt.CheckState.Unchecked)
            self.tree.addTopLevelItem(item)

    def filter_list(self, text):
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            item.setHidden(text.lower() not in item.text(0).lower())

    def toggle_all(self):
        checked = any(self.tree.topLevelItem(i).checkState(0) == Qt.CheckState.Unchecked
                      for i in range(self.tree.topLevelItemCount()))
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            item.setCheckState(0, Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)

    def uninstall_selected(self):
        selected = []
        for i, app in enumerate(self.apps):
            item = self.tree.topLevelItem(i)
            if item.checkState(0) == Qt.CheckState.Checked:
                selected.append(app)

        if not selected:
            QMessageBox.information(self, "Info", "Nie wybrano żadnej aplikacji.")
            return

        reply = QMessageBox.question(self, "Potwierdzenie",
                                     f"Czy na pewno chcesz odinstalować {len(selected)} aplikacji?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return

        for app in selected:
            if app["type"] == "win32":
                success, msg = uninstall_win32(app.get("uninstall"))
            elif app["type"] == "appx":
                success, msg = uninstall_appx(app.get("package"))
            else:
                success, msg = False, "Nieznany typ aplikacji."

            self.log.setText(f"{app['name']}: {msg}")

    def do_update(self):
        success, msg = check_update()
        QMessageBox.information(self, "Aktualizacja", msg)

# ------------------------- Main -------------------------
if __name__ == "__main__":
    ensure_admin()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
