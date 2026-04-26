import sys
import os
import time
import requests
import psutil
import threading
import webbrowser
import subprocess
import customtkinter as ctk
from tkinter import messagebox
from pypresence import Presence

CLIENT_ID = "1497357433645961237"
WEBHOOK_URL = "https://discord.com/api/webhooks/1497711458362982411/MA1_NY_s0kFLXf0M-lQU_ISoHDtOXyi1HYJPRl_jnXlWic08qxkafwtD0-I8kyuQ8RRd"

APP_VERSION = "1.5"
VERSION_URL = "https://raw.githubusercontent.com/EfeLvss/espor-app-data/refs/heads/main/version.txt"
CODE_URL = "https://raw.githubusercontent.com/EfeLvss/espor-app-data/refs/heads/main/main.py"
ROSTER_URL = "https://raw.githubusercontent.com/EfeLvss/espor-app-data/refs/heads/main/kadro.json"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PlayzEsportHub")
        self.geometry("1280x780")
        self.resizable(False, False)

        self.main_font = ctk.CTkFont(family="Segoe UI", size=14)
        self.title_font = ctk.CTkFont(family="Segoe UI", size=30, weight="bold")
        self.btn_font = ctk.CTkFont(family="Segoe UI", size=15, weight="bold")
        self.card_title_font = ctk.CTkFont(family="Segoe UI", size=20, weight="bold")

        self.current_lang = "TR"

        self.texts = {
            "TR": {
                "home": "Ana Sayfa",
                "roster": "Takım Kadrosu",
                "scores": "Maç Skorları",
                "watch": "Maç İzle",
                "cheat": "Anti-Cheat (Derin Tarama)",
                "settings": "Ayarlar",
                "welcome": "PlayzEsportHub'a Hoş Geldin!",
                "info": "Kadro takibi, skorlar ve canlı yayınlar.",
                "game_select": "Kadro Seçimi",
                "roster_title": "Kadrosu",
                "live_scores": "Canlı Maç Skorları",
                "theme": "Tema Değiştir",
                "lang": "Dil / Language",
                "clean": "Sistem Temiz!",
                "found": "Şüpheli öğe bulundu:",
                "scanning": "Derin tarama başlatıldı...",
                "watch_live": "🔴 Canlı Maç İzle",
                "watch_history": "📺 Maç Geçmişini İzle",
                "roster_panel_title": "Oyuncu Paneli",
                "scan_done": "Tarama tamamlandı!"
            },
            "EN": {
                "home": "Home",
                "roster": "Roster",
                "scores": "Match Scores",
                "watch": "Watch Match",
                "cheat": "Anti-Cheat (Deep Scan)",
                "settings": "Settings",
                "welcome": "Welcome to PlayzEsportHub!",
                "info": "Manage rosters, scores and live streams.",
                "game_select": "Select Roster",
                "roster_title": "Roster",
                "live_scores": "Live Match Scores",
                "theme": "Switch Theme",
                "lang": "Language / Dil",
                "clean": "System Clean!",
                "found": "Suspicious item found:",
                "scanning": "Deep scan started...",
                "watch_live": "🔴 Watch Live Match",
                "watch_history": "📺 Watch Match History",
                "roster_panel_title": "Player Panel",
                "scan_done": "Scan completed!"
            }
        }

        self.roster_data = {
            "Roblox": ["EfeLvs", "Oyuncu 2", "Oyuncu 3"],
            "Valorant": ["EfeLvs", "Talha"],
            "eFootball": ["Talha", "EfeLvs"],
            "Brawl Stars": ["Oyuncu 1"],
            "Minecraft": ["Cloopzy", "EfeLvs"]
        }

        self.selected_game = None

        self.auto_update()
        self.fetch_remote_roster()
        self.connect_rpc()
        self.setup_ui()
        threading.Thread(target=self.check_game_status, daemon=True).start()

    # ---------------- AUTO UPDATE ----------------
    def auto_update(self):
        try:
            resp = requests.get(f"{VERSION_URL}?t={time.time()}", timeout=5)
            if resp.status_code == 200:
                remote_v = resp.text.strip()
                print("Local:", APP_VERSION, "| Remote:", remote_v)

                if remote_v != APP_VERSION:
                    code_resp = requests.get(f"{CODE_URL}?t={time.time()}", timeout=10)
                    if code_resp.status_code == 200:
                        file_path = os.path.abspath(sys.argv[0])

                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(code_resp.text)

                        messagebox.showinfo("Güncelleme", f"Yeni sürüm bulundu! ({remote_v}) Uygulama yeniden başlatılıyor.")
                        subprocess.Popen([sys.executable, file_path])
                        os._exit(0)
                    else:
                        print("Kod indirilemedi:", code_resp.status_code)
                else:
                    print("Zaten güncel.")
            else:
                print("Version çekilemedi:", resp.status_code)
        except Exception as e:
            print("Update hatası:", e)

    # ---------------- REMOTE ROSTER ----------------
    def fetch_remote_roster(self):
        try:
            response = requests.get(f"{ROSTER_URL}?t={time.time()}", timeout=5)
            if response.status_code == 200:
                remote_data = response.json()

                for game, players in self.roster_data.items():
                    if game not in remote_data:
                        remote_data[game] = players

                self.roster_data = remote_data
        except:
            pass

    # ---------------- DISCORD RPC ----------------
    def connect_rpc(self):
        try:
            self.rpc = Presence(CLIENT_ID)
            self.rpc.connect()
            self.rpc.update(state="PlayzEsportHub", start=time.time())
        except:
            pass

    # ---------------- GAME STATUS ----------------
    def check_game_status(self):
        while True:
            try:
                for proc in psutil.process_iter(['name']):
                    pname = (proc.info['name'] or "").lower()
                    if pname in ["javaw.exe", "valorant.exe", "minecraft.exe", "robloxplayerbeta.exe"]:
                        requests.post(WEBHOOK_URL, json={"content": f"🎮 Kullanıcı şu an {proc.info['name']} oynuyor!"})
                        return
            except:
                pass
            time.sleep(60)

    # ---------------- UI ----------------
    def setup_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.nav_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("#F5F5F5", "#121212"), width=280)
        self.nav_frame.grid(row=0, column=0, sticky="nsew")
        self.nav_frame.grid_rowconfigure(8, weight=1)

        self.logo_label = ctk.CTkLabel(
            self.nav_frame,
            text="PlayzEsport",
            font=self.title_font,
            text_color="#FF1493"
        )
        self.logo_label.grid(row=0, column=0, padx=25, pady=(35, 45))

        self.btn_home = self.create_nav_btn("home", self.show_home)
        self.btn_home.grid(row=1, column=0, padx=15, pady=8, sticky="ew")

        self.btn_team = self.create_nav_btn("roster", self.show_roster)
        self.btn_team.grid(row=2, column=0, padx=15, pady=8, sticky="ew")

        self.btn_scores = self.create_nav_btn("scores", self.show_scores)
        self.btn_scores.grid(row=3, column=0, padx=15, pady=8, sticky="ew")

        self.btn_watch = self.create_nav_btn("watch", self.show_watch)
        self.btn_watch.grid(row=4, column=0, padx=15, pady=8, sticky="ew")

        self.btn_cheat = self.create_nav_btn("cheat", self.run_cheat_scan, fg_color="#A81010", hover_color="#E51A1A")
        self.btn_cheat.grid(row=6, column=0, padx=15, pady=(40, 8), sticky="ew")

        self.btn_settings = self.create_nav_btn("settings", self.show_settings, fg_color="transparent", border=2)
        self.btn_settings.grid(row=7, column=0, padx=15, pady=8, sticky="ew")

        self.main_frame = ctk.CTkFrame(self, fg_color=("#FFFFFF", "#1E1E1E"), corner_radius=20)
        self.main_frame.grid(row=0, column=1, padx=25, pady=25, sticky="nsew")

        self.frames = {}
        for F in ("home", "roster", "scores", "watch", "settings"):
            self.frames[F] = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            self.frames[F].grid(row=0, column=0, sticky="nsew")

        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.refresh_ui()
        self.show_frame("home")

    def create_nav_btn(self, key, command, fg_color="#FF1493", hover_color="#FF69B4", border=0):
        txt = self.texts[self.current_lang][key]
        if border > 0:
            return ctk.CTkButton(
                self.nav_frame,
                text=txt,
                font=self.btn_font,
                fg_color=fg_color,
                border_color="#FF1493",
                border_width=border,
                hover_color=("#E0E0E0", "#33001b"),
                text_color="#FF1493",
                height=50,
                corner_radius=12,
                command=command
            )
        return ctk.CTkButton(
            self.nav_frame,
            text=txt,
            font=self.btn_font,
            fg_color=fg_color,
            hover_color=hover_color,
            height=50,
            corner_radius=12,
            command=command,
            text_color="white"
        )

    def refresh_ui(self):
        for f in self.frames.values():
            for w in f.winfo_children():
                w.destroy()

        self.build_home()
        self.build_roster()
        self.build_scores()
        self.build_watch()
        self.build_settings()

    def show_frame(self, name):
        for f in self.frames.values():
            f.grid_remove()
        self.frames[name].grid()

    def show_home(self):
        self.show_frame("home")

    def show_roster(self):
        self.show_frame("roster")

    def show_scores(self):
        self.show_frame("scores")

    def show_watch(self):
        self.show_frame("watch")

    def show_settings(self):
        self.show_frame("settings")

    # ---------------- HOME ----------------
    def build_home(self):
        f = self.frames["home"]

        ctk.CTkLabel(
            f,
            text=self.texts[self.current_lang]["welcome"],
            font=self.title_font,
            text_color=("#121212", "#FFFFFF")
        ).pack(pady=(70, 15))

        ctk.CTkLabel(
            f,
            text=self.texts[self.current_lang]["info"],
            font=self.main_font,
            text_color="gray"
        ).pack(pady=10)

    # ---------------- ROSTER WITH SIDE PANEL ----------------
    def build_roster(self):
        f = self.frames["roster"]

        ctk.CTkLabel(
            f,
            text=self.texts[self.current_lang]["game_select"],
            font=self.title_font,
            text_color=("#121212", "#FFFFFF")
        ).pack(pady=20)

        container = ctk.CTkFrame(f, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=10)

        left = ctk.CTkScrollableFrame(container, width=420, fg_color="transparent")
        left.pack(side="left", fill="y", padx=(0, 15), pady=10)

        right = ctk.CTkFrame(container, corner_radius=18, fg_color=("#EEEEEE", "#222222"))
        right.pack(side="left", fill="both", expand=True, pady=10)

        self.roster_title_lbl = ctk.CTkLabel(
            right,
            text=self.texts[self.current_lang]["roster_panel_title"],
            font=self.card_title_font,
            text_color="#FF1493"
        )
        self.roster_title_lbl.pack(pady=(25, 10))

        self.roster_info_lbl = ctk.CTkLabel(
            right,
            text="Bir oyun seç...",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=("#121212", "#FFFFFF"),
            justify="left"
        )
        self.roster_info_lbl.pack(pady=20, padx=20, anchor="w")

        self.player_box = ctk.CTkScrollableFrame(right, fg_color="transparent")
        self.player_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        for g in self.roster_data.keys():
            b = ctk.CTkButton(
                left,
                text=g,
                font=self.btn_font,
                height=70,
                corner_radius=15,
                fg_color=("#EEEEEE", "#2A2A2A"),
                text_color=("#121212", "#FFFFFF"),
                hover_color="#FF1493",
                command=lambda x=g: self.show_players_panel(x)
            )
            b.pack(pady=10, fill="x")

    def show_players_panel(self, game):
        self.selected_game = game

        self.roster_info_lbl.configure(text=f"🎮 {game} {self.texts[self.current_lang]['roster_title']}")

        for w in self.player_box.winfo_children():
            w.destroy()

        players = self.roster_data.get(game, [])

        if not players:
            ctk.CTkLabel(
                self.player_box,
                text="Oyuncu bulunamadı.",
                font=self.main_font,
                text_color="gray"
            ).pack(pady=10)
            return

        for i, player in enumerate(players, start=1):
            card = ctk.CTkFrame(self.player_box, corner_radius=14, fg_color=("#DDDDDD", "#2B2B2B"))
            card.pack(fill="x", pady=8)

            ctk.CTkLabel(
                card,
                text=f"{i}. {player}",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=("#121212", "#FFFFFF")
            ).pack(anchor="w", padx=18, pady=15)

    # ---------------- SCORES ----------------
    def build_scores(self):
        f = self.frames["scores"]

        ctk.CTkLabel(
            f,
            text=self.texts[self.current_lang]["live_scores"],
            font=self.title_font,
            text_color=("#121212", "#FFFFFF")
        ).pack(pady=30)

        box = ctk.CTkFrame(f, fg_color=("#EEEEEE", "#2A2A2A"), corner_radius=15)
        box.pack(padx=50, fill="x", pady=20)

        ctk.CTkLabel(
            box,
            text="Skor verisi bekleniyor...",
            font=self.main_font,
            text_color="gray"
        ).pack(pady=20)

    # ---------------- WATCH ----------------
    def build_watch(self):
        f = self.frames["watch"]

        ctk.CTkLabel(
            f,
            text="Maç İzleme Merkezi",
            font=self.title_font,
            text_color=("#121212", "#FFFFFF")
        ).pack(pady=(50, 30))

        card = ctk.CTkFrame(f, corner_radius=20, fg_color=("#EEEEEE", "#222222"))
        card.pack(padx=80, pady=20, fill="x")

        ctk.CTkButton(
            card,
            text=self.texts[self.current_lang]["watch_live"],
            font=self.btn_font,
            height=65,
            fg_color="#FF1493",
            hover_color="#FF69B4",
            corner_radius=14,
            command=lambda: webbrowser.open("https://kick.com/efelvs")
        ).pack(padx=30, pady=(30, 15), fill="x")

        ctk.CTkButton(
            card,
            text=self.texts[self.current_lang]["watch_history"],
            font=self.btn_font,
            height=65,
            fg_color=("#333333", "#333333"),
            hover_color="#444444",
            corner_radius=14,
            command=lambda: webbrowser.open("https://youtube.com/@efelvs")
        ).pack(padx=30, pady=(0, 30), fill="x")

    # ---------------- SETTINGS ----------------
    def build_settings(self):
        f = self.frames["settings"]

        ctk.CTkLabel(
            f,
            text=self.texts[self.current_lang]["settings"],
            font=self.title_font,
            text_color=("#121212", "#FFFFFF")
        ).pack(pady=30)

        ctk.CTkButton(
            f,
            text=self.texts[self.current_lang]["theme"],
            font=self.btn_font,
            height=45,
            fg_color=("#EEEEEE", "#2A2A2A"),
            text_color=("#121212", "#FFFFFF"),
            command=self.switch_theme
        ).pack(pady=10)

        ctk.CTkButton(
            f,
            text=self.texts[self.current_lang]["lang"],
            font=self.btn_font,
            height=45,
            fg_color=("#EEEEEE", "#2A2A2A"),
            text_color=("#121212", "#FFFFFF"),
            command=self.switch_lang
        ).pack(pady=10)

    def switch_theme(self):
        ctk.set_appearance_mode("light" if ctk.get_appearance_mode() == "Dark" else "dark")

    def switch_lang(self):
        self.current_lang = "EN" if self.current_lang == "TR" else "TR"
        self.refresh_ui()

    # ---------------- REAL DEEP SCAN ----------------
    def run_cheat_scan(self):
        messagebox.showinfo("Anti-Cheat", self.texts[self.current_lang]["scanning"])

        suspicious_keywords = [
            "wurst", "cheatengine", "vape", "huzuni", "aimbot", "killaura", "injector",
            "processhacker", "xenos", "dllinjector", "extremeinjector", "krnl", "synapse",
            "scriptware", "fluxus", "electron", "solara", "jjsploit", "executor",
            "silentaim", "esp", "wallhack", "triggerbot", "autoclicker"
        ]

        found_items = []

        # 1) PROCESS TARAMA
        try:
            for p in psutil.process_iter(['name', 'exe']):
                pname = (p.info['name'] or "").lower()
                pexe = (p.info['exe'] or "").lower()

                if any(k in pname or k in pexe for k in suspicious_keywords):
                    found_items.append(f"PROCESS: {p.info['name']} | {p.info['exe']}")
        except:
            pass

        # 2) KLASÖR TARAMA
        scan_paths = []

        try:
            user_profile = os.path.expanduser("~")
            appdata = os.getenv("APPDATA", "")
            localappdata = os.getenv("LOCALAPPDATA", "")

            scan_paths.extend([
                os.path.join(user_profile, "Desktop"),
                os.path.join(user_profile, "Downloads"),
                os.path.join(user_profile, "Documents"),
                os.path.join(user_profile, "AppData", "Roaming"),
                os.path.join(user_profile, "AppData", "Local"),
                os.path.join(user_profile, "AppData", "Local", "Temp"),
                os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup"),
                os.path.join(localappdata, "Temp"),
            ])
        except:
            pass

        checked = set()
        max_files = 3000

        for base in scan_paths:
            if not base or not os.path.exists(base):
                continue
            if base in checked:
                continue
            checked.add(base)

            scanned_count = 0

            try:
                for root, dirs, files in os.walk(base):
                    for name in files:
                        scanned_count += 1
                        if scanned_count > max_files:
                            break

                        lower_name = name.lower()
                        full_path = os.path.join(root, name).lower()

                        if any(k in lower_name or k in full_path for k in suspicious_keywords):
                            found_items.append(f"FILE: {os.path.join(root, name)}")

                    if scanned_count > max_files:
                        break
            except:
                pass

        # 3) STARTUP BASİT KONTROL
        try:
            startup_folder = os.path.join(
                os.getenv("APPDATA", ""),
                "Microsoft", "Windows", "Start Menu", "Programs", "Startup"
            )
            if os.path.exists(startup_folder):
                for item in os.listdir(startup_folder):
                    item_lower = item.lower()
                    if any(k in item_lower for k in suspicious_keywords):
                        found_items.append(f"STARTUP: {os.path.join(startup_folder, item)}")
        except:
            pass

        # SONUÇ
        if found_items:
            preview = "\n".join(found_items[:8])
            if len(found_items) > 8:
                preview += f"\n... ve {len(found_items)-8} tane daha"

            messagebox.showerror(
                "ALARM",
                f"{self.texts[self.current_lang]['found']}\n\n{preview}"
            )
        else:
            messagebox.showinfo("OK", f"{self.texts[self.current_lang]['clean']}\n{self.texts[self.current_lang]['scan_done']}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
