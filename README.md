# Poker Session Tracker

A desktop application for tracking poker sessions between friends. Built with Python and Tkinter.

## Features

- Track multiple poker sessions
- Manage player buy-ins and rebuys
- View player statistics and leaderboard
- Track session history
- Clean and intuitive user interface

## Installation

1. Make sure you have Python 3.7 or higher installed on your system
2. Clone this repository or download the source code
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python poker_tracker.py
   ```

2. Main Features:
   - Start New Session: Create a new poker session with players and initial buy-in
   - View Leaderboard: See all players ranked by total profit/loss
   - View Player Stats: Check detailed statistics for any player
   - View Past Sessions: Browse through all previous sessions

3. During a Session:
   - Add players to the session
   - Record rebuys when players need more chips
   - Enter cash-out amounts at the end of the session
   - The app automatically calculates profits/losses

## Data Storage

All session data is stored locally in a `poker_data.json` file in the same directory as the application.

## License

This project is open source and available under the MIT License. 