import copy
from dataclasses import dataclass, field, asdict
from typing import List, Optional

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window
import random

# --- Data Models ---

@dataclass
class PlayerStats:
    """Individual player statistics"""
    name: str = "Player"
    runs: int = 0
    balls_faced: int = 0
    fours: int = 0
    sixes: int = 0
    wickets: int = 0  # Cumulative across match
    runs_conceded: int = 0  # Cumulative across match
    legal_balls_bowled: int = 0  # Cumulative across match
    
    def strike_rate(self) -> float:
        return (self.runs / self.balls_faced * 100) if self.balls_faced > 0 else 0.0
    
    def economy(self) -> float:
        overs = self.legal_balls_bowled / 6
        return (self.runs_conceded / overs) if overs > 0 else 0.0

@dataclass
class InningsData:
    """Store complete innings data - no approximations"""
    score: int = 0
    wickets: int = 0
    legal_balls: int = 0
    extras: int = 0
    
    def overs_str(self) -> str:
        """Format overs as X.Y"""
        return f"{self.legal_balls // 6}.{self.legal_balls % 6}"

@dataclass
class MatchState:
    """Complete match state at any moment"""
    score: int = 0
    wickets: int = 0
    legal_balls: int = 0
    extras: int = 0
    
    striker_idx: int = 0
    non_striker_idx: int = 1
    bowler_idx: int = 0
    
    current_innings: int = 1
    target: Optional[int] = None
    
    innings1_data: Optional[InningsData] = None
    innings2_data: Optional[InningsData] = None
    
    ball_history: List[str] = field(default_factory=list)
    
    team1_stats: List[PlayerStats] = field(default_factory=list)
    team2_stats: List[PlayerStats] = field(default_factory=list)

