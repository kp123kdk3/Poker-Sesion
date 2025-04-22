import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime
import tkcalendar

class PokerTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Poker Session Tracker")
        self.root.geometry("800x800")
        self.root.configure(bg="#ffffff")  # White background
        
        # Center the window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Configure ttk styles
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use clam theme as base
        
        # Configure colors
        self.bg_color = "#ffffff"  # White background
        self.accent_color = "#2196f3"  # Light blue for title
        self.text_color = "#000000"  # Black text
        self.button_bg = "#f0f0f0"  # Light grey for buttons
        self.button_hover = "#e0e0e0"  # Slightly darker on hover
        
        # Configure custom styles
        self.style.configure("Main.TFrame",
            background=self.bg_color,
            foreground=self.text_color,
            font=("Helvetica", 10)
        )
        
        self.style.configure("Title.TLabel",
            font=("Helvetica", 28, "bold"),
            background=self.bg_color,
            foreground=self.accent_color,
            padding=(0, 30)  # Vertical padding
        )
        
        self.style.configure("Custom.TButton",
            font=("Helvetica", 14),
            padding=(25, 12),
            width=30,  # Width of 30 units
            background=self.button_bg,
            foreground=self.text_color,
            borderwidth=0,
            relief="flat"
        )
        
        self.style.map("Custom.TButton",
            background=[("active", self.button_hover)]
        )
        
        # Create main container
        self.container = ttk.Frame(root, style="Main.TFrame")
        self.container.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # Show main screen
        self.show_main_screen()
        
        # Load data
        self.data_file = "poker_data.json"
        self.load_data()
    
    def create_main_buttons(self, parent):
        buttons = [
            ("Start New Session", self.start_new_session),
            ("View Leaderboard", self.view_leaderboard),
            ("View Player Stats", self.view_player_stats),
            ("View Past Sessions", self.view_past_sessions)
        ]
        
        for text, command in buttons:
            button = ttk.Button(parent, text=text, command=command,
                              style="Custom.TButton")
            button.pack(pady=15)
    
    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "players": {},
                "sessions": []
            }
            self.save_data()
    
    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)
    
    def create_section_frame(self, parent, title):
        frame = ttk.Frame(parent, style="Main.TFrame")
        frame.pack(fill=tk.X, pady=15)
        
        if title:
            label = ttk.Label(frame, text=title, 
                            font=("Segoe UI", 18, "bold"),
                            background=self.bg_color,
                            foreground=self.accent_color)
            label.pack(anchor="w", pady=(0, 15))
        
        return frame
    
    def create_input_row(self, parent, label_text, entry_width=20):
        frame = ttk.Frame(parent, style="Main.TFrame")
        frame.pack(fill=tk.X, pady=8)
        
        label = ttk.Label(frame, text=label_text, 
                         font=("Segoe UI", 11),
                         width=15, 
                         anchor="w")
        label.pack(side=tk.LEFT, padx=5)
        
        entry = ttk.Entry(frame, width=entry_width,
                         font=("Segoe UI", 11))
        entry.pack(side=tk.LEFT, padx=5)
        
        return entry
    
    def start_new_session(self):
        # Clear main frame
        for widget in self.container.winfo_children():
            if isinstance(widget, ttk.Frame) and widget != self.container.winfo_children()[0]:
                widget.destroy()
        
        # Create master frame for centering
        master_frame = ttk.Frame(self.container, style="Main.TFrame")
        master_frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Create back button
        back_button = ttk.Button(master_frame, text="← Back", 
                               command=self.show_main_screen,
                               style="Custom.TButton")
        back_button.pack(anchor="nw", pady=(0, 20))
        
        # Create form frame
        form_frame = ttk.Frame(master_frame, style="Main.TFrame")
        form_frame.pack(fill=tk.X, pady=15)
        
        # Date input
        date_frame = ttk.Frame(form_frame, style="Main.TFrame")
        date_frame.pack(fill=tk.X, pady=10)
        ttk.Label(date_frame, text="Session Date:", width=15, anchor="w").pack(side=tk.LEFT, padx=5)
        self.date_entry = tkcalendar.DateEntry(date_frame, width=12, 
                                             background='darkblue',
                                             foreground='white',
                                             borderwidth=2)
        self.date_entry.pack(side=tk.LEFT, padx=5)
        
        # Buy-in amount
        buyin_frame = ttk.Frame(form_frame, style="Main.TFrame")
        buyin_frame.pack(fill=tk.X, pady=10)
        ttk.Label(buyin_frame, text="Initial Buy-In:", width=15, anchor="w").pack(side=tk.LEFT, padx=5)
        self.buyin_entry = ttk.Entry(buyin_frame, width=30)
        self.buyin_entry.pack(side=tk.LEFT, padx=5)
        
        # Player input
        player_frame = ttk.Frame(form_frame, style="Main.TFrame")
        player_frame.pack(fill=tk.X, pady=10)
        ttk.Label(player_frame, text="Player Name:", width=15, anchor="w").pack(side=tk.LEFT, padx=5)
        self.player_entry = ttk.Entry(player_frame, width=30)
        self.player_entry.pack(side=tk.LEFT, padx=5)
        add_player_button = ttk.Button(player_frame, text="Add Player",
                                     command=self.add_player,
                                     style="Custom.TButton")
        add_player_button.pack(side=tk.LEFT, padx=5)
        
        # Players list
        list_frame = ttk.Frame(master_frame, style="Main.TFrame")
        list_frame.pack(fill=tk.X, pady=15)
        
        ttk.Label(list_frame, text="Current Players:", 
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 5))
        
        self.players_listbox = tk.Listbox(list_frame, height=5, width=50,
                                        bg="white", fg="black",
                                        font=("Segoe UI", 12))
        self.players_listbox.pack(fill=tk.X, pady=5)
        
        # Start session button
        start_button = ttk.Button(master_frame, text="Start Session",
                                command=self.create_session,
                                style="Custom.TButton")
        start_button.pack(pady=20)
    
    def add_player(self):
        player_name = self.player_entry.get().strip()
        if player_name and player_name not in self.players_listbox.get(0, tk.END):
            self.players_listbox.insert(tk.END, player_name)
            self.player_entry.delete(0, tk.END)
    
    def create_session(self):
        date = self.date_entry.get_date().strftime("%Y-%m-%d")
        try:
            buyin = float(self.buyin_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid buy-in amount")
            return
        
        players = list(self.players_listbox.get(0, tk.END))
        if not players:
            messagebox.showerror("Error", "Please add at least one player")
            return
        
        # Create session data
        session_data = {
            "date": date,
            "initial_buyin": buyin,
            "players": []
        }
        
        for player in players:
            session_data["players"].append({
                "name": player,
                "total_buyins": buyin,
                "cash_out": 0,
                "profit": 0
            })
        
        self.data["sessions"].append(session_data)
        self.save_data()
        
        # Show session management screen
        self.manage_session(session_data)
    
    def manage_session(self, session_data):
        # Clear main frame
        for widget in self.container.winfo_children():
            if isinstance(widget, ttk.Frame) and widget != self.container.winfo_children()[0]:
                widget.destroy()
        
        # Create back button
        back_button = ttk.Button(self.container, text="← Back", 
                               command=self.show_main_screen)
        back_button.pack(anchor="nw", pady=10)
        
        # Session info frame
        info_frame = self.create_section_frame(self.container, "Session Info")
        ttk.Label(info_frame, text=f"Date: {session_data['date']}").pack(anchor="w")
        ttk.Label(info_frame, text=f"Initial Buy-In: ${session_data['initial_buyin']}").pack(anchor="w")
        
        # Players frame
        players_frame = self.create_section_frame(self.container, "Active Players")
        
        for player in session_data["players"]:
            player_frame = ttk.Frame(players_frame, style="Main.TFrame")
            player_frame.pack(fill=tk.X, pady=5)
            
            # Player info
            info_frame = ttk.Frame(player_frame, style="Main.TFrame")
            info_frame.pack(side=tk.LEFT, padx=5)
            
            ttk.Label(info_frame, text=player["name"], width=15, anchor="w").pack(side=tk.LEFT)
            ttk.Label(info_frame, text=f"Buy-Ins: ${player['total_buyins']}").pack(side=tk.LEFT, padx=5)
            
            # Actions frame
            actions_frame = ttk.Frame(player_frame, style="Main.TFrame")
            actions_frame.pack(side=tk.RIGHT, padx=5)
            
            rebuy_button = ttk.Button(actions_frame, text="Add Rebuy",
                                    command=lambda p=player: self.add_rebuy(p))
            rebuy_button.pack(side=tk.LEFT, padx=5)
            
            cashout_entry = ttk.Entry(actions_frame, width=10)
            cashout_entry.pack(side=tk.LEFT, padx=5)
            
            save_button = ttk.Button(actions_frame, text="Save Cash Out",
                                   command=lambda p=player, e=cashout_entry: self.save_cashout(p, e))
            save_button.pack(side=tk.LEFT, padx=5)
    
    def add_rebuy(self, player):
        try:
            rebuy_amount = float(simpledialog.askstring("Add Rebuy", 
                                                      f"Enter rebuy amount for {player['name']}:"))
            if rebuy_amount > 0:
                player["total_buyins"] += rebuy_amount
                self.save_data()
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Please enter a valid amount")
    
    def save_cashout(self, player, entry):
        try:
            cashout = float(entry.get())
            player["cash_out"] = cashout
            player["profit"] = cashout - player["total_buyins"]
            self.save_data()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
    
    def view_leaderboard(self):
        # Clear main frame
        for widget in self.container.winfo_children():
            if isinstance(widget, ttk.Frame) and widget != self.container.winfo_children()[0]:
                widget.destroy()
        
        # Create back button
        back_button = ttk.Button(self.container, text="← Back", 
                               command=self.show_main_screen)
        back_button.pack(anchor="nw", pady=10)
        
        # Create leaderboard frame
        leaderboard_frame = self.create_section_frame(self.container, "Leaderboard")
        
        # Create leaderboard table
        tree = ttk.Treeview(leaderboard_frame, columns=("Name", "Profit/Loss", "Sessions"), 
                          show="headings", height=10)
        tree.heading("Name", text="Player Name")
        tree.heading("Profit/Loss", text="Total Profit/Loss")
        tree.heading("Sessions", text="Sessions Played")
        
        # Set column widths
        tree.column("Name", width=150)
        tree.column("Profit/Loss", width=150)
        tree.column("Sessions", width=100)
        
        # Calculate player stats
        player_stats = {}
        for session in self.data["sessions"]:
            for player in session["players"]:
                name = player["name"]
                if name not in player_stats:
                    player_stats[name] = {"profit": 0, "sessions": 0}
                player_stats[name]["profit"] += player["profit"]
                player_stats[name]["sessions"] += 1
        
        # Sort players by profit
        sorted_players = sorted(player_stats.items(), 
                              key=lambda x: x[1]["profit"], 
                              reverse=True)
        
        for name, stats in sorted_players:
            tree.insert("", tk.END, values=(name, f"${stats['profit']:.2f}", stats["sessions"]))
        
        tree.pack(fill=tk.X, pady=10)
    
    def view_player_stats(self):
        # Clear main frame
        for widget in self.container.winfo_children():
            if isinstance(widget, ttk.Frame) and widget != self.container.winfo_children()[0]:
                widget.destroy()
        
        # Create back button
        back_button = ttk.Button(self.container, text="← Back", 
                               command=self.show_main_screen)
        back_button.pack(anchor="nw", pady=10)
        
        # Create player selection frame
        selection_frame = self.create_section_frame(self.container, "Select Player")
        
        # Get unique players
        players = set()
        for session in self.data["sessions"]:
            for player in session["players"]:
                players.add(player["name"])
        
        player_var = tk.StringVar()
        player_dropdown = ttk.Combobox(selection_frame, textvariable=player_var,
                                     values=sorted(players), state="readonly",
                                     width=20)
        player_dropdown.pack(side=tk.LEFT, padx=5)
        
        view_button = ttk.Button(selection_frame, text="View Stats",
                               command=lambda: self.show_player_stats(player_var.get()))
        view_button.pack(side=tk.LEFT, padx=5)
    
    def show_player_stats(self, player_name):
        # Clear previous stats if any
        for widget in self.container.winfo_children():
            if isinstance(widget, ttk.Frame) and widget != self.container.winfo_children()[0]:
                widget.destroy()
        
        # Calculate player stats
        total_sessions = 0
        total_profit = 0
        biggest_win = 0
        biggest_loss = 0
        session_history = []
        
        for session in self.data["sessions"]:
            for player in session["players"]:
                if player["name"] == player_name:
                    total_sessions += 1
                    total_profit += player["profit"]
                    biggest_win = max(biggest_win, player["profit"])
                    biggest_loss = min(biggest_loss, player["profit"])
                    session_history.append({
                        "date": session["date"],
                        "profit": player["profit"]
                    })
        
        # Create stats frame
        stats_frame = self.create_section_frame(self.container, f"Statistics for {player_name}")
        
        stats = [
            ("Total Sessions Played", str(total_sessions)),
            ("Total Profit/Loss", f"${total_profit:.2f}"),
            ("Average Profit/Loss per Session", f"${total_profit/total_sessions:.2f}" if total_sessions > 0 else "$0.00"),
            ("Biggest Win", f"${biggest_win:.2f}"),
            ("Biggest Loss", f"${biggest_loss:.2f}")
        ]
        
        for label, value in stats:
            frame = ttk.Frame(stats_frame, style="Main.TFrame")
            frame.pack(fill=tk.X, pady=5)
            ttk.Label(frame, text=label, width=25, anchor="w").pack(side=tk.LEFT)
            ttk.Label(frame, text=value).pack(side=tk.LEFT)
        
        # Create session history frame
        history_frame = self.create_section_frame(self.container, "Session History")
        
        tree = ttk.Treeview(history_frame, columns=("Date", "Profit/Loss"), 
                          show="headings", height=10)
        tree.heading("Date", text="Date")
        tree.heading("Profit/Loss", text="Profit/Loss")
        
        # Set column widths
        tree.column("Date", width=150)
        tree.column("Profit/Loss", width=150)
        
        for session in sorted(session_history, key=lambda x: x["date"], reverse=True):
            tree.insert("", tk.END, values=(session["date"], f"${session['profit']:.2f}"))
        
        tree.pack(fill=tk.X, pady=10)
    
    def view_past_sessions(self):
        # Clear main frame
        for widget in self.container.winfo_children():
            if isinstance(widget, ttk.Frame) and widget != self.container.winfo_children()[0]:
                widget.destroy()
        
        # Create back button
        back_button = ttk.Button(self.container, text="← Back", 
                               command=self.show_main_screen)
        back_button.pack(anchor="nw", pady=10)
        
        # Create sessions frame
        sessions_frame = self.create_section_frame(self.container, "Past Sessions")
        
        for session in sorted(self.data["sessions"], 
                            key=lambda x: x["date"], 
                            reverse=True):
            session_frame = ttk.Frame(sessions_frame, style="Main.TFrame")
            session_frame.pack(fill=tk.X, pady=10)
            
            # Session info
            info_frame = ttk.Frame(session_frame, style="Main.TFrame")
            info_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(info_frame, text=f"Date: {session['date']}", 
                     font=("Segoe UI", 12, "bold")).pack(anchor="w")
            ttk.Label(info_frame, text=f"Initial Buy-In: ${session['initial_buyin']}").pack(anchor="w")
            
            # Players info
            for player in session["players"]:
                player_frame = ttk.Frame(session_frame, style="Main.TFrame")
                player_frame.pack(fill=tk.X, pady=2)
                
                ttk.Label(player_frame, text=f"{player['name']}:", 
                         width=15, anchor="w").pack(side=tk.LEFT)
                ttk.Label(player_frame, text=f"Buy-Ins: ${player['total_buyins']}").pack(side=tk.LEFT, padx=5)
                ttk.Label(player_frame, text=f"Cash Out: ${player['cash_out']}").pack(side=tk.LEFT, padx=5)
                ttk.Label(player_frame, text=f"Profit/Loss: ${player['profit']}").pack(side=tk.LEFT, padx=5)
            
            ttk.Separator(sessions_frame, orient="horizontal").pack(fill=tk.X, pady=10)
    
    def show_main_screen(self):
        # Clear main frame
        for widget in self.container.winfo_children():
            if isinstance(widget, ttk.Frame) and widget != self.container.winfo_children()[0]:
                widget.destroy()
        
        # Create title frame
        title_frame = ttk.Frame(self.container, style="Main.TFrame")
        title_frame.pack(fill=tk.X, pady=(0, 30))  # 30px padding below title
        
        # Create title
        title_label = ttk.Label(title_frame, text="Poker Session Tracker", 
                              style="Title.TLabel")
        title_label.pack()
        
        # Create button frame
        button_frame = ttk.Frame(self.container, style="Main.TFrame")
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Create buttons with proper spacing
        buttons = [
            ("Start New Session", self.start_new_session),
            ("View Leaderboard", self.view_leaderboard),
            ("View Player Stats", self.view_player_stats),
            ("View Past Sessions", self.view_past_sessions)
        ]
        
        for text, command in buttons:
            button = ttk.Button(button_frame, text=text, command=command,
                              style="Custom.TButton")
            button.pack(pady=15)  # 15px padding between buttons

if __name__ == "__main__":
    root = tk.Tk()
    app = PokerTracker(root)
    root.mainloop() 