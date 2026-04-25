import sys
import os
import time
import requests
import psutil
import threading
import multiprocessing
import webview
import customtkinter as ctk
from tkinter import messagebox
from pypresence import Presence

CLIENT_ID = "1497357433645961237"
WEBHOOK_URL = "https://discord.com/api/webhooks/1497711458362982411/MA1_NY_s0kFLXf0M-lQU_ISoHDtOXyi1HYJPRl_jnXlWic08qxkafwtD0-I8kyuQ8RRd"

APP_VERSION = "1.0"
VERSION_URL = "https://raw.githubusercontent.com/EfeLvss/repo/main/version.txt"
CODE_URL = "https://raw.githubusercontent.com/EfeLvss/repo/main/main.py"
ROSTER_URL = "https://raw.githubusercontent.com/EfeLvss/repo/main/kadro.json"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

def open_stream(url):
    webview.create_window('PlayzEsport Yayın', url, width=1024, height=576, background_color='#000000')
    webview.start()

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
                "info": "Uygulama üzerinden maçları izleyebilir ve kadroları takip edebilirsin.",
                "game_select": "Kadro Seçimi", "roster_title": "Kadrosu",
                "live_scores": "Canlı Skorlar", "watch_live": "Canlı Yayın", "watch_replay": "Maç Tekrarları",
                "stream_info": "Yayın sadece platformsuz saf oynatıcı (embed) olarak açılacaktır.",
                "start_stream": "🔴 Canlı Yayını Başlat", "theme": "Açık / Koyu Tema", "lang": "Dil: Türkçe / English",
                "cheat_warn": "Tarama için oyunun açık olması lazım!", "clean": "Sistem Temiz! Hile bulunamadı.",
                "found": "Şüpheli yazılım/işlem bulundu:", "scanning": "Sistem derinlemesine taranıyor..."
            },
            "EN": {
                "home": "Home", "roster": "Team Roster", "scores": "Match Scores", "watch": "Watch Match",
                "cheat": "Anti-Cheat", "settings": "Settings", "welcome": "Welcome to PlayzEsportHub!",
                "info": "Watch matches and track rosters directly through the app.",
                "game_select": "Select Roster", "roster_title": "Roster",
                "live_scores": "Live Scores", "watch_live": "Live Stream", "watch_replay": "Match Replays",
                "stream_info": "The stream will open as a pure embed player without platform UI.",
                "start_stream": "🔴 Start Live Stream", "theme": "Light / Dark Theme", "lang": "Language: Türkçe / English",
                "cheat_warn": "The game must be running for the scan!", "clean": "System Clean! No cheats found.",
                "found": "Suspicious software/process found:", "scanning": "Deep scanning system..."
            }
        }
        
        self.roster_data = {
            "Valorant": ["Oyuncu 1", "Oyuncu 2"], "Brawl Stars": ["Oyuncu 1", "Oyuncu 2"],
            "eFootball": ["Talha", "EfeLvs"], "Roblox": ["Oyuncu 1", "Oyuncu 2"], "Minecraft": ["Oyuncu 1", "Oyuncu 2"]
        }
        
        self.auto_update()
        self.fetch_remote_roster()
        self.connect_rpc()
        self.setup_ui()
        threading.Thread(target=self.check_game_status, daemon=True).start()

    def auto_update(self):
        try:
            resp = requests.get(VERSION_URL, timeout=3)
            if resp.status_code == 200:
                remote_version = resp.text.strip()
                if remote_version != APP_VERSION:
                    code_resp = requests.get(CODE_URL, timeout=5)
                    if code_resp.status_code == 200:
                        with open(sys.argv[0], 'w', encoding='utf-8') as f:
                            f.write(code_resp.text)
                        os.execv(sys.executable, ['python'] + sys.argv)
        except:
            pass

    def fetch_remote_roster(self):
        try:
            response = requests.get(ROSTER_URL, timeout=3)
            if response.status_code == 200:
                self.roster_data = response.json()
        except:
            pass

    def connect_rpc(self):
        try:
            self.rpc = Presence(CLIENT_ID)
            self.rpc.connect()
            self.rpc.update(state="PlayzEsportHub Kullanıyor", start=time.time())
        except:
            pass

    def check_game_status(self):
        games = ["javaw.exe", "minecraft.exe", "valorant.exe"]
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() in games:
                    requests.post(WEBHOOK_URL, json={"content": "🎮 **PlayzEsportHub:** Bir kullanıcı şu an oyunda!"})
                    break
        except:
            pass

    def setup_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Çift renk ayarları (Açık Tema Rengi, Koyu Tema Rengi)
        self.nav_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("#EBEBEB", "#121212"))
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
            frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.build_home()
        self.build_roster()
        self.build_scores()
        self.build_kick()
        self.build_settings()
        self.show_frame("home")

    def create_nav_btn(self, text_key, command, fg_color="#FF1493", hover_color="#FF69B4", border=0):
        text = self.texts[self.current_lang][text_key]
        if border > 0:
            return ctk.CTkButton(self.nav_frame, text=text, font=self.btn_font, fg_color=fg_color, border_color="#FF1493", border_width=border, hover_color="#33001b", text_color="#FF1493", height=45, corner_radius=10, command=command)
        return ctk.CTkButton(self.nav_frame, text=text, font=self.btn_font, fg_color=fg_color, hover_color=hover_color, height=45, corner_radius=10, command=command)

    def show_frame(self, name):
        for frame in self.frames.values():
            frame.grid_remove()
        self.frames[name].grid()

    def show_home(self): self.show_frame("home")
    def show_roster(self): self.show_frame("roster")
    def show_scores(self): self.show_frame("scores")
    def show_kick(self): self.show_frame("kick")
    def show_settings(self): self.show_frame("settings")

    def build_home(self):
        frame = self.frames["home"]
        self.lbl_welcome = ctk.CTkLabel(frame, text=self.texts[self.current_lang]["welcome"], font=self.title_font, text_color=("#000000", "#FFFFFF"))
        self.lbl_welcome.pack(pady=(60, 15))
        self.lbl_info = ctk.CTkLabel(frame, text=self.texts[self.current_lang]["info"], font=self.main_font, text_color="gray")
        self.lbl_info.pack(pady=10)

    def build_roster(self):
        frame = self.frames["roster"]
        self.lbl_roster_title = ctk.CTkLabel(frame, text=self.texts[self.current_lang]["game_select"], font=self.title_font, text_color=("#000000", "#FFFFFF"))
        self.lbl_roster_title.pack(pady=(30, 20))
        
        games_frame = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        games_frame.pack(fill="both", expand=True, padx=30)
        
        games = ["Valorant", "Brawl Stars", "eFootball", "Roblox", "Minecraft"]
        for i, game in enumerate(games):
            btn = ctk.CTkButton(games_frame, text=game, font=self.btn_font, height=70, corner_radius=15, fg_color=("#F0F0F0", "#2A2A2A"), text_color=("#000000", "#FFFFFF"), hover_color="#FF1493", command=lambda g=game: self.show_team_players(g))
            btn.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            games_frame.grid_columnconfigure(i%2, weight=1)
            
        self.players_label = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"), text_color=("#000000", "#FFFFFF"))
        self.players_label.pack(pady=20)

    def show_team_players(self, game):
        players = "\n".join(self.roster_data.get(game, []))
        self.players_label.configure(text=f"━ {game} {self.texts[self.current_lang]['roster_title']} ━\n\n{players}")

    def build_scores(self):
        frame = self.frames["scores"]
        self.lbl_scores_title = ctk.CTkLabel(frame, text=self.texts[self.current_lang]["live_scores"], font=self.title_font, text_color=("#000000", "#FFFFFF"))
        self.lbl_scores_title.pack(pady=(30, 30))
        
        score_frame = ctk.CTkFrame(frame, fg_color=("#F0F0F0", "#2A2A2A"), corner_radius=15)
        score_frame.pack(padx=50, fill="x")
        ctk.CTkLabel(score_frame, text="PlayzEsport  3 - 1  G2 Esports", font=self.main_font, text_color=("#000000", "#FFFFFF")).pack(pady=15)

    def build_kick(self):
        frame = self.frames["kick"]
        
        self.watch_tab = ctk.CTkSegmentedButton(frame, values=[self.texts[self.current_lang]["watch_live"], self.texts[self.current_lang]["watch_replay"]], command=self.switch_watch_tab, font=self.btn_font, selected_color="#FF1493", selected_hover_color="#FF69B4")
        self.watch_tab.pack(pady=(20, 10), padx=30, fill="x")
        self.watch_tab.set(self.texts[self.current_lang]["watch_live"])

        self.live_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.replay_frame = ctk.CTkFrame(frame, fg_color="transparent")
        
        self.live_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.lbl_stream_info = ctk.CTkLabel(self.live_frame, text=self.texts[self.current_lang]["stream_info"], font=self.main_font, text_color="gray")
        self.lbl_stream_info.pack(pady=(40, 20))
        
        self.btn_start_stream = ctk.CTkButton(self.live_frame, text=self.texts[self.current_lang]["start_stream"], font=self.btn_font, height=60, fg_color="#FF1493", hover_color="#FF69B4", command=lambda: self.launch_stream("https://player.kick.com/eray"))
        self.btn_start_stream.pack(pady=10)

        ctk.CTkButton(self.replay_frame, text="▶ PlayzEsport vs G2 - Büyük Final", font=self.btn_font, height=55, fg_color=("#F0F0F0", "#2A2A2A"), text_color=("#000000", "#FFFFFF"), hover_color="#FF1493", command=lambda: self.launch_stream("https://player.kick.com/eray")).pack(pady=10, fill="x", padx=50)

    def switch_watch_tab(self, value):
        if value == self.texts[self.current_lang]["watch_live"]:
            self.replay_frame.pack_forget()
            self.live_frame.pack(fill="both", expand=True, padx=10, pady=10)
        else:
            self.live_frame.pack_forget()
            self.replay_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def launch_stream(self, url):
        p = multiprocessing.Process(target=open_stream, args=(url,))
        p.start()

    def build_settings(self):
        frame = self.frames["settings"]
        self.lbl_settings = ctk.CTkLabel(frame, text=self.texts[self.current_lang]["settings"], font=self.title_font, text_color=("#000000", "#FFFFFF"))
        self.lbl_settings.pack(pady=(30, 30))
        
        self.btn_theme = ctk.CTkButton(frame, text=self.texts[self.current_lang]["theme"], font=self.btn_font, command=lambda: ctk.set_appearance_mode("light" if ctk.get_appearance_mode() == "Dark" else "dark"), height=45, fg_color=("#F0F0F0", "#2A2A2A"), text_color=("#000000", "#FFFFFF"), hover_color="#FF1493")
        self.btn_theme.pack(pady=15)
        
        self.btn_lang = ctk.CTkButton(frame, text=self.texts[self.current_lang]["lang"], font=self.btn_font, command=self.toggle_lang, height=45, fg_color=("#F0F0F0", "#2A2A2A"), text_color=("#000000", "#FFFFFF"), hover_color="#FF1493")
        self.btn_lang.pack(pady=15)

    def toggle_lang(self):
        self.current_lang = "EN" if self.current_lang == "TR" else "TR"
        self.update_texts()

    def update_texts(self):
        # Update Nav Buttons
        self.btn_home.configure(text=self.texts[self.current_lang]["home"])
        self.btn_team.configure(text=self.texts[self.current_lang]["roster"])
        self.btn_scores.configure(text=self.texts[self.current_lang]["scores"])
        self.btn_kick.configure(text=self.texts[self.current_lang]["watch"])
        self.btn_cheat.configure(text=self.texts[self.current_lang]["cheat"])
        self.btn_settings.configure(text=self.texts[self.current_lang]["settings"])
        
        # Update Labels
        self.lbl_welcome.configure(text=self.texts[self.current_lang]["welcome"])
        self.lbl_info.configure(text=self.texts[self.current_lang]["info"])
        self.lbl_roster_title.configure(text=self.texts[self.current_lang]["game_select"])
        self.lbl_scores_title.configure(text=self.texts[self.current_lang]["live_scores"])
        self.lbl_stream_info.configure(text=self.texts[self.current_lang]["stream_info"])
        self.btn_start_stream.configure(text=self.texts[self.current_lang]["start_stream"])
        self.lbl_settings.configure(text=self.texts[self.current_lang]["settings"])
        self.btn_theme.configure(text=self.texts[self.current_lang]["theme"])
        self.btn_lang.configure(text=self.texts[self.current_lang]["lang"])
        
        self.watch_tab.configure(values=[self.texts[self.current_lang]["watch_live"], self.texts[self.current_lang]["watch_replay"]])
        self.watch_tab.set(self.texts[self.current_lang]["watch_live"])
        self.players_label.configure(text="")

    def run_cheat_scan(self):
        messagebox.showinfo("Anti-Cheat", self.texts[self.current_lang]["scanning"])
        
        # Daha detaylı imza taraması
        cheat_signatures = ["wurst", "cheatengine", "vape", "huzuni", "aimbot", "injector", "xigncode", "memoryhacker", "macro"]
        found = False
        
        try:
            for proc in psutil.process_iter(['name', 'exe']):
                name = proc.info['name'].lower()
                if proc.info['exe']:
                    exe_path = proc.info['exe'].lower()
                else:
                    exe_path = ""
                
                if any(sig in name or sig in exe_path for sig in cheat_signatures):
                    messagebox.showerror("Tehlike", f"{self.texts[self.current_lang]['found']} {name}")
                    found = True
                    break
        except:
            pass
            
        if not found:
            messagebox.showinfo("Sonuç", self.texts[self.current_lang]["clean"])

if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = App()
    app.mainloop()