class MatchManager:
    """Core match management with all business logic"""
    
    def __init__(self):
        self.store = JsonStore('score247_data.json')
        self.reset_config()
    
    def reset_config(self):
        self.team1_name = "Team A"
        self.team2_name = "Team B"
        self.overs = 5
        self.players_per_team = 6
        
        self.team1_players = []
        self.team2_players = []
        
        # Rule Toggles
        self.wide_gives_runs = True
        self.wide_counts_as_ball = False
        self.noball_gives_runs = True
        self.noball_rebowled = True
        self.last_man_can_play = False
        
        self.batting_team_name = ""
        self.bowling_team_name = ""
        self.toss_winner = ""
        
        self.is_resumed = False
        
        self.state = MatchState()
        self.undo_stack = []
    
    def init_players(self):
        self.state.team1_stats = [PlayerStats(name=name) for name in self.team1_players]
        self.state.team2_stats = [PlayerStats(name=name) for name in self.team2_players]
    
    def get_batting_stats(self) -> List[PlayerStats]:
        return (self.state.team1_stats if self.batting_team_name == self.team1_name 
                else self.state.team2_stats)
    
    def get_bowling_stats(self) -> List[PlayerStats]:
        return (self.state.team2_stats if self.batting_team_name == self.team1_name 
                else self.state.team1_stats)
    
    def get_rules_summary(self) -> str:
        """
        Return formatted rules summary
        
        This displays user-configurable rules.
        Wicket legality on no-balls is handled separately in code (see process_delivery)
        """
        lines = [
            f"Overs: {self.overs}",
            f"Players per team: {self.players_per_team}",
            "",
            "Wide ball rules:",
            f"  • Gives run: {'Yes' if self.wide_gives_runs else 'No'}",
            f"  • Counts as ball: {'Yes' if self.wide_counts_as_ball else 'No'}",
            "",
            "No-ball rules:",
            f"  • Gives run: {'Yes' if self.noball_gives_runs else 'No'}",
            f"  • Re-bowled: {'Yes' if self.noball_rebowled else 'No'}",
            f"  • Wickets allowed: All (gully rules)",
            "",
            f"Last man can play: {'Yes' if self.last_man_can_play else 'No'}",
        ]
        return "\n".join(lines)
    
    def save_snapshot(self):
        self.undo_stack.append(copy.deepcopy(self.state))
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)
    
    def undo(self) -> bool:
        """
        Undo restrictions to prevent corruption
        
        RULES:
        1. Cannot undo after innings break (undo_stack cleared at break)
        2. Can undo after resume (within same innings)
        3. Cannot undo across app restarts (stack not persisted)
        """
        if self.undo_stack:
            self.state = self.undo_stack.pop()
            self.persist_to_disk()
            return True
        return False
    
    def is_solo_batting(self) -> bool:
        """
        Returns True if only one batsman can bat (last man scenario)
        
        LOGIC CLARIFICATION:
        - If last_man_can_play = False: innings ends at (players-1) wickets
        - If last_man_can_play = True: solo batting starts at (players-1) wickets,
          innings ends at (players) wickets
        
        Example with 6 players:
        - Normal rules: ends at 5 wickets (6th player can't bat alone)
        - Last man can play: solo batting at 5 wickets, ends at 6 wickets
        """
        if not self.last_man_can_play:
            return False
        
        # Solo batting active when (players - 1) wickets have fallen
        return self.state.wickets == self.players_per_team - 1
    
    def get_max_wickets_for_innings_end(self) -> int:
        """
        Returns the wicket count at which innings MUST end
        
        This is the source of truth for all-out conditions
        - Normal rules: (players - 1) wickets = all out
        - Last man can play: (players) wickets = all out
        """
        if self.last_man_can_play:
            return self.players_per_team  # All players must be out
        else:
            return self.players_per_team - 1  # Last pair broken
    
    def process_delivery(self, runs_scored: int, is_wide=False, is_noball=False, 
                        is_wicket=False, runs_from_extra=0):
        """
        Process a single delivery with full rule compliance
        
        CRITICAL RULES:
        1. NO-BALL WICKETS: Only run-outs are legal on no-balls
           - This implementation treats is_wicket as "any dismissal"
           - In real cricket, bowled/caught/LBW illegal on no-ball
           - For gully cricket simplicity: we allow all wickets but document this
        
        2. SOLO BATTING: When last man is in, no more wickets possible
           - Wicket ends innings immediately
           - No strike rotation
        
        3. WIDE BALL: Batsman cannot be out (except run-out in real cricket)
           - Current implementation: wicket not expected on wide
        """
        self.save_snapshot()
        
        if is_wicket:
            # If already in solo batting, this wicket ends the innings
            if self.is_solo_batting():
                self.state.wickets += 1
                # Ball history for innings-ending wicket
                self.state.ball_history.append("W")
                if len(self.state.ball_history) > 100:
                    self.state.ball_history = self.state.ball_history[-100:]
                self.persist_to_disk()
                return  # Innings over, no further processing
            
        
        # Calculate runs
        extra_runs = 0
        if is_wide and self.wide_gives_runs:
            extra_runs += 1
        if is_noball and self.noball_gives_runs:
            extra_runs += 1
        
        extra_runs += runs_from_extra
        total_runs = runs_scored + extra_runs
        
        self.state.score += total_runs
        self.state.extras += extra_runs
        
        # Legal ball check
        is_legal = True
        if is_wide and not self.wide_counts_as_ball:
            is_legal = False
        if is_noball and self.noball_rebowled:
            is_legal = False
        
        if is_legal:
            self.state.legal_balls += 1
        
        # Update batsman
        bat_stats = self.get_batting_stats()
        striker = bat_stats[self.state.striker_idx]
        
        if not is_wide:
            if is_legal or is_noball:
                striker.balls_faced += 1
            striker.runs += runs_scored
            if runs_scored == 4:
                striker.fours += 1
            elif runs_scored == 6:
                striker.sixes += 1
        
        # Update bowler
        bowl_stats = self.get_bowling_stats()
        bowler = bowl_stats[self.state.bowler_idx]
        
        bowler.runs_conceded += total_runs
        if is_legal:
            bowler.legal_balls_bowled += 1
        if is_wicket:
            bowler.wickets += 1
        
        # Handle wicket
        if is_wicket:
            self.state.wickets += 1
            next_idx = max(self.state.striker_idx, self.state.non_striker_idx) + 1
            if next_idx < len(bat_stats):
                self.state.striker_idx = next_idx
        
        # Strike rotation - check current state after wicket processing
        solo = self.is_solo_batting()
        
        if not is_wicket and not solo and runs_scored % 2 != 0:
            self.state.striker_idx, self.state.non_striker_idx = \
                self.state.non_striker_idx, self.state.striker_idx
        
        # End of over rotation - skip if solo batting
        if is_legal and self.state.legal_balls % 6 == 0 and not solo:
            self.state.striker_idx, self.state.non_striker_idx = \
                self.state.non_striker_idx, self.state.striker_idx
        
        # Ball history 
        if is_wicket:
            hist = "W"
        elif is_wide:
            hist = f"Wd{'+'+str(runs_scored+runs_from_extra) if (runs_scored+runs_from_extra) > 0 else ''}"
        elif is_noball:
            hist = f"Nb{'+'+str(runs_scored+runs_from_extra) if (runs_scored+runs_from_extra) > 0 else ''}"
        else:
            hist = str(runs_scored)
        
        self.state.ball_history.append(hist)
        
        if len(self.state.ball_history) > 100:
            self.state.ball_history = self.state.ball_history[-100:]
        
        self.persist_to_disk()
    
    def change_bowler(self, new_bowler_idx: int):
        self.state.bowler_idx = new_bowler_idx
        self.persist_to_disk()
    
    def persist_to_disk(self):
        innings1_dict = None
        innings2_dict = None
        
        if self.state.innings1_data:
            innings1_dict = asdict(self.state.innings1_data)
        if self.state.innings2_data:
            innings2_dict = asdict(self.state.innings2_data)
        
        data = {
            'setup': {
                't1_name': self.team1_name,
                't2_name': self.team2_name,
                't1_players': self.team1_players,
                't2_players': self.team2_players,
                'overs': self.overs,
                'players': self.players_per_team,
                'batting': self.batting_team_name,
                'bowling': self.bowling_team_name,
                'toss_winner': self.toss_winner,
                'wd_runs': self.wide_gives_runs,
                'wd_ball': self.wide_counts_as_ball,
                'nb_runs': self.noball_gives_runs,
                'nb_rebowl': self.noball_rebowled,
                'last_man': self.last_man_can_play,
            },
            'state': {
                'score': self.state.score,
                'wickets': self.state.wickets,
                'legal_balls': self.state.legal_balls,
                'extras': self.state.extras,
                'striker_idx': self.state.striker_idx,
                'non_striker_idx': self.state.non_striker_idx,
                'bowler_idx': self.state.bowler_idx,
                'current_innings': self.state.current_innings,
                'target': self.state.target,
                'innings1_data': innings1_dict,
                'innings2_data': innings2_dict,
                'ball_history': self.state.ball_history,
                'team1_stats': [asdict(p) for p in self.state.team1_stats],
                'team2_stats': [asdict(p) for p in self.state.team2_stats],
            }
        }
        self.store.put('match', **data)
    
    def load_from_disk(self) -> bool:
        if not self.store.exists('match'):
            return False
        
        try:
            data = self.store.get('match')
            
            s = data['setup']
            self.team1_name = s['t1_name']
            self.team2_name = s['t2_name']
            self.team1_players = s['t1_players']
            self.team2_players = s['t2_players']
            self.overs = s['overs']
            self.players_per_team = s['players']
            self.batting_team_name = s['batting']
            self.bowling_team_name = s['bowling']
            self.toss_winner = s.get('toss_winner', '')
            
            self.wide_gives_runs = s.get('wd_runs', True)
            self.wide_counts_as_ball = s.get('wd_ball', False)
            self.noball_gives_runs = s.get('nb_runs', True)
            self.noball_rebowled = s.get('nb_rebowl', True)
            self.last_man_can_play = s.get('last_man', False)
            
            st = data['state']
            
            innings1_data = None
            innings2_data = None
            
            if st.get('innings1_data'):
                innings1_data = InningsData(**st['innings1_data'])
            if st.get('innings2_data'):
                innings2_data = InningsData(**st['innings2_data'])
            
            self.state = MatchState(
                score=st['score'],
                wickets=st['wickets'],
                legal_balls=st['legal_balls'],
                extras=st.get('extras', 0),
                striker_idx=st['striker_idx'],
                non_striker_idx=st['non_striker_idx'],
                bowler_idx=st['bowler_idx'],
                current_innings=st['current_innings'],
                target=st.get('target'),
                innings1_data=innings1_data,
                innings2_data=innings2_data,
                ball_history=st.get('ball_history', []),
            )
            
            self.state.team1_stats = [PlayerStats(**p) for p in st['team1_stats']]
            self.state.team2_stats = [PlayerStats(**p) for p in st['team2_stats']]
            
            self.is_resumed = True
            
            return True
        except Exception as e:
            print(f"Load error: {e}")
            return False
    
    def clear_save(self):
        if self.store.exists('match'):
            self.store.delete('match')
        self.is_resumed = False

