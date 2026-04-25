import sys
import os
import time
import requests
import psutil
import threading
import webbrowser
import customtkinter as ctk
from tkinter import messagebox
from pypresence import Presence

CLIENT_ID = "1497357433645961237"
WEBHOOK_URL = "https://discord.com/api/webhooks/1497711458362982411/MA1_NY_s0kFLXf0M-lQU_ISoHDtOXyi1HYJPRl_jnXlWic08qxkafwtD0-I8kyuQ8RRd"

APP_VERSION = "1.2"
VERSION_URL = "https://raw.githubusercontent.com/EfeLvss/espor-app-data/refs/heads/main/version.txt"
CODE_URL = "https://raw.githubusercontent.com/EfeLvss/espor-app-data/refs/heads/main/main.py"
ROSTER_URL = "https://raw.githubusercontent.com/EfeLvss/espor-app-data/refs/heads/main/kadro.json"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PlayzEsportHub")
        self.geometry("1150x750")
        self.resizable(False, False)
        
        self.main_font = ctk.CTkFont(family="Segoe UI", size=14)
        self.title_font = ctk.CTkFont(family="Segoe UI", size=28, weight="bold")
        self.btn_font = ctk.CTkFont(family="Segoe UI", size=15, weight="bold")
        
        self.current_lang = "TR"
        self.texts = {
            "TR": {
                "home": "Ana Sayfa", "roster": "Takım Kadrosu", "scores": "Maç Skorları", "watch": "Maç İzle",
                "cheat": "Hile Kontrol", "settings": "Ayarlar", "welcome": "PlayzEsportHub'a Hoş Geldin!",
                "info": "Maçları izleyebilir ve kadroları takip edebilirsiniz.",
                "game_select": "Kadro Seçimi", "roster_title": "Kadrosu",
                "live_scores": "Canlı Skorlar", "watch_live": "Canlı Yayın", "watch_replay": "Maç Tekrarları",
                "stream_info": "Yayın harici tarayıcıda platformsuz açılacaktır.",
                "start_stream": "🔴 Canlı Yayını Başlat", "theme": "Tema Değiştir", "lang": "Dil / Language",
                "cheat_warn": "Tarama için oyunun açık olması lazım!", "clean": "Sistem Temiz!",
                "found": "Zararlı işlem bulundu:", "scanning": "Derin tarama yapılıyor...", "upd_wait": "Güncelleniyor..."
            },
            "EN": {
                "home": "Home", "roster": "Roster", "scores": "Scores", "watch": "Watch",
                "cheat": "Anti-Cheat", "settings": "Settings", "welcome": "Welcome to PlayzEsportHub!",
                "info": "Watch matches and track rosters directly.",
                "game_select": "Select Roster", "roster_title": "Roster",
                "live_scores": "Live Scores", "watch_live": "Live Stream", "watch_replay": "Replays",
                "stream_info": "Stream will open in browser as embed.",
                "start_stream": "🔴 Start Stream", "theme": "Switch Theme", "lang": "Language / Dil",
                "cheat_warn": "Game must be running for scan!", "clean": "System Clean!",
                "found": "Suspicious process found:", "scanning": "Deep scanning...", "upd_wait": "Updating..."
            }
        }
        
        self.roster_data = {
            "Valorant": ["EfeLvs", "Talha"], "Brawl Stars": ["Oyuncu 31"],
            "eFootball": ["Talha", "EfeLvs"], "Roblox": ["Oyuncu 1"], "Minecraft": ["Wurst Hunter"]
        }
        
        self.auto_update()
        self.fetch_remote_roster()
        self.connect_rpc()
        self.setup_ui()
        threading.Thread(target=self.check_game_status, daemon=True).start()

    def auto_update(self):
        try:
            resp = requests.get(VERSION_URL, timeout=5)
            if resp.status_code == 200:
                remote_v = resp.text.strip()
                if remote_v != APP_VERSION:
                    code_resp = requests.get(CODE_URL, timeout=10)
                    if code_resp.status_code == 200:
                        file_path = os.path.abspath(sys.argv[0])
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(code_resp.text)
                        os.execv(sys.executable, [sys.executable] + sys.argv)
        except:
            pass

    def fetch_remote_roster(self):
        try:
            response = requests.get(ROSTER_URL, timeout=5)
            if response.status_code == 200:
                self.roster_data = response.json()
        except:
            pass

    def connect_rpc(self):
        try:
            self.rpc = Presence(CLIENT_ID)
            self.rpc.connect()
            self.rpc.update(state="PlayzEsportHub", start=time.time())
        except:
            pass

    def check_game_status(self):
        while True:
            try:
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'].lower() in ["javaw.exe", "valorant.exe", "minecraft.exe"]:
                        requests.post(WEBHOOK_URL, json={"content": f"🎮 Kullanıcı şu an {proc.info['name']} oynuyor!"})
                        return
            except: pass
            time.sleep(60)

    def setup_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.nav_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("#F5F5F5", "#121212"))
        self.nav_frame.grid(row=0, column=0, sticky="nsew")
        self.nav_frame.grid_rowconfigure(8, weight=1)

        self.logo_label = ctk.CTkLabel(self.nav_frame, text="PlayzEsport", font=self.title_font, text_color="#FF1493")
        self.logo_label.grid(row=0, column=0, padx=25, pady=(35, 45))

        self.btn_home = self.create_nav_btn("home", self.show_home)
        self.btn_home.grid(row=1, column=0, padx=15, pady=8, sticky="ew")

        self.btn_team = self.create_nav_btn("roster", self.show_roster)
        self.btn_team.grid(row=2, column=0, padx=15, pady=8, sticky="ew")

        self.btn_scores = self.create_nav_btn("scores", self.show_scores)
        self.btn_scores.grid(row=3, column=0, padx=15, pady=8, sticky="ew")

        self.btn_kick = self.create_nav_btn("watch", self.show_kick)
        self.btn_kick.grid(row=4, column=0, padx=15, pady=8, sticky="ew")

        self.btn_cheat = self.create_nav_btn("cheat", self.run_cheat_scan, fg_color="#A81010", hover_color="#E51A1A")
        self.btn_cheat.grid(row=6, column=0, padx=15, pady=(40, 8), sticky="ew")

        self.btn_settings = self.create_nav_btn("settings", self.show_settings, fg_color="transparent", border=2)
        self.btn_settings.grid(row=7, column=0, padx=15, pady=8, sticky="ew")

        self.main_frame = ctk.CTkFrame(self, fg_color=("#FFFFFF", "#1E1E1E"), corner_radius=20)
        self.main_frame.grid(row=0, column=1, padx=25, pady=25, sticky="nsew")

        self.frames = {}
        for F in ("home", "roster", "scores", "kick", "settings"):
            self.frames[F] = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            self.frames[F].grid(row=0, column=0, sticky="nsew")

        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.refresh_ui()
        self.show_frame("home")

    def create_nav_btn(self, key, command, fg_color="#FF1493", hover_color="#FF69B4", border=0):
        txt = self.texts[self.current_lang][key]
        if border > 0:
            return ctk.CTkButton(self.nav_frame, text=txt, font=self.btn_font, fg_color=fg_color, border_color="#FF1493", border_width=border, hover_color=("#E0E0E0", "#33001b"), text_color="#FF1493", height=45, corner_radius=10, command=command)
        return ctk.CTkButton(self.nav_frame, text=txt, font=self.btn_font, fg_color=fg_color, hover_color=hover_color, height=45, corner_radius=10, command=command, text_color="white")

    def refresh_ui(self):
        for f in self.frames.values():
            for w in f.winfo_children(): w.destroy()
        
        self.build_home()
        self.build_roster()
        self.build_scores()
        self.build_kick()
        self.build_settings()

    def show_frame(self, name):
        for f in self.frames.values(): f.grid_remove()
        self.frames[name].grid()

    def show_home(self): self.show_frame("home")
    def show_roster(self): self.show_frame("roster")
    def show_scores(self): self.show_frame("scores")
    def show_kick(self): self.show_frame("kick")
    def show_settings(self): self.show_frame("settings")

    def build_home(self):
        f = self.frames["home"]
        ctk.CTkLabel(f, text=self.texts[self.current_lang]["welcome"], font=self.title_font, text_color=("#121212", "#FFFFFF")).pack(pady=(60, 15))
        ctk.CTkLabel(f, text=self.texts[self.current_lang]["info"], font=self.main_font, text_color="gray").pack(pady=10)

    def build_roster(self):
        f = self.frames["roster"]
        ctk.CTkLabel(f, text=self.texts[self.current_lang]["game_select"], font=self.title_font, text_color=("#121212", "#FFFFFF")).pack(pady=20)
        sf = ctk.CTkScrollableFrame(f, fg_color="transparent")
        sf.pack(fill="both", expand=True, padx=30)
        for i, g in enumerate(self.roster_data.keys()):
            b = ctk.CTkButton(sf, text=g, font=self.btn_font, height=70, corner_radius=15, fg_color=("#EEEEEE", "#2A2A2A"), text_color=("#121212", "#FFFFFF"), hover_color="#FF1493", command=lambda x=g: self.show_players(x))
            b.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            sf.grid_columnconfigure(i%2, weight=1)
        self.p_lbl = ctk.CTkLabel(f, text="", font=ctk.CTkFont(size=18, weight="bold"), text_color=("#121212", "#FFFFFF"))
        self.p_lbl.pack(pady=20)

    def show_players(self, g):
        self.p_lbl.configure(text=f"━ {g} {self.texts[self.current_lang]['roster_title']} ━\n\n" + "\n".join(self.roster_data[g]))

    def build_scores(self):
        f = self.frames["scores"]
        ctk.CTkLabel(f, text=self.texts[self.current_lang]["live_scores"], font=self.title_font, text_color=("#121212", "#FFFFFF")).pack(pady=30)
        box = ctk.CTkFrame(f, fg_color=("#EEEEEE", "#2A2A2A"), corner_radius=15)
        box.pack(padx=50, fill="x")
        ctk.CTkLabel(box, text="PlayzEsport  3 - 1  G2", font=self.main_font, text_color=("#121212", "#FFFFFF")).pack(pady=15)

    def build_kick(self):
        f = self.frames["kick"]
        self.tab = ctk.CTkSegmentedButton(f, values=[self.texts[self.current_lang]["watch_live"], self.texts[self.current_lang]["watch_replay"]], font=self.btn_font, selected_color="#FF1493")
        self.tab.pack(pady=20, padx=30, fill="x")
        self.tab.set(self.texts[self.current_lang]["watch_live"])
        ctk.CTkLabel(f, text=self.texts[self.current_lang]["stream_info"], font=self.main_font, text_color="gray").pack(pady=20)
        ctk.CTkButton(f, text=self.texts[self.current_lang]["start_stream"], font=self.btn_font, height=60, fg_color="#FF1493", command=lambda: webbrowser.open("https://player.kick.com/eray")).pack()

    def build_settings(self):
        f = self.frames["settings"]
        ctk.CTkLabel(f, text=self.texts[self.current_lang]["settings"], font=self.title_font, text_color=("#121212", "#FFFFFF")).pack(pady=30)
        ctk.CTkButton(f, text=self.texts[self.current_lang]["theme"], font=self.btn_font, height=45, fg_color=("#EEEEEE", "#2A2A2A"), text_color=("#121212", "#FFFFFF"), command=self.switch_theme).pack(pady=10)
        ctk.CTkButton(f, text=self.texts[self.current_lang]["lang"], font=self.btn_font, height=45, fg_color=("#EEEEEE", "#2A2A2A"), text_color=("#121212", "#FFFFFF"), command=self.switch_lang).pack(pady=10)

    def switch_theme(self):
        ctk.set_appearance_mode("light" if ctk.get_appearance_mode() == "Dark" else "dark")

    def switch_lang(self):
        self.current_lang = "EN" if self.current_lang == "TR" else "TR"
        self.btn_home.configure(text=self.texts[self.current_lang]["home"])
        self.btn_team.configure(text=self.texts[self.current_lang]["roster"])
        self.btn_scores.configure(text=self.texts[self.current_lang]["scores"])
        self.btn_kick.configure(text=self.texts[self.current_lang]["watch"])
        self.btn_cheat.configure(text=self.texts[self.current_lang]["cheat"])
        self.btn_settings.configure(text=self.texts[self.current_lang]["settings"])
        self.refresh_ui()

    def run_cheat_scan(self):
        messagebox.showinfo("Anti-Cheat", self.texts[self.current_lang]["scanning"])
        sigs = ["wurst", "cheatengine", "vape", "huzuni", "aimbot", "killaura", "metin2mod", "injector"]
        found = False
        try:
            for p in psutil.process_iter(['name', 'exe']):
                n = p.info['name'].lower()
                path = (p.info['exe'] or "").lower()
                if any(s in n or s in path for s in sigs):
                    messagebox.showerror("ALARM", f"{self.texts[self.current_lang]['found']} {n}")
                    found = True; break
        except: pass
        if not found: messagebox.showinfo("OK", self.texts[self.current_lang]["clean"])

if __name__ == "__main__":
    app = App()
    app.mainloop()
