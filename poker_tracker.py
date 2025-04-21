import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime
import tkcalendar

class PokerTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Poker Session Tracker")
        self.root.geometry("800x600")
        self.root.configure(bg="white")
        
        # Set style
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Helvetica", 12))
        self.style.configure("TLabel", font=("Helvetica", 12), background="white")
        self.style.configure("TEntry", font=("Helvetica", 12))
        
        # Load or create data file
        self.data_file = "poker_data.json"
        self.load_data()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create title
        title_label = ttk.Label(self.main_frame, text="Poker Session Tracker", 
                              font=("Helvetica", 24, "bold"))
        title_label.pack(pady=20)
        
        # Create buttons
        self.create_main_buttons()
        
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
    
    def create_main_buttons(self):
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(pady=20)
        
        buttons = [
            ("Start New Session", self.start_new_session),
            ("View Leaderboard", self.view_leaderboard),
            ("View Player Stats", self.view_player_stats),
            ("View Past Sessions", self.view_past_sessions)
        ]
        
        for text, command in buttons:
            button = ttk.Button(button_frame, text=text, command=command, width=20)
            button.pack(pady=10)
    
    def start_new_session(self):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Create back button
        back_button = ttk.Button(self.main_frame, text="← Back", 
                               command=self.show_main_screen)
        back_button.pack(anchor="nw", pady=10)
        
        # Create session form
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(pady=20)
        
        # Date input
        date_frame = ttk.Frame(form_frame)
        date_frame.pack(fill=tk.X, pady=5)
        ttk.Label(date_frame, text="Session Date:").pack(side=tk.LEFT)
        self.date_entry = tkcalendar.DateEntry(date_frame, width=12, 
                                             background='darkblue',
                                             foreground='white',
                                             borderwidth=2)
        self.date_entry.pack(side=tk.LEFT, padx=5)
        
        # Buy-in amount
        buyin_frame = ttk.Frame(form_frame)
        buyin_frame.pack(fill=tk.X, pady=5)
        ttk.Label(buyin_frame, text="Initial Buy-In Amount:").pack(side=tk.LEFT)
        self.buyin_entry = ttk.Entry(buyin_frame, width=10)
        self.buyin_entry.pack(side=tk.LEFT, padx=5)
        
        # Players list
        players_frame = ttk.Frame(form_frame)
        players_frame.pack(fill=tk.X, pady=5)
        ttk.Label(players_frame, text="Players:").pack(anchor="w")
        
        self.players_listbox = tk.Listbox(players_frame, height=5, width=30)
        self.players_listbox.pack(side=tk.LEFT, padx=5)
        
        # Player input
        player_input_frame = ttk.Frame(players_frame)
        player_input_frame.pack(side=tk.LEFT, padx=5)
        
        self.player_entry = ttk.Entry(player_input_frame, width=20)
        self.player_entry.pack(pady=5)
        
        add_player_button = ttk.Button(player_input_frame, text="Add Player",
                                     command=self.add_player)
        add_player_button.pack(pady=5)
        
        # Start session button
        start_button = ttk.Button(form_frame, text="Start Session",
                                command=self.create_session)
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
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Create back button
        back_button = ttk.Button(self.main_frame, text="← Back", 
                               command=self.show_main_screen)
        back_button.pack(anchor="nw", pady=10)
        
        # Session info
        info_frame = ttk.Frame(self.main_frame)
        info_frame.pack(pady=10)
        ttk.Label(info_frame, text=f"Session Date: {session_data['date']}").pack()
        ttk.Label(info_frame, text=f"Initial Buy-In: ${session_data['initial_buyin']}").pack()
        
        # Players frame
        players_frame = ttk.Frame(self.main_frame)
        players_frame.pack(pady=20)
        
        for player in session_data["players"]:
            player_frame = ttk.Frame(players_frame)
            player_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(player_frame, text=player["name"]).pack(side=tk.LEFT, padx=5)
            ttk.Label(player_frame, text=f"Total Buy-Ins: ${player['total_buyins']}").pack(side=tk.LEFT, padx=5)
            
            rebuy_button = ttk.Button(player_frame, text="Add Rebuy",
                                    command=lambda p=player: self.add_rebuy(p))
            rebuy_button.pack(side=tk.LEFT, padx=5)
            
            cashout_entry = ttk.Entry(player_frame, width=10)
            cashout_entry.pack(side=tk.LEFT, padx=5)
            
            save_button = ttk.Button(player_frame, text="Save Cash Out",
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
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Create back button
        back_button = ttk.Button(self.main_frame, text="← Back", 
                               command=self.show_main_screen)
        back_button.pack(anchor="nw", pady=10)
        
        # Create leaderboard title
        ttk.Label(self.main_frame, text="Leaderboard", 
                 font=("Helvetica", 20, "bold")).pack(pady=20)
        
        # Create leaderboard table
        tree = ttk.Treeview(self.main_frame, columns=("Name", "Profit/Loss", "Sessions"), 
                          show="headings")
        tree.heading("Name", text="Player Name")
        tree.heading("Profit/Loss", text="Total Profit/Loss")
        tree.heading("Sessions", text="Sessions Played")
        
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
        
        tree.pack(pady=20)
    
    def view_player_stats(self):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Create back button
        back_button = ttk.Button(self.main_frame, text="← Back", 
                               command=self.show_main_screen)
        back_button.pack(anchor="nw", pady=10)
        
        # Create player selection
        selection_frame = ttk.Frame(self.main_frame)
        selection_frame.pack(pady=20)
        
        ttk.Label(selection_frame, text="Select Player:").pack(side=tk.LEFT, padx=5)
        
        # Get unique players
        players = set()
        for session in self.data["sessions"]:
            for player in session["players"]:
                players.add(player["name"])
        
        player_var = tk.StringVar()
        player_dropdown = ttk.Combobox(selection_frame, textvariable=player_var,
                                     values=sorted(players), state="readonly")
        player_dropdown.pack(side=tk.LEFT, padx=5)
        
        view_button = ttk.Button(selection_frame, text="View Stats",
                               command=lambda: self.show_player_stats(player_var.get()))
        view_button.pack(side=tk.LEFT, padx=5)
    
    def show_player_stats(self, player_name):
        # Clear previous stats if any
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Frame) and widget != self.main_frame.winfo_children()[0]:
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
        stats_frame = ttk.Frame(self.main_frame)
        stats_frame.pack(pady=20)
        
        stats = [
            ("Total Sessions Played", str(total_sessions)),
            ("Total Profit/Loss", f"${total_profit:.2f}"),
            ("Average Profit/Loss per Session", f"${total_profit/total_sessions:.2f}" if total_sessions > 0 else "$0.00"),
            ("Biggest Win", f"${biggest_win:.2f}"),
            ("Biggest Loss", f"${biggest_loss:.2f}")
        ]
        
        for label, value in stats:
            frame = ttk.Frame(stats_frame)
            frame.pack(fill=tk.X, pady=5)
            ttk.Label(frame, text=label, width=25).pack(side=tk.LEFT)
            ttk.Label(frame, text=value).pack(side=tk.LEFT)
        
        # Create session history table
        history_frame = ttk.Frame(self.main_frame)
        history_frame.pack(pady=20)
        
        ttk.Label(history_frame, text="Session History", 
                 font=("Helvetica", 16, "bold")).pack(pady=10)
        
        tree = ttk.Treeview(history_frame, columns=("Date", "Profit/Loss"), 
                          show="headings")
        tree.heading("Date", text="Date")
        tree.heading("Profit/Loss", text="Profit/Loss")
        
        for session in sorted(session_history, key=lambda x: x["date"], reverse=True):
            tree.insert("", tk.END, values=(session["date"], f"${session['profit']:.2f}"))
        
        tree.pack()
    
    def view_past_sessions(self):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Create back button
        back_button = ttk.Button(self.main_frame, text="← Back", 
                               command=self.show_main_screen)
        back_button.pack(anchor="nw", pady=10)
        
        # Create sessions title
        ttk.Label(self.main_frame, text="Past Sessions", 
                 font=("Helvetica", 20, "bold")).pack(pady=20)
        
        # Create sessions list
        sessions_frame = ttk.Frame(self.main_frame)
        sessions_frame.pack(pady=20)
        
        for session in sorted(self.data["sessions"], 
                            key=lambda x: x["date"], 
                            reverse=True):
            session_frame = ttk.Frame(sessions_frame)
            session_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(session_frame, text=f"Date: {session['date']}").pack(anchor="w")
            ttk.Label(session_frame, text=f"Initial Buy-In: ${session['initial_buyin']}").pack(anchor="w")
            
            for player in session["players"]:
                player_frame = ttk.Frame(session_frame)
                player_frame.pack(fill=tk.X, pady=2)
                
                ttk.Label(player_frame, text=f"{player['name']}:", width=15).pack(side=tk.LEFT)
                ttk.Label(player_frame, text=f"Buy-Ins: ${player['total_buyins']}").pack(side=tk.LEFT, padx=5)
                ttk.Label(player_frame, text=f"Cash Out: ${player['cash_out']}").pack(side=tk.LEFT, padx=5)
                ttk.Label(player_frame, text=f"Profit/Loss: ${player['profit']}").pack(side=tk.LEFT, padx=5)
            
            ttk.Separator(sessions_frame, orient="horizontal").pack(fill=tk.X, pady=10)
    
    def show_main_screen(self):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Recreate main screen
        title_label = ttk.Label(self.main_frame, text="Poker Session Tracker", 
                              font=("Helvetica", 24, "bold"))
        title_label.pack(pady=20)
        
        self.create_main_buttons()

if __name__ == "__main__":
    root = tk.Tk()
    app = PokerTracker(root)
    root.mainloop() 