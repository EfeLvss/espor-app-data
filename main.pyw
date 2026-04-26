import sys
import os
import time
import requests
import psutil
import threading
import webbrowser
import subprocess
import socket
import ctypes
import customtkinter as ctk
from tkinter import messagebox, filedialog
from pypresence import Presence
from moviepy import VideoFileClip

CLIENT_ID = "1497357433645961237"
WEBHOOK_URL = "https://discord.com/api/webhooks/1497711458362982411/MA1_NY_s0kFLXf0M-lQU_ISoHDtOXyi1HYJPRl_jnXlWic08qxkafwtD0-I8kyuQ8RRd"

APP_VERSION = "2.3"
VERSION_URL = "https://raw.githubusercontent.com/EfeLvss/espor-app-data/refs/heads/main/version.txt"
CODE_URL = "https://raw.githubusercontent.com/EfeLvss/espor-app-data/refs/heads/main/main.pyw"
ROSTER_URL = "https://raw.githubusercontent.com/EfeLvss/espor-app-data/refs/heads/main/kadro.json"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Windows click-through styles
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW = 0x00000080


class OverlayWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.running = True
        self.cached_ping = 0

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.geometry("300x28+2+2")
        self.configure(fg_color="#0B0B0B")

        try:
            self.attributes("-alpha", 0.80)
        except:
            pass

        self.container = ctk.CTkFrame(self, fg_color="#0B0B0B", corner_radius=6)
        self.container.pack(fill="both", expand=True, padx=1, pady=1)

        self.label = ctk.CTkLabel(
            self.container,
            text="TPS:20.0 | P:0 | R:0%",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#00FF99"
        )
        self.label.pack(anchor="w", padx=8, pady=4)

        self.after(150, self.enable_clickthrough)
        self.after(100, self.force_topmost)

        threading.Thread(target=self.ping_loop, daemon=True).start()
        self.update_overlay()

    def enable_clickthrough(self):
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            styles = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(
                hwnd,
                GWL_EXSTYLE,
                styles | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW
            )
        except:
            pass

    def ping_loop(self):
        while self.running:
            self.cached_ping = self.get_ping()
            time.sleep(3)

    def get_ping(self):
        try:
            start = time.time()
            s = socket.create_connection(("8.8.8.8", 53), timeout=0.5)
            s.close()
            return int((time.time() - start) * 1000)
        except:
            return 0

    def force_topmost(self):
        if self.running:
            try:
                self.attributes("-topmost", True)
                self.lift()
                self.geometry("+2+2")
            except:
                pass
            self.after(1500, self.force_topmost)

    def update_overlay(self):
        if not self.running:
            return

        ram = int(psutil.virtual_memory().percent)
        tps = "20.0"

        self.label.configure(text=f"TPS:{tps} | P:{self.cached_ping} | R:{ram}%")
        self.after(2000, self.update_overlay)

    def stop_overlay(self):
        self.running = False
        self.destroy()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PlayzEsportHub")
        self.geometry("1360x820")
        self.resizable(False, False)

        self.main_font = ctk.CTkFont(family="Segoe UI", size=14)
        self.title_font = ctk.CTkFont(family="Segoe UI", size=30, weight="bold")
        self.btn_font = ctk.CTkFont(family="Segoe UI", size=15, weight="bold")
        self.card_title_font = ctk.CTkFont(family="Segoe UI", size=20, weight="bold")

        self.current_lang = "TR"
        self.overlay_window = None

        self.texts = {
            "TR": {
                "home": "Ana Sayfa",
                "roster": "Takım Kadrosu",
                "scores": "Maç Skorları",
                "watch": "Maç İzle",
                "performance": "Performance",
                "compressor": "Video Sıkıştırıcı",
                "cheat": "Anti-Cheat (Derin Tarama)",
                "settings": "Ayarlar",
                "welcome": "PlayzEsportHub'a Hoş Geldin!",
                "info": "Kadro takibi, yayınlar, performans araçları ve video sıkıştırıcı.",
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
                "scan_done": "Tarama tamamlandı!",
                "overlay_on": "Overlay Aç",
                "overlay_off": "Overlay Kapat",
                "boost_mc": "Minecraft Boost Aç",
                "boost_info": "Minecraft önceliği yükseltildi.",
                "compress_title": "Video Sıkıştırıcı",
                "compress_desc": "Video seç ve yaklaşık 50 MB'a sıkıştır.",
                "select_video": "Video Seç ve 50MB Yap"
            },
            "EN": {
                "home": "Home",
                "roster": "Roster",
                "scores": "Match Scores",
                "watch": "Watch Match",
                "performance": "Performance",
                "compressor": "Video Compressor",
                "cheat": "Anti-Cheat (Deep Scan)",
                "settings": "Settings",
                "welcome": "Welcome to PlayzEsportHub!",
                "info": "Track rosters, streams, performance tools and video compressor.",
                "game_select": "Roster Selection",
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
                "scan_done": "Scan completed!",
                "overlay_on": "Enable Overlay",
                "overlay_off": "Disable Overlay",
                "boost_mc": "Enable Minecraft Boost",
                "boost_info": "Minecraft priority increased.",
                "compress_title": "Video Compressor",
                "compress_desc": "Choose a video and compress it to about 50 MB.",
                "select_video": "Choose Video and Make 50MB"
            }
        }

        self.roster_data = {
            "Roblox": ["EfeLvs", "Oyuncu 2", "Oyuncu 3"],
            "Valorant": ["EfeLvs", "Talha"],
            "eFootball": ["Talha", "EfeLvs"],
            "Brawl Stars": ["Oyuncu 1"],
            "Minecraft": ["Cloopzy", "EfeLvs"]
        }

        self.setup_ui()

        threading.Thread(target=self.auto_update_loop, daemon=True).start()
        threading.Thread(target=self.fetch_remote_roster_and_refresh, daemon=True).start()
        threading.Thread(target=self.connect_rpc, daemon=True).start()
        threading.Thread(target=self.check_game_status, daemon=True).start()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------- UPDATE ----------------
    def auto_update(self):
        try:
            headers = {
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }

            version_url = f"{VERSION_URL}?t={int(time.time() * 1000)}"
            resp = requests.get(version_url, headers=headers, timeout=2.5)

            if resp.status_code != 200:
                return

            remote_v = resp.text.strip().replace("\ufeff", "").replace("\n", "").replace("\r", "")
            local_v = str(APP_VERSION).strip()

            if not remote_v or remote_v == local_v:
                return

            code_url = f"{CODE_URL}?t={int(time.time() * 1000)}"
            code_resp = requests.get(code_url, headers=headers, timeout=6)

            if code_resp.status_code == 200 and len(code_resp.text) > 500:
                file_path = os.path.abspath(sys.argv[0])

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code_resp.text)

                try:
                    self.after(0, lambda: messagebox.showinfo(
                        "Güncelleme",
                        f"Yeni sürüm bulundu! ({remote_v}) Uygulama yeniden başlatılıyor."
                    ))
                except:
                    pass

                time.sleep(1)
                subprocess.Popen([sys.executable, file_path], creationflags=subprocess.CREATE_NO_WINDOW)
                os._exit(0)

        except:
            pass

    def auto_update_loop(self):
        self.auto_update()

        for _ in range(4):
            time.sleep(5)
            self.auto_update()

        while True:
            time.sleep(30)
            self.auto_update()

    # ---------------- ROSTER ----------------
    def fetch_remote_roster(self):
        try:
            response = requests.get(f"{ROSTER_URL}?t={int(time.time() * 1000)}", timeout=2.5)
            if response.status_code == 200:
                remote_data = response.json()
                for game, players in self.roster_data.items():
                    if game not in remote_data:
                        remote_data[game] = players
                self.roster_data = remote_data
        except:
            pass

    def fetch_remote_roster_and_refresh(self):
        self.fetch_remote_roster()
        try:
            self.after(0, self.refresh_ui)
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

    # ---------------- MINECRAFT BOOST ----------------
    def boost_minecraft(self):
        boosted = False
        try:
            for proc in psutil.process_iter(['name']):
                name = (proc.info['name'] or "").lower()
                if name in ["javaw.exe", "minecraft.exe"]:
                    try:
                        p = psutil.Process(proc.pid)
                        p.nice(psutil.HIGH_PRIORITY_CLASS)
                        boosted = True
                    except:
                        pass
        except:
            pass

        if boosted:
            messagebox.showinfo("Boost", self.texts[self.current_lang]["boost_info"])
        else:
            messagebox.showwarning("Boost", "Minecraft açık değil kanka." if self.current_lang == "TR" else "Minecraft is not open.")

    # ---------------- VIDEO COMPRESSOR ----------------
    def compress_video_to_50mb(self):
        try:
            input_path = filedialog.askopenfilename(
                title="Video seç" if self.current_lang == "TR" else "Choose video",
                filetypes=[("Video Files", "*.mp4 *.mov *.avi *.mkv *.webm")]
            )

            if not input_path:
                return

            save_path = filedialog.asksaveasfilename(
                title="Kaydet" if self.current_lang == "TR" else "Save As",
                defaultextension=".mp4",
                filetypes=[("MP4 Video", "*.mp4")],
                initialfile="compressed_50mb.mp4"
            )

            if not save_path:
                return

            messagebox.showinfo(
                self.texts[self.current_lang]["compress_title"],
                "Sıkıştırma başladı. Büyük videoda sürebilir."
                if self.current_lang == "TR" else
                "Compression started. Large videos may take some time."
            )

            target_size_mb = 50
            target_size_bits = target_size_mb * 1024 * 1024 * 8

            clip = VideoFileClip(input_path)
            duration = clip.duration

            if duration <= 0:
                messagebox.showerror("Hata" if self.current_lang == "TR" else "Error",
                                     "Video süresi okunamadı." if self.current_lang == "TR" else "Video duration could not be read.")
                clip.close()
                return

            audio_bitrate_kbps = 96
            total_bitrate_bps = target_size_bits / duration
            video_bitrate_kbps = int((total_bitrate_bps / 1000) - audio_bitrate_kbps)

            if video_bitrate_kbps < 250:
                video_bitrate_kbps = 250

            width, height = clip.size
            if width > 1280:
                clip = clip.resized(width=1280)

            clip.write_videofile(
                save_path,
                codec="libx264",
                audio_codec="aac",
                bitrate=f"{video_bitrate_kbps}k",
                audio_bitrate=f"{audio_bitrate_kbps}k",
                preset="slow",
                threads=4,
                logger=None
            )

            clip.close()

            final_size_mb = os.path.getsize(save_path) / (1024 * 1024)

            if final_size_mb <= 50.5:
                messagebox.showinfo(
                    "Başarılı" if self.current_lang == "TR" else "Success",
                    f"Video sıkıştırıldı!\nBoyut: {final_size_mb:.2f} MB"
                    if self.current_lang == "TR" else
                    f"Video compressed!\nSize: {final_size_mb:.2f} MB"
                )
            else:
                messagebox.showwarning(
                    "Uyarı" if self.current_lang == "TR" else "Warning",
                    f"Video sıkıştırıldı ama çıktı {final_size_mb:.2f} MB oldu."
                    if self.current_lang == "TR" else
                    f"Video compressed but output is {final_size_mb:.2f} MB."
                )

        except Exception as e:
            messagebox.showerror(
                "Hata" if self.current_lang == "TR" else "Error",
                f"Video sıkıştırma hatası:\n{str(e)}"
            )

    # ---------------- SETTINGS ACTIONS ----------------
    def switch_theme(self):
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")

    def switch_lang(self):
        self.current_lang = "EN" if self.current_lang == "TR" else "TR"
        self.refresh_ui()

    # ---------------- UI ----------------
    def setup_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.nav_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=("#F5F5F5", "#121212"), width=280)
        self.nav_frame.grid(row=0, column=0, sticky="nsew")
        self.nav_frame.grid_rowconfigure(12, weight=1)

        self.logo_label = ctk.CTkLabel(self.nav_frame, text="PlayzEsport", font=self.title_font, text_color="#FF1493")
        self.logo_label.grid(row=0, column=0, padx=25, pady=(35, 35))

        self.btn_home = self.create_nav_btn("home", self.show_home)
        self.btn_home.grid(row=1, column=0, padx=15, pady=8, sticky="ew")

        self.btn_team = self.create_nav_btn("roster", self.show_roster)
        self.btn_team.grid(row=2, column=0, padx=15, pady=8, sticky="ew")

        self.btn_scores = self.create_nav_btn("scores", self.show_scores)
        self.btn_scores.grid(row=3, column=0, padx=15, pady=8, sticky="ew")

        self.btn_watch = self.create_nav_btn("watch", self.show_watch)
        self.btn_watch.grid(row=4, column=0, padx=15, pady=8, sticky="ew")

        self.btn_perf = self.create_nav_btn("performance", self.show_performance)
        self.btn_perf.grid(row=5, column=0, padx=15, pady=8, sticky="ew")

        self.btn_compressor = self.create_nav_btn("compressor", self.show_compressor, fg_color="#7A3DFF", hover_color="#8F5BFF")
        self.btn_compressor.grid(row=6, column=0, padx=15, pady=8, sticky="ew")

        self.btn_cheat = self.create_nav_btn("cheat", self.run_cheat_scan, fg_color="#A81010", hover_color="#E51A1A")
        self.btn_cheat.grid(row=8, column=0, padx=15, pady=(30, 8), sticky="ew")

        self.btn_settings = self.create_nav_btn("settings", self.show_settings, fg_color="transparent", border=2)
        self.btn_settings.grid(row=9, column=0, padx=15, pady=8, sticky="ew")

        self.main_frame = ctk.CTkFrame(self, fg_color=("#FFFFFF", "#1E1E1E"), corner_radius=20)
        self.main_frame.grid(row=0, column=1, padx=25, pady=25, sticky="nsew")

        self.frames = {}
        for F in ("home", "roster", "scores", "watch", "performance", "compressor", "settings"):
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
                self.nav_frame, text=txt, font=self.btn_font, fg_color=fg_color,
                border_color="#FF1493", border_width=border, hover_color=("#E0E0E0", "#33001b"),
                text_color="#FF1493", height=50, corner_radius=12, command=command
            )
        return ctk.CTkButton(
            self.nav_frame, text=txt, font=self.btn_font, fg_color=fg_color,
            hover_color=hover_color, height=50, corner_radius=12, command=command, text_color="white"
        )

    def refresh_ui(self):
        for f in self.frames.values():
            for w in f.winfo_children():
                w.destroy()

        self.build_home()
        self.build_roster()
        self.build_scores()
        self.build_watch()
        self.build_performance()
        self.build_compressor()
        self.build_settings()

        self.btn_home.configure(text=self.texts[self.current_lang]["home"])
        self.btn_team.configure(text=self.texts[self.current_lang]["roster"])
        self.btn_scores.configure(text=self.texts[self.current_lang]["scores"])
        self.btn_watch.configure(text=self.texts[self.current_lang]["watch"])
        self.btn_perf.configure(text=self.texts[self.current_lang]["performance"])
        self.btn_compressor.configure(text=self.texts[self.current_lang]["compressor"])
        self.btn_cheat.configure(text=self.texts[self.current_lang]["cheat"])
        self.btn_settings.configure(text=self.texts[self.current_lang]["settings"])

    def show_frame(self, name):
        for f in self.frames.values():
            f.grid_remove()
        self.frames[name].grid()

    def show_home(self): self.show_frame("home")
    def show_roster(self): self.show_frame("roster")
    def show_scores(self): self.show_frame("scores")
    def show_watch(self): self.show_frame("watch")
    def show_performance(self): self.show_frame("performance")
    def show_compressor(self): self.show_frame("compressor")
    def show_settings(self): self.show_frame("settings")

    def build_home(self):
        f = self.frames["home"]
        ctk.CTkLabel(f, text=self.texts[self.current_lang]["welcome"], font=self.title_font, text_color=("#121212", "#FFFFFF")).pack(pady=(70, 15))
        ctk.CTkLabel(f, text=self.texts[self.current_lang]["info"], font=self.main_font, text_color="gray").pack(pady=10)

    def build_roster(self):
        f = self.frames["roster"]
        ctk.CTkLabel(f, text=self.texts[self.current_lang]["game_select"], font=self.title_font, text_color=("#121212", "#FFFFFF")).pack(pady=20)

        container = ctk.CTkFrame(f, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=10)

        left = ctk.CTkScrollableFrame(container, width=420, fg_color="transparent")
        left.pack(side="left", fill="y", padx=(0, 15), pady=10)

        right = ctk.CTkFrame(container, corner_radius=18, fg_color=("#EEEEEE", "#222222"))
        right.pack(side="left", fill="both", expand=True, pady=10)

        self.roster_title_lbl = ctk.CTkLabel(right, text=self.texts[self.current_lang]["roster_panel_title"], font=self.card_title_font, text_color="#FF1493")
        self.roster_title_lbl.pack(pady=(25, 10))

        self.roster_info_lbl = ctk.CTkLabel(right, text="Bir oyun seç..." if self.current_lang == "TR" else "Select a game...", font=ctk.CTkFont(size=18, weight="bold"), text_color=("#121212", "#FFFFFF"), justify="left")
        self.roster_info_lbl.pack(pady=20, padx=20, anchor="w")

        self.player_box = ctk.CTkScrollableFrame(right, fg_color="transparent")
        self.player_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        for g in self.roster_data.keys():
            b = ctk.CTkButton(
                left, text=g, font=self.btn_font, height=70, corner_radius=15,
                fg_color=("#EEEEEE", "#2A2A2A"), text_color=("#121212", "#FFFFFF"),
                hover_color="#FF1493", command=lambda x=g: self.show_players_panel(x)
            )
            b.pack(pady=10, fill="x")

    def show_players_panel(self, game):
        self.roster_info_lbl.configure(text=f"🎮 {game} {self.texts[self.current_lang]['roster_title']}")
        for w in self.player_box.winfo_children():
            w.destroy()

        players = self.roster_data.get(game, [])
        if not players:
            ctk.CTkLabel(self.player_box, text="Oyuncu bulunamadı." if self.current_lang == "TR" else "No players found.", font=self.main_font, text_color="gray").pack(pady=10)
            return

        for i, player in enumerate(players, start=1):
            card = ctk.CTkFrame(self.player_box, corner_radius=14, fg_color=("#DDDDDD", "#2B2B2B"))
            card.pack(fill="x", pady=8)
            ctk.CTkLabel(card, text=f"{i}. {player}", font=ctk.CTkFont(size=18, weight="bold"), text_color=("#121212", "#FFFFFF")).pack(anchor="w", padx=18, pady=15)

    def build_scores(self):
        f = self.frames["scores"]
        ctk.CTkLabel(f, text=self.texts[self.current_lang]["live_scores"], font=self.title_font, text_color=("#121212", "#FFFFFF")).pack(pady=30)

    def build_watch(self):
        f = self.frames["watch"]
        ctk.CTkLabel(
            f,
            text="Maç İzleme Merkezi" if self.current_lang == "TR" else "Match Watch Center",
            font=self.title_font,
            text_color=("#121212", "#FFFFFF")
        ).pack(pady=(50, 30))

        card = ctk.CTkFrame(f, corner_radius=20, fg_color=("#EEEEEE", "#222222"))
        card.pack(padx=80, pady=20, fill="x")

        ctk.CTkButton(
            card, text=self.texts[self.current_lang]["watch_live"], font=self.btn_font,
            height=65, fg_color="#FF1493", hover_color="#FF69B4", corner_radius=14,
            command=lambda: webbrowser.open("https://kick.com/efelvs")
        ).pack(padx=30, pady=(30, 15), fill="x")

        ctk.CTkButton(
            card, text=self.texts[self.current_lang]["watch_history"], font=self.btn_font,
            height=65, fg_color=("#333333", "#333333"), hover_color="#444444", corner_radius=14,
            command=lambda: webbrowser.open("https://youtube.com/@efelvs")
        ).pack(padx=30, pady=(0, 30), fill="x")

    def build_performance(self):
        f = self.frames["performance"]

        ctk.CTkLabel(f, text="Performance Center", font=self.title_font, text_color=("#121212", "#FFFFFF")).pack(pady=(35, 20))

        top = ctk.CTkFrame(f, corner_radius=20, fg_color=("#EEEEEE", "#222222"))
        top.pack(fill="x", padx=40, pady=10)

        ctk.CTkButton(
            top, text=self.texts[self.current_lang]["overlay_on"], font=self.btn_font,
            height=55, fg_color="#00AA66", hover_color="#00CC77", corner_radius=14,
            command=self.enable_overlay
        ).pack(side="left", padx=20, pady=20)

        ctk.CTkButton(
            top, text=self.texts[self.current_lang]["overlay_off"], font=self.btn_font,
            height=55, fg_color="#AA2222", hover_color="#CC3333", corner_radius=14,
            command=self.disable_overlay
        ).pack(side="left", padx=10, pady=20)

        ctk.CTkButton(
            top, text=self.texts[self.current_lang]["boost_mc"], font=self.btn_font,
            height=55, fg_color="#3366FF", hover_color="#4A7BFF", corner_radius=14,
            command=self.boost_minecraft
        ).pack(side="left", padx=10, pady=20)

    def build_compressor(self):
        f = self.frames["compressor"]

        ctk.CTkLabel(
            f,
            text=self.texts[self.current_lang]["compress_title"],
            font=self.title_font,
            text_color=("#121212", "#FFFFFF")
        ).pack(pady=(60, 15))

        ctk.CTkLabel(
            f,
            text=self.texts[self.current_lang]["compress_desc"],
            font=self.main_font,
            text_color="gray"
        ).pack(pady=10)

        ctk.CTkButton(
            f,
            text=self.texts[self.current_lang]["select_video"],
            font=self.btn_font,
            height=60,
            width=320,
            fg_color="#7A3DFF",
            hover_color="#8F5BFF",
            corner_radius=16,
            command=self.compress_video_to_50mb
        ).pack(pady=30)

    def build_settings(self):
        f = self.frames["settings"]

        ctk.CTkLabel(f, text=self.texts[self.current_lang]["settings"], font=self.title_font, text_color=("#121212", "#FFFFFF")).pack(pady=30)

        ctk.CTkButton(
            f, text=self.texts[self.current_lang]["theme"], font=self.btn_font, height=45,
            fg_color=("#EEEEEE", "#2A2A2A"), text_color=("#121212", "#FFFFFF"), command=self.switch_theme
        ).pack(pady=10)

        ctk.CTkButton(
            f, text=self.texts[self.current_lang]["lang"], font=self.btn_font, height=45,
            fg_color=("#EEEEEE", "#2A2A2A"), text_color=("#121212", "#FFFFFF"), command=self.switch_lang
        ).pack(pady=10)

    def run_cheat_scan(self):
        messagebox.showinfo("Anti-Cheat", self.texts[self.current_lang]["scanning"])

        suspicious_keywords = [
            "wurst", "cheatengine", "vape", "huzuni", "aimbot", "killaura", "injector",
            "processhacker", "xenos", "dllinjector", "extremeinjector", "krnl", "synapse",
            "scriptware", "fluxus", "electron", "solara", "jjsploit", "executor"
        ]

        found_items = []

        try:
            for p in psutil.process_iter(['name', 'exe']):
                pname = (p.info['name'] or "").lower()
                pexe = (p.info['exe'] or "").lower()
                if any(k in pname or k in pexe for k in suspicious_keywords):
                    found_items.append(f"PROCESS: {p.info['name']} | {p.info['exe']}")
        except:
            pass

        if found_items:
            preview = "\n".join(found_items[:8])
            messagebox.showerror("ALARM", f"{self.texts[self.current_lang]['found']}\n\n{preview}")
        else:
            messagebox.showinfo("OK", f"{self.texts[self.current_lang]['clean']}\n{self.texts[self.current_lang]['scan_done']}")

    def enable_overlay(self):
        if self.overlay_window is None or not self.overlay_window.winfo_exists():
            self.overlay_window = OverlayWindow(self)

    def disable_overlay(self):
        if self.overlay_window and self.overlay_window.winfo_exists():
            self.overlay_window.stop_overlay()
            self.overlay_window = None

    def on_close(self):
        try:
            self.disable_overlay()
        except:
            pass
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