mgr = MatchManager()

# --- UI Screens ---

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        title = Label(text='Score247\nGully Cricket', font_size='36sp',
                     size_hint_y=0.35, bold=True, color=(1, 0.85, 0.2, 1))
        layout.add_widget(title)
        
        btn_new = Button(text='New Match', size_hint_y=0.15,
                        background_color=(0.2, 0.7, 0.3, 1), font_size='18sp')
        btn_new.bind(on_press=self.new_match)
        layout.add_widget(btn_new)
        
        btn_resume = Button(text='Resume Match', size_hint_y=0.15,
                           background_color=(0.3, 0.5, 0.8, 1), font_size='18sp')
        btn_resume.bind(on_press=self.resume_match)
        layout.add_widget(btn_resume)
        
        layout.add_widget(Label(size_hint_y=0.35))
        self.add_widget(layout)
    
    def new_match(self, instance):
        mgr.reset_config()
        self.manager.current = 'setup'
    
    def resume_match(self, instance):
        if mgr.load_from_disk():
            Popup(title='Match Resumed',
                 content=Label(text=f'Continuing saved match\nInnings {mgr.state.current_innings}'),
                 size_hint=(0.7, 0.3), auto_dismiss=True).open()
            self.manager.current = 'scoring'
        else:
            Popup(title='No Match Found',
                 content=Label(text='Start a new match first'),
                 size_hint=(0.7, 0.3)).open()

class SetupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        main = BoxLayout(orientation='vertical', padding=10, spacing=8)
        
        main.add_widget(Label(text='Match Setup', font_size='24sp',
                             bold=True, size_hint_y=0.08))
        
        scroll = ScrollView(size_hint_y=0.77)
        grid = GridLayout(cols=2, spacing=8, size_hint_y=None,
                         row_default_height=45, row_force_default=True)
        grid.bind(minimum_height=grid.setter('height'))
        
        grid.add_widget(Label(text='Team 1:', halign='right'))
        self.t1_input = TextInput(text='Team A', multiline=False)
        grid.add_widget(self.t1_input)
        
        grid.add_widget(Label(text='Team 2:', halign='right'))
        self.t2_input = TextInput(text='Team B', multiline=False)
        grid.add_widget(self.t2_input)
        
        grid.add_widget(Label(text='Overs:', halign='right'))
        self.overs_input = TextInput(text='5', input_filter='int', multiline=False)
        grid.add_widget(self.overs_input)
        
        grid.add_widget(Label(text='Players/Team:', halign='right'))
        self.players_input = TextInput(text='6', input_filter='int', multiline=False)
        grid.add_widget(self.players_input)
        
        grid.add_widget(Label(text='Wide gives run:', halign='right'))
        self.wd_run = ToggleButton(text='YES', state='down')
        grid.add_widget(self.wd_run)
        
        grid.add_widget(Label(text='Wide counts as ball:', halign='right'))
        self.wd_ball = ToggleButton(text='NO', state='normal')
        grid.add_widget(self.wd_ball)
        
        grid.add_widget(Label(text='No-ball gives run:', halign='right'))
        self.nb_run = ToggleButton(text='YES', state='down')
        grid.add_widget(self.nb_run)
        
        grid.add_widget(Label(text='No-ball re-bowled:', halign='right'))
        self.nb_rebowl = ToggleButton(text='YES', state='down')
        grid.add_widget(self.nb_rebowl)
        
        grid.add_widget(Label(text='Last man can play:', halign='right'))
        self.last_man = ToggleButton(text='NO', state='normal')
        grid.add_widget(self.last_man)
        
        scroll.add_widget(grid)
        main.add_widget(scroll)
        
        btn = Button(text='Next: Player Names', size_hint_y=0.12,
                    background_color=(0.2, 0.7, 0.3, 1), font_size='18sp')
        btn.bind(on_press=self.validate_and_next)
        main.add_widget(btn)
        
        self.add_widget(main)
    
    def validate_and_next(self, instance):
        try:
            overs = int(self.overs_input.text)
            players = int(self.players_input.text)
            
            if overs < 1 or overs > 50:
                raise ValueError("Overs: 1-50")
            if players < 2 or players > 11:
                raise ValueError("Players: 2-11")
            
            mgr.team1_name = self.t1_input.text.strip() or "Team A"
            mgr.team2_name = self.t2_input.text.strip() or "Team B"
            mgr.overs = overs
            mgr.players_per_team = players
            
            mgr.wide_gives_runs = (self.wd_run.state == 'down')
            mgr.wide_counts_as_ball = (self.wd_ball.state == 'down')
            mgr.noball_gives_runs = (self.nb_run.state == 'down')
            mgr.noball_rebowled = (self.nb_rebowl.state == 'down')
            mgr.last_man_can_play = (self.last_man.state == 'down')
            
            self.manager.current = 'players'
            
        except ValueError as e:
            Popup(title='Invalid', content=Label(text=str(e)),
                 size_hint=(0.7, 0.3)).open()

class PlayerNamesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_enter(self):
        self.clear_widgets()
        self.build_ui()
    
    def build_ui(self):
        main = BoxLayout(orientation='vertical', padding=10, spacing=8)
        
        main.add_widget(Label(text='Enter Player Names', font_size='22sp',
                             bold=True, size_hint_y=0.08))
        
        scroll = ScrollView(size_hint_y=0.77)
        grid = GridLayout(cols=2, spacing=8, size_hint_y=None,
                         row_default_height=45, row_force_default=True)
        grid.bind(minimum_height=grid.setter('height'))
        
        self.t1_inputs = []
        self.t2_inputs = []
        
        grid.add_widget(Label(text=mgr.team1_name, bold=True))
        grid.add_widget(Label(text=mgr.team2_name, bold=True))
        
        for i in range(mgr.players_per_team):
            t1_in = TextInput(text=f'Player {i+1}', multiline=False)
            t2_in = TextInput(text=f'Player {i+1}', multiline=False)
            
            self.t1_inputs.append(t1_in)
            self.t2_inputs.append(t2_in)
            
            grid.add_widget(t1_in)
            grid.add_widget(t2_in)
        
        scroll.add_widget(grid)
        main.add_widget(scroll)
        
        btn = Button(text='Next: Toss', size_hint_y=0.12,
                    background_color=(0.2, 0.7, 0.3, 1), font_size='18sp')
        btn.bind(on_press=self.save_and_next)
        main.add_widget(btn)
        
        self.add_widget(main)
    
    def save_and_next(self, instance):
        mgr.team1_players = [inp.text.strip() or f'Player {i+1}' 
                            for i, inp in enumerate(self.t1_inputs)]
        mgr.team2_players = [inp.text.strip() or f'Player {i+1}' 
                            for i, inp in enumerate(self.t2_inputs)]
        
        mgr.init_players()
        self.manager.current = 'toss'

class TossScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.winner = None
    
    def on_enter(self):
        self.clear_widgets()
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        self.lbl = Label(text='Time for the Toss!', font_size='26sp',
                        size_hint_y=0.25, bold=True)
        layout.add_widget(self.lbl)
        
        self.btn_toss = Button(text='FLIP COIN', size_hint_y=0.15,
                              background_color=(0.9, 0.7, 0.2, 1), font_size='20sp')
        self.btn_toss.bind(on_press=self.do_toss)
        layout.add_widget(self.btn_toss)
        
        self.choice_box = BoxLayout(spacing=10, size_hint_y=0.15)
        layout.add_widget(self.choice_box)
        
        layout.add_widget(Label(size_hint_y=0.45))
        self.add_widget(layout)
    
    def do_toss(self, instance):
        self.winner = random.choice([mgr.team1_name, mgr.team2_name])
        mgr.toss_winner = self.winner
        
        self.lbl.text = f'{self.winner} Won!\nChoose:'
        self.btn_toss.disabled = True
        
        btn_bat = Button(text='BAT', background_color=(0.2, 0.7, 0.3, 1))
        btn_bat.bind(on_press=lambda x: self.set_choice('bat'))
        
        btn_bowl = Button(text='BOWL', background_color=(0.7, 0.3, 0.2, 1))
        btn_bowl.bind(on_press=lambda x: self.set_choice('bowl'))
        
        self.choice_box.add_widget(btn_bat)
        self.choice_box.add_widget(btn_bowl)
    
    def set_choice(self, choice):
        if choice == 'bat':
            mgr.batting_team_name = self.winner
            mgr.bowling_team_name = (mgr.team2_name if self.winner == mgr.team1_name 
                                    else mgr.team1_name)
        else:
            mgr.bowling_team_name = self.winner
            mgr.batting_team_name = (mgr.team2_name if self.winner == mgr.team1_name 
                                    else mgr.team1_name)
        
        self.manager.current = 'rules_summary'

class RulesSummaryScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(Label(text='Match Rules', font_size='24sp',
                               bold=True, size_hint_y=0.12))
        
        rules_text = mgr.get_rules_summary()
        
        layout.add_widget(Label(text=rules_text, font_size='16sp',
                               size_hint_y=0.68, halign='left', valign='top',
                               text_size=(Window.width - 60, None)))
        
        btn = Button(text='START MATCH', size_hint_y=0.15,
                    background_color=(0.2, 0.7, 0.3, 1), font_size='20sp')
        btn.bind(on_press=self.start_match)
        layout.add_widget(btn)
        
        self.add_widget(layout)
    
    def start_match(self, instance):
        self.manager.current = 'scoring'

class ScoringScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=5, spacing=5)
        
        # Scoreboard
        self.score_lbl = Label(text='0/0 (0.0)', font_size='44sp',
                              bold=True, size_hint_y=0.14, color=(1, 0.9, 0.3, 1))
        layout.add_widget(self.score_lbl)
        
        # Info
        self.info_lbl = Label(text='', font_size='15sp', size_hint_y=0.07,
                             color=(0.8, 0.8, 0.8, 1))
        layout.add_widget(self.info_lbl)
        
        # Players
        self.players_lbl = Label(text='', font_size='14sp', size_hint_y=0.08,
                                color=(0.7, 0.9, 0.7, 1))
        layout.add_widget(self.players_lbl)
        
        # Run buttons
        runs_grid = GridLayout(cols=4, spacing=5, size_hint_y=0.22)
        
        for r in [0, 1, 2, 3, 4, 5, 6]:
            btn = Button(text=str(r), background_color=(0.2, 0.5, 0.9, 1), font_size='22sp')
            btn.bind(on_press=lambda x, run=r: self.add_runs(run))
            runs_grid.add_widget(btn)
        
        btn_out = Button(text='OUT', background_color=(0.9, 0.2, 0.2, 1),
                        font_size='20sp', bold=True)
        btn_out.bind(on_press=lambda x: self.add_runs(0, is_wicket=True))
        runs_grid.add_widget(btn_out)
        
        layout.add_widget(runs_grid)
        
        extras_box = BoxLayout(spacing=5, size_hint_y=0.11)
        
        btn_wd = Button(text='WIDE', background_color=(0.8, 0.6, 0.2, 1))
        btn_wd.bind(on_press=self.handle_wide)
        
        btn_nb = Button(text='NO BALL', background_color=(0.8, 0.6, 0.2, 1))
        btn_nb.bind(on_press=self.handle_noball)
        
        extras_box.add_widget(btn_wd)
        extras_box.add_widget(btn_nb)
        layout.add_widget(extras_box)
        
        # Controls
        ctrl_box = BoxLayout(spacing=5, size_hint_y=0.11)
        
        btn_undo = Button(text='UNDO', background_color=(0.5, 0.5, 0.5, 1), font_size='16sp')
        btn_undo.bind(on_press=self.do_undo)
        
        btn_bowler = Button(text='BOWLER', background_color=(0.4, 0.6, 0.5, 1), font_size='16sp')
        btn_bowler.bind(on_press=self.change_bowler)
        
        btn_rules = Button(text='RULES', background_color=(0.5, 0.5, 0.6, 1), font_size='16sp')
        btn_rules.bind(on_press=self.show_rules)
        
        btn_end = Button(text='END', background_color=(0.7, 0.3, 0.3, 1), font_size='16sp')
        btn_end.bind(on_press=self.end_innings_manual)
        
        ctrl_box.add_widget(btn_undo)
        ctrl_box.add_widget(btn_bowler)
        ctrl_box.add_widget(btn_rules)
        ctrl_box.add_widget(btn_end)
        layout.add_widget(ctrl_box)
        
        # History
        self.history_lbl = Label(text='', font_size='16sp', size_hint_y=0.27,
                                color=(0.9, 0.9, 0.9, 1))
        layout.add_widget(self.history_lbl)
        
        self.add_widget(layout)
    
    def on_enter(self):
        self.update_display()
    
    def add_runs(self, runs, is_wicket=False):
        mgr.process_delivery(runs, is_wicket=is_wicket)
        self.update_display()
        self.check_auto_end()
    
    def handle_wide(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text='Runs from wide (batsman):', size_hint_y=0.3))
        
        runs_input = TextInput(text='0', input_filter='int', multiline=False,
                              size_hint_y=0.3, font_size='20sp')
        content.add_widget(runs_input)
        
        btn_box = BoxLayout(spacing=8, size_hint_y=0.35)
        btn_cancel = Button(text='CANCEL', background_color=(0.5, 0.5, 0.5, 1))
        btn_ok = Button(text='OK', background_color=(0.2, 0.7, 0.3, 1))
        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_ok)
        content.add_widget(btn_box)
        
        popup = Popup(title='Wide Ball', content=content, size_hint=(0.75, 0.4),
                     auto_dismiss=False)
        
        def on_ok(instance):
            try:
                runs = int(runs_input.text) if runs_input.text else 0
                runs = max(0, min(runs, 6))  # UX: Clamp to valid range
                mgr.process_delivery(runs, is_wide=True)
                self.update_display()
                self.check_auto_end()
            except:
                pass
            popup.dismiss()
        
        btn_ok.bind(on_press=on_ok)
        btn_cancel.bind(on_press=popup.dismiss)
        popup.open()
    
    def handle_noball(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text='Runs scored (by batsman):', size_hint_y=0.3))
        
        runs_input = TextInput(text='0', input_filter='int', multiline=False,
                              size_hint_y=0.3, font_size='20sp')
        content.add_widget(runs_input)
        
        btn_box = BoxLayout(spacing=8, size_hint_y=0.35)
        btn_cancel = Button(text='CANCEL', background_color=(0.5, 0.5, 0.5, 1))
        btn_ok = Button(text='OK', background_color=(0.2, 0.7, 0.3, 1))
        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_ok)
        content.add_widget(btn_box)
        
        popup = Popup(title='No Ball', content=content, size_hint=(0.75, 0.4),
                     auto_dismiss=False)
        
        def on_ok(instance):
            try:
                runs = int(runs_input.text) if runs_input.text else 0
                runs = max(0, min(runs, 6))  # UX: Clamp to valid range
                mgr.process_delivery(runs, is_noball=True)
                self.update_display()
                self.check_auto_end()
            except:
                pass
            popup.dismiss()
        
        btn_ok.bind(on_press=on_ok)
        btn_cancel.bind(on_press=popup.dismiss)
        popup.open()
    
    def do_undo(self, instance):

        if not mgr.undo_stack:
            Popup(title='Cannot Undo',
                 content=Label(text='No actions to undo.\n\nNote: Undo cleared after innings break.'),
                 size_hint=(0.7, 0.35)).open()
            return
        
        if mgr.undo():
            self.update_display()
        else:
            Popup(title='Undo Failed',
                 content=Label(text='Unable to undo.'),
                 size_hint=(0.6, 0.3)).open()
    
    def change_bowler(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=5)
        content.add_widget(Label(text='Select Bowler:', size_hint_y=0.2))
        
        scroll = ScrollView(size_hint_y=0.6)
        btn_box = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        btn_box.bind(minimum_height=btn_box.setter('height'))
        
        bowl_stats = mgr.get_bowling_stats()
        for i, player in enumerate(bowl_stats):
            btn = Button(text=f'{player.name}', size_hint_y=None, height=50)
            btn.bind(on_press=lambda x, idx=i: self.select_bowler(idx, popup))
            btn_box.add_widget(btn)
        
        scroll.add_widget(btn_box)
        content.add_widget(scroll)
        
        popup = Popup(title='Change Bowler', content=content, size_hint=(0.7, 0.6))
        popup.open()
    
    def select_bowler(self, idx, popup):
        mgr.change_bowler(idx)
        popup.dismiss()
        self.update_display()
    
    def show_rules(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        rules_text = mgr.get_rules_summary()
        content.add_widget(Label(text=rules_text, size_hint_y=0.8,
                                halign='left', valign='top',
                                text_size=(Window.width - 60, None)))
        
        btn = Button(text='Close', size_hint_y=0.15)
        content.add_widget(btn)
        
        popup = Popup(title='Match Rules', content=content, size_hint=(0.8, 0.6))
        btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def update_display(self):
        s = mgr.state
        
        ov = s.legal_balls // 6
        bl = s.legal_balls % 6
        
        self.score_lbl.text = f"{mgr.batting_team_name}\n{s.score}/{s.wickets} ({ov}.{bl})"
        
        info = f"Innings {s.current_innings}"
        if s.target:
            need = s.target - s.score
            rem_balls = (mgr.overs * 6) - s.legal_balls
            if rem_balls > 0:
                rrr = (need / (rem_balls / 6))
                info += f" | Need {need} in {rem_balls} (RRR: {rrr:.2f})"
            else:
                info += f" | Need {need} runs"
        
        self.info_lbl.text = info
        
        # Players info
        bat_stats = mgr.get_batting_stats()
        bowl_stats = mgr.get_bowling_stats()
        
        striker = bat_stats[s.striker_idx]
        
        if mgr.is_solo_batting():
            self.players_lbl.text = (f"Bat: {striker.name}* ({striker.runs}) [SOLO] | "
                                    f"Bowl: {bowl_stats[s.bowler_idx].name}")
        else:
            non_striker = bat_stats[s.non_striker_idx]
            self.players_lbl.text = (f"Bat: {striker.name}* ({striker.runs}), "
                                    f"{non_striker.name} ({non_striker.runs}) | "
                                    f"Bowl: {bowl_stats[s.bowler_idx].name}")
        
        # History
        hist = " ".join(s.ball_history[-18:])
        self.history_lbl.text = f"Recent:\n{hist}"
    
    def check_auto_end(self):
        s = mgr.state
        
        max_wickets = mgr.get_max_wickets_for_innings_end()
        
        # Check all-out condition
        if s.wickets >= max_wickets:
            self.handle_innings_break()
            return
        
        # Check overs completed
        if s.legal_balls >= mgr.overs * 6:
            self.handle_innings_break()
            return
        
        # Check target chased
        if s.target and s.score >= s.target:
            self.manager.current = 'result'
    
    def end_innings_manual(self, instance):

        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        content.add_widget(Label(
            text='End this innings?\n\nThis cannot be undone.',
            font_size='16sp',
            size_hint_y=0.6
        ))
        
        btn_box = BoxLayout(spacing=10, size_hint_y=0.35)
        
        btn_yes = Button(text='YES, END', background_color=(0.9, 0.3, 0.3, 1))
        btn_no = Button(text='CANCEL', background_color=(0.4, 0.6, 0.5, 1))
        
        btn_box.add_widget(btn_no)
        btn_box.add_widget(btn_yes)
        content.add_widget(btn_box)
        
        popup = Popup(title='Confirm End Innings', content=content, 
                     size_hint=(0.75, 0.35))
        
        btn_yes.bind(on_press=lambda x: self.confirm_end_innings(popup))
        btn_no.bind(on_press=popup.dismiss)
        
        popup.open()
    
    def confirm_end_innings(self, popup):
        """Actually end the innings after confirmation"""
        popup.dismiss()
        self.handle_innings_break()
    
    def handle_innings_break(self):
        s = mgr.state
        
        if s.current_innings == 1:
            mgr.state.innings1_data = InningsData(
                score=s.score,
                wickets=s.wickets,
                legal_balls=s.legal_balls,
                extras=s.extras
            )
            
            # Clear undo stack to prevent cross-innings corruption
            # This ensures no undo can go back to innings 1 from innings 2
            mgr.undo_stack = []
            
            s.target = s.score + 1
            s.current_innings = 2
            
            # Reset innings 2 batting state
            s.score = 0
            s.wickets = 0
            s.legal_balls = 0
            s.extras = 0
            s.ball_history = []
            s.striker_idx = 0
            s.non_striker_idx = 1
            s.bowler_idx = 0
            
            # Bowling stats are NOT reset (per-match cumulative)
            # Batting stats for innings 2 team start fresh automatically
            
            mgr.batting_team_name, mgr.bowling_team_name = \
                mgr.bowling_team_name, mgr.batting_team_name
            
            mgr.persist_to_disk()
            
            Popup(title='Innings Break',
                 content=Label(text=f'Target: {s.target}\nSwap sides!'),
                 size_hint=(0.7, 0.4), auto_dismiss=True).open()
            
            self.update_display()
        else:
            mgr.state.innings2_data = InningsData(
                score=s.score,
                wickets=s.wickets,
                legal_balls=s.legal_balls,
                extras=s.extras
            )
            mgr.persist_to_disk()
            self.manager.current = 'result'

class ResultScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        s = mgr.state
        
        # Determine winner
        winner_text = "Match Drawn"
        winner_color = (0.8, 0.8, 0.8, 1)
        
        if s.target:
            if s.score >= s.target:
                winner_text = f"{mgr.batting_team_name} Wins!"
                winner_color = (0.2, 1, 0.2, 1)
            elif s.score == s.target - 1:
                winner_text = "Match Tied!"
                winner_color = (1, 0.8, 0.2, 1)
            else:
                winner_text = f"{mgr.bowling_team_name} Wins!"
                winner_color = (0.2, 1, 0.2, 1)
        
        layout.add_widget(Label(text='MATCH COMPLETE', font_size='24sp',
                               bold=True, size_hint_y=0.15))
        
        layout.add_widget(Label(text=winner_text, font_size='32sp',
                               color=winner_color, size_hint_y=0.2, bold=True))
        
        # Scores summary
        score_text = self.get_score_summary()
        layout.add_widget(Label(text=score_text, font_size='18sp', size_hint_y=0.15))
        
        # Player of match
        pom, pom_reason = self.get_player_of_match()
        layout.add_widget(Label(text=f'Player of Match:\n{pom}\n{pom_reason}',
                               font_size='16sp', size_hint_y=0.15,
                               color=(1, 0.8, 0.3, 1)))
        
        # Buttons
        btn_box = BoxLayout(spacing=10, size_hint_y=0.15)
        
        btn_stats = Button(text='View Stats', background_color=(0.4, 0.6, 0.5, 1))
        btn_stats.bind(on_press=self.show_stats)
        
        btn_new = Button(text='New Match', background_color=(0.2, 0.7, 0.3, 1))
        btn_new.bind(on_press=self.new_match)
        
        btn_home = Button(text='Home', background_color=(0.5, 0.5, 0.7, 1))
        btn_home.bind(on_press=self.go_home)
        
        btn_box.add_widget(btn_stats)
        btn_box.add_widget(btn_new)
        btn_box.add_widget(btn_home)
        
        layout.add_widget(btn_box)
        layout.add_widget(Label(size_hint_y=0.2))
        
        self.add_widget(layout)
    
    def get_score_summary(self):
        s = mgr.state
        
        # Determine which team batted first
        if mgr.batting_team_name == mgr.team1_name:
            inn1_team = mgr.team2_name
            inn2_team = mgr.team1_name
        else:
            inn1_team = mgr.team1_name
            inn2_team = mgr.team2_name
        
        # Use stored innings data
        if s.innings1_data:
            inn1_text = f"{inn1_team}: {s.innings1_data.score}/{s.innings1_data.wickets} ({s.innings1_data.overs_str()})"
        else:
            inn1_text = f"{inn1_team}: Data not available"
        
        if s.innings2_data:
            inn2_text = f"{inn2_team}: {s.innings2_data.score}/{s.innings2_data.wickets} ({s.innings2_data.overs_str()})"
        else:
            # Current innings data
            inn2_text = f"{inn2_team}: {s.score}/{s.wickets} ({s.legal_balls//6}.{s.legal_balls%6})"
        
        return f"{inn1_text}\n{inn2_text}"
    
    def get_player_of_match(self):
        """
        Player of Match Formula:
        - Runs: 1 point per run
        - Strike rate bonus: +0.5 per run if SR > 150 (min 10 balls)
        - Wickets: 25 points per wicket
        - Economy bonus: +10 if economy < 6 (min 2 overs)
        
        Deterministic - highest score wins
        """
        all_players = mgr.state.team1_stats + mgr.state.team2_stats
        
        best_player = None
        best_score = -1
        best_reason = ""
        
        for p in all_players:
            if p.balls_faced == 0 and p.legal_balls_bowled == 0:
                continue
            
            score = 0
            reasons = []
            
            # Batting contribution
            if p.runs > 0:
                score += p.runs
                reasons.append(f"{p.runs} runs")
                
                if p.balls_faced >= 10 and p.strike_rate() > 150:
                    bonus = p.runs * 0.5
                    score += bonus
                    reasons.append(f"SR {p.strike_rate():.1f}")
            
            # Bowling contribution
            if p.wickets > 0:
                wicket_points = p.wickets * 25
                score += wicket_points
                reasons.append(f"{p.wickets} wkts")
                
                overs = p.legal_balls_bowled / 6
                if overs >= 2 and p.economy() < 6:
                    score += 10
                    reasons.append(f"eco {p.economy():.1f}")
            
            if score > best_score:
                best_score = score
                best_player = p
                best_reason = ", ".join(reasons)
        
        if best_player:
            return best_player.name, best_reason
        else:
            return "No outstanding performance", ""
    
    def show_stats(self, instance):
        self.manager.current = 'stats'
    
    def new_match(self, instance):
        mgr.reset_config()
        mgr.clear_save()
        self.manager.current = 'setup'
    
    def go_home(self, instance):
        mgr.clear_save()
        self.manager.current = 'home'

class StatsScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        self.build_ui()
    
    def build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        layout.add_widget(Label(text='Match Statistics', font_size='24sp',
                               bold=True, size_hint_y=0.1))
        
        scroll = ScrollView(size_hint_y=0.75)
        stats_layout = BoxLayout(orientation='vertical', spacing=10,
                                size_hint_y=None)
        stats_layout.bind(minimum_height=stats_layout.setter('height'))
        
        # Team 1 batting stats
        stats_layout.add_widget(Label(
            text=f'[b]{mgr.team1_name} - Batting[/b]',
            markup=True, size_hint_y=None, height=35,
            color=(0.3, 0.8, 1, 1)
        ))
        
        for p in mgr.state.team1_stats:
            if p.balls_faced > 0:
                txt = f"{p.name}: {p.runs}({p.balls_faced})"
                if p.fours > 0 or p.sixes > 0:
                    txt += f" [{p.fours}x4, {p.sixes}x6]"
                txt += f" SR: {p.strike_rate():.1f}"
                stats_layout.add_widget(Label(text=txt, size_hint_y=None, height=30))
        
        # Team 1 bowling stats
        stats_layout.add_widget(Label(
            text=f'[b]{mgr.team1_name} - Bowling[/b]',
            markup=True, size_hint_y=None, height=35,
            color=(0.3, 0.8, 1, 1)
        ))
        
        for p in mgr.state.team1_stats:
            if p.legal_balls_bowled > 0:
                overs = p.legal_balls_bowled // 6
                balls = p.legal_balls_bowled % 6
                txt = f"{p.name}: {p.wickets}/{p.runs_conceded} in {overs}.{balls} ov"
                txt += f" Eco: {p.economy():.1f}"
                stats_layout.add_widget(Label(text=txt, size_hint_y=None, height=30))
        
        stats_layout.add_widget(Label(text='', size_hint_y=None, height=20))
        
        # Team 2 batting stats
        stats_layout.add_widget(Label(
            text=f'[b]{mgr.team2_name} - Batting[/b]',
            markup=True, size_hint_y=None, height=35,
            color=(1, 0.8, 0.3, 1)
        ))
        
        for p in mgr.state.team2_stats:
            if p.balls_faced > 0:
                txt = f"{p.name}: {p.runs}({p.balls_faced})"
                if p.fours > 0 or p.sixes > 0:
                    txt += f" [{p.fours}x4, {p.sixes}x6]"
                txt += f" SR: {p.strike_rate():.1f}"
                stats_layout.add_widget(Label(text=txt, size_hint_y=None, height=30))
        
        # Team 2 bowling stats
        stats_layout.add_widget(Label(
            text=f'[b]{mgr.team2_name} - Bowling[/b]',
            markup=True, size_hint_y=None, height=35,
            color=(1, 0.8, 0.3, 1)
        ))
        
        for p in mgr.state.team2_stats:
            if p.legal_balls_bowled > 0:
                overs = p.legal_balls_bowled // 6
                balls = p.legal_balls_bowled % 6
                txt = f"{p.name}: {p.wickets}/{p.runs_conceded} in {overs}.{balls} ov"
                txt += f" Eco: {p.economy():.1f}"
                stats_layout.add_widget(Label(text=txt, size_hint_y=None, height=30))
        
        scroll.add_widget(stats_layout)
        layout.add_widget(scroll)
        
        btn_back = Button(text='Back to Result', size_hint_y=0.12,
                         background_color=(0.5, 0.5, 0.7, 1), font_size='18sp')
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'result'))
        layout.add_widget(btn_back)
        
        self.add_widget(layout)

class CricketApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        self.title = 'Score247'
        
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(SetupScreen(name='setup'))
        sm.add_widget(PlayerNamesScreen(name='players'))
        sm.add_widget(TossScreen(name='toss'))
        sm.add_widget(RulesSummaryScreen(name='rules_summary'))
        sm.add_widget(ScoringScreen(name='scoring'))
        sm.add_widget(ResultScreen(name='result'))
        sm.add_widget(StatsScreen(name='stats'))
        
        return sm
        pom, pom_reason = self.get_player_of_match()
        layout.add_widget(Label(
            text=f"🏆 Player of the Match:\n{pom}\n{pom_reason}",
            font_size='18sp',
            size_hint_y=0.2,
            halign='center',
            valign='middle',
            text_size=(Window.width - 40, None)
        ))

        # Navigation buttons
        btn_box = BoxLayout(spacing=10, size_hint_y=0.15)

        btn_home = Button(text='HOME')
        btn_home.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))

        btn_new = Button(text='NEW MATCH', background_color=(0.2, 0.7, 0.3, 1))
        btn_new.bind(on_press=self.new_match)

        btn_stats = Button(text='VIEW STATS')
        btn_stats.bind(on_press=lambda x: setattr(self.manager, 'current', 'stats'))

        btn_box.add_widget(btn_home)
        btn_box.add_widget(btn_stats)
        btn_box.add_widget(btn_new)

        layout.add_widget(btn_box)
        self.add_widget(layout)

    def new_match(self, instance):
        mgr.clear_save()
        mgr.reset_config()
        self.manager.current = 'setup'

    def get_score_summary(self) -> str:
        i1 = mgr.state.innings1_data
        i2 = mgr.state.innings2_data

        lines = [
            f"{mgr.team1_name}: {i1.score}/{i1.wickets} ({i1.overs_str()})",
            f"{mgr.team2_name}: {i2.score}/{i2.wickets} ({i2.overs_str()})",
            "",
            f"Toss Winner: {mgr.toss_winner}"
        ]
        return "\n".join(lines)

    def get_player_of_match(self):
        """
        Deterministic Player of Match Formula (QA Approved)

        Score = (Runs * 1.0)
              + (Wickets * 20)
              - (Economy * 2)
        """
        best_player = None
        best_score = -999

        for p in mgr.state.team1_stats + mgr.state.team2_stats:
            score = (
                p.runs +
                (p.wickets * 20) -
                (p.economy() * 2 if p.legal_balls_bowled > 0 else 0)
            )
            if score > best_score:
                best_score = score
                best_player = p

        reason = f"Runs: {best_player.runs}, Wickets: {best_player.wickets}"
        return best_player.name, reason


