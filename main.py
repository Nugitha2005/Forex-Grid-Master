import MetaTrader5 as mt5
import customtkinter as ctk  # The modern UI library
from classes import GridBot
from threading import Thread

# --- THEME SETTINGS ---
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title('FutureTrade AI | Bot Dashboard')
        self.geometry('400x950')  # Slightly wider/taller for better spacing
        self.resizable(False, False)

        # --- FONT STYLES ---
        self.header_font = ("Roboto Medium", 20)
        self.label_font = ("Roboto", 12)

        # ==========================================================
        # SECTION: LOGIN
        # ==========================================================
        self.frame_login = ctk.CTkFrame(self, corner_radius=10)
        self.frame_login.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        # Title
        self.lbl_title = ctk.CTkLabel(self.frame_login, text="AUTHENTICATION", font=self.header_font,
                                      text_color="#00E5FF")
        self.lbl_title.grid(row=0, column=0, columnspan=2, pady=(10, 10))

        # Login Fields
        self.txtb_login = ctk.CTkEntry(self.frame_login, placeholder_text="Login ID")
        self.txtb_login.grid(row=1, column=0, padx=10, pady=5)

        self.txtb_passwd = ctk.CTkEntry(self.frame_login, placeholder_text="Password", show="*")
        self.txtb_passwd.grid(row=1, column=1, padx=10, pady=5)

        self.txtb_server = ctk.CTkEntry(self.frame_login, placeholder_text="Server")
        self.txtb_server.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        # Login Button (Neon Style)
        self.btn_login = ctk.CTkButton(self.frame_login, text="CONNECT TO TERMINAL", command=self.Login,
                                       fg_color="#00C853", hover_color="#009624")
        self.btn_login.grid(row=3, column=0, columnspan=2, padx=10, pady=(10, 20), sticky="ew")

        # ==========================================================
        # HELPER: FUNCTION TO CREATE BOT FRAMES
        # ==========================================================
        def create_bot_section(parent, row_idx, bot_name, run_command, color):
            frame = ctk.CTkFrame(parent, corner_radius=10, border_color=color, border_width=1)
            frame.grid(row=row_idx, column=0, padx=20, pady=10, sticky="ew")

            # Header
            lbl = ctk.CTkLabel(frame, text=f"// {bot_name}", font=("Roboto Medium", 14), text_color=color)
            lbl.grid(row=0, column=0, columnspan=2, pady=5, sticky="w", padx=15)

            # We create specific variables for your logic to grab
            txt_symbol = ctk.CTkEntry(frame, placeholder_text="Symbol (e.g. EURUSD)")
            txt_volume = ctk.CTkEntry(frame, placeholder_text="Volume (e.g. 0.01)")
            txt_tp = ctk.CTkEntry(frame, placeholder_text="TP")
            txt_levels = ctk.CTkEntry(frame, placeholder_text="Levels")

            # --- MODIFIED SECTION FOR DELAY ---
            txt_cycles = ctk.CTkEntry(frame, placeholder_text="Cycles")
            txt_delay = ctk.CTkEntry(frame, placeholder_text="Delay (sec)")  # <--- NEW FIELD

            # Grid Layout for inputs
            txt_symbol.grid(row=1, column=0, padx=5, pady=2)
            txt_volume.grid(row=1, column=1, padx=5, pady=2)
            txt_tp.grid(row=2, column=0, padx=5, pady=2)
            txt_levels.grid(row=2, column=1, padx=5, pady=2)

            # Split row 3 between Cycles and Delay
            txt_cycles.grid(row=3, column=0, padx=5, pady=2)
            txt_delay.grid(row=3, column=1, padx=5, pady=2)  # <--- NEW GRID POSITION

            # Run Button
            btn = ctk.CTkButton(frame, text=f"INITIALIZE {bot_name.upper()}", command=run_command, fg_color=color,
                                hover_color="#333333")
            btn.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

            # Return the delay box along with the others
            return txt_symbol, txt_volume, txt_tp, txt_levels, txt_cycles, txt_delay

        # ==========================================================
        # CREATE BOT 1 SECTION
        # ==========================================================
        # Added self.b1_del to catch the new return value
        self.b1_symbol, self.b1_vol, self.b1_tp, self.b1_lvl, self.b1_cyc, self.b1_del = create_bot_section(self, 1,
                                                                                                            "Alpha Bot",
                                                                                                            self.run_b1,
                                                                                                            "#2962FF")

        # ==========================================================
        # CREATE BOT 2 SECTION
        # ==========================================================
        self.b2_symbol, self.b2_vol, self.b2_tp, self.b2_lvl, self.b2_cyc, self.b2_del = create_bot_section(self, 2,
                                                                                                            "Beta Bot",
                                                                                                            self.run_b2,
                                                                                                            "#FF6D00")

        # ==========================================================
        # CREATE BOT 3 SECTION
        # ==========================================================
        self.b3_symbol, self.b3_vol, self.b3_tp, self.b3_lvl, self.b3_cyc, self.b3_del = create_bot_section(self, 3,
                                                                                                            "Gamma Bot",
                                                                                                            self.run_b3,
                                                                                                            "#D500F9")

    # ==========================================================
    # LOGIC FUNCTIONS
    # ==========================================================
    def Login(self):
        try:
            login_id = int(self.txtb_login.get())
            passwd = str(self.txtb_passwd.get())
            server = str(self.txtb_server.get())

            if mt5.initialize(login=login_id, password=passwd, server=server):
                print(">>> SYSTEM ACCESS GRANTED")
                self.btn_login.configure(text="CONNECTED ✓", fg_color="gray", state="disabled")
            else:
                print(">>> ACCESS DENIED", mt5.last_error())
        except ValueError:
            print(">>> ERROR: Check Input Format")

    def run_b1(self):
        # Added self.b1_del
        self._start_bot(self.b1_symbol, self.b1_vol, self.b1_tp, self.b1_lvl, self.b1_cyc, self.b1_del)

    def run_b2(self):
        self._start_bot(self.b2_symbol, self.b2_vol, self.b2_tp, self.b2_lvl, self.b2_cyc, self.b2_del)

    def run_b3(self):
        self._start_bot(self.b3_symbol, self.b3_vol, self.b3_tp, self.b3_lvl, self.b3_cyc, self.b3_del)

    def _start_bot(self, txt_sym, txt_vol, txt_tp, txt_lvl, txt_cyc, txt_del):
        try:
            symbol = str(txt_sym.get())
            volume = float(txt_vol.get())
            tp = float(txt_tp.get())
            levels = int(txt_lvl.get())
            cycles = int(txt_cyc.get())
            delay = int(txt_del.get())  # <--- Get delay from the box

            print(f">>> LAUNCHING PROTOCOL FOR: {symbol} WITH {delay}s DELAY")

            # IMPORTANT: Ensure your GridBot class accepts 'delay' as the 6th argument!
            bot = GridBot(symbol, volume, tp, levels, cycles, delay)

            thread = Thread(target=bot.run)
            thread.start()
        except ValueError:
            print(">>> ERROR: Invalid numeric input (Check Delay field)")


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    app = App()
    app.mainloop()