class StatsScreen(Screen):
    def on_enter(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=5)

        layout.add_widget(Label(text='Match Statistics', font_size='24sp', bold=True))

        scroll = ScrollView()
        box = BoxLayout(orientation='vertical', size_hint_y=None)
        box.bind(minimum_height=box.setter('height'))

        for team_name, stats in [
            (mgr.team1_name, mgr.state.team1_stats),
            (mgr.team2_name, mgr.state.team2_stats)
        ]:
            box.add_widget(Label(text=team_name, font_size='20sp', bold=True))
            for p in stats:
                text = (
                    f"{p.name} | "
                    f"Runs: {p.runs}, "
                    f"Wkts: {p.wickets}, "
                    f"SR: {p.strike_rate():.1f}, "
                    f"Econ: {p.economy():.2f}"
                )
                box.add_widget(Label(text=text, size_hint_y=None, height=30))

        scroll.add_widget(box)
        layout.add_widget(scroll)

        btn = Button(text='BACK', size_hint_y=0.1)
        btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'result'))
        layout.add_widget(btn)

        self.add_widget(layout)


class Score247App(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(SetupScreen(name='setup'))
        sm.add_widget(PlayerNamesScreen(name='players'))
        sm.add_widget(TossScreen(name='toss'))
        sm.add_widget(RulesSummaryScreen(name='rules_summary'))
        sm.add_widget(ScoringScreen(name='scoring'))
        sm.add_widget(ResultScreen(name='result'))
        sm.add_widget(StatsScreen(name='stats'))
        return sm


if __name__ == '__main__':
    Score247App().run()
