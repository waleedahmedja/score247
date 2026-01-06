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

from ui_theme import *

# --- Data Models --- (NO CHANGES)

@dataclass
class PlayerStats:
    """Individual player statistics"""
    name: str = "Player"
    runs: int = 0
    balls_faced: int = 0
    fours: int = 0
    sixes: int = 0
    wickets: int = 0
    runs_conceded: int = 0
    legal_balls_bowled: int = 0
    
    def strike_rate(self) -> float:
        return (self.runs / self.balls_faced * 100) if self.balls_faced > 0 else 0.0
    
    def economy(self) -> float:
        overs = self.legal_balls_bowled / 6
        return (self.runs_conceded / overs) if overs > 0 else 0.0

@dataclass
class InningsData:
    """Store complete innings data"""
    score: int = 0
    wickets: int = 0
    legal_balls: int = 0
    extras: int = 0
    
    def overs_str(self) -> str:
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
    """Core match management - NO LOGIC CHANGES"""
    
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
        if self.undo_stack:
            self.state = self.undo_stack.pop()
            self.persist_to_disk()
            return True
        return False
    
    def is_solo_batting(self) -> bool:
        if not self.last_man_can_play:
            return False
        return self.state.wickets == self.players_per_team - 1
    
    def get_max_wickets_for_innings_end(self) -> int:
        if self.last_man_can_play:
            return self.players_per_team
        else:
            return self.players_per_team - 1
    
    def process_delivery(self, runs_scored: int, is_wide=False, is_noball=False, 
                        is_wicket=False, runs_from_extra=0):
        self.save_snapshot()
        
        if is_wicket:
            if self.is_solo_batting():
                self.state.wickets += 1
                self.state.ball_history.append("W")
                if len(self.state.ball_history) > 100:
                    self.state.ball_history = self.state.ball_history[-100:]
                self.persist_to_disk()
                return
        
        extra_runs = 0
        if is_wide and self.wide_gives_runs:
            extra_runs += 1
        if is_noball and self.noball_gives_runs:
            extra_runs += 1
        
        extra_runs += runs_from_extra
        total_runs = runs_scored + extra_runs
        
        self.state.score += total_runs
        self.state.extras += extra_runs
        
        is_legal = True
        if is_wide and not self.wide_counts_as_ball:
            is_legal = False
        if is_noball and self.noball_rebowled:
            is_legal = False
        
        if is_legal:
            self.state.legal_balls += 1
        
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
        
        bowl_stats = self.get_bowling_stats()
        bowler = bowl_stats[self.state.bowler_idx]
        
        bowler.runs_conceded += total_runs
        if is_legal:
            bowler.legal_balls_bowled += 1
        if is_wicket:
            bowler.wickets += 1
        
        if is_wicket:
            self.state.wickets += 1
            next_idx = max(self.state.striker_idx, self.state.non_striker_idx) + 1
            if next_idx < len(bat_stats):
                self.state.striker_idx = next_idx
        
        solo = self.is_solo_batting()
        
        if not is_wicket and not solo and runs_scored % 2 != 0:
            self.state.striker_idx, self.state.non_striker_idx = \
                self.state.non_striker_idx, self.state.striker_idx
        
        if is_legal and self.state.legal_balls % 6 == 0 and not solo:
            self.state.striker_idx, self.state.non_striker_idx = \
                self.state.non_striker_idx, self.state.striker_idx
        
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

# --- UI Screens --- (ONLY UI CHANGES)

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=PAD_LARGE, spacing=SPACE_LARGE)
        
        title = Label(
            text='Score247\nGully Cricket',
            font_size=FONT_XLARGE,
            size_hint_y=HOME_TITLE_HEIGHT,
            bold=True,
            color=TEXT_ACCENT
        )
        layout.add_widget(title)
        
        btn_new = Button(
            text='New Match',
            size_hint_y=HOME_BTN_HEIGHT,
            background_color=BTN_ACTION,
            font_size=FONT_MEDIUM,
            bold=True
        )
        btn_new.bind(on_press=self.new_match)
        layout.add_widget(btn_new)
        
        btn_resume = Button(
            text='Resume Match',
            size_hint_y=HOME_BTN_HEIGHT,
            background_color=SECONDARY,
            font_size=FONT_MEDIUM
        )
        btn_resume.bind(on_press=self.resume_match)
        layout.add_widget(btn_resume)
        
        layout.add_widget(Label(size_hint_y=HOME_SPACER_HEIGHT))
        self.add_widget(layout)

        footer = Label(
            text='Yours Truly, \n waleedahmedja',
            font_size=FONT_SMALL,
            size_hint_y=0.1,  # Takes up 10% of the vertical space
            color=TEXT_SECONDARY,
            italic=True
        )
        layout.add_widget(footer)
    
    def new_match(self, instance):
        mgr.reset_config()
        self.manager.current = 'setup'
    
    def resume_match(self, instance):
        if mgr.load_from_disk():
            Popup(
                title='Match Resumed',
                content=Label(
                    text=f'Continuing saved match\nInnings {mgr.state.current_innings}',
                    color=TEXT_PRIMARY
                ),
                size_hint=POPUP_SMALL,
                auto_dismiss=True
            ).open()
            self.manager.current = 'scoring'
        else:
            Popup(
                title='No Match Found',
                content=Label(text='Start a new match first', color=TEXT_PRIMARY),
                size_hint=POPUP_SMALL
            ).open()

class SetupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        main = BoxLayout(orientation='vertical', padding=PAD_NORMAL, spacing=SPACE_NORMAL)
        
        main.add_widget(Label(
            text='Match Setup',
            font_size=FONT_LARGE,
            bold=True,
            size_hint_y=SETUP_HEADER_HEIGHT,
            color=TEXT_PRIMARY
        ))
        
        scroll = ScrollView(size_hint_y=SETUP_FORM_HEIGHT)
        grid = GridLayout(
            cols=2,
            spacing=SPACE_NORMAL,
            size_hint_y=None,
            row_default_height=BTN_HEIGHT_NORMAL,
            row_force_default=True
        )
        grid.bind(minimum_height=grid.setter('height'))
        
        # Team names
        grid.add_widget(Label(text='Team 1:', halign='right', color=TEXT_SECONDARY))
        self.t1_input = TextInput(text='Team A', multiline=False)
        grid.add_widget(self.t1_input)
        
        grid.add_widget(Label(text='Team 2:', halign='right', color=TEXT_SECONDARY))
        self.t2_input = TextInput(text='Team B', multiline=False)
        grid.add_widget(self.t2_input)
        
        # Match settings
        grid.add_widget(Label(text='Overs:', halign='right', color=TEXT_SECONDARY))
        self.overs_input = TextInput(text='5', input_filter='int', multiline=False)
        grid.add_widget(self.overs_input)
        
        grid.add_widget(Label(text='Players/Team:', halign='right', color=TEXT_SECONDARY))
        self.players_input = TextInput(text='6', input_filter='int', multiline=False)
        grid.add_widget(self.players_input)
        
        # Rule toggles
        grid.add_widget(Label(text='Wide gives run:', halign='right', color=TEXT_SECONDARY))
        self.wd_run = ToggleButton(text='YES', state='down')
        grid.add_widget(self.wd_run)
        
        grid.add_widget(Label(text='Wide counts as ball:', halign='right', color=TEXT_SECONDARY))
        self.wd_ball = ToggleButton(text='NO', state='normal')
        grid.add_widget(self.wd_ball)
        
        grid.add_widget(Label(text='No-ball gives run:', halign='right', color=TEXT_SECONDARY))
        self.nb_run = ToggleButton(text='YES', state='down')
        grid.add_widget(self.nb_run)
        
        grid.add_widget(Label(text='No-ball re-bowled:', halign='right', color=TEXT_SECONDARY))
        self.nb_rebowl = ToggleButton(text='YES', state='down')
        grid.add_widget(self.nb_rebowl)
        
        grid.add_widget(Label(text='Last man can play:', halign='right', color=TEXT_SECONDARY))
        self.last_man = ToggleButton(text='NO', state='normal')
        grid.add_widget(self.last_man)
        
        scroll.add_widget(grid)
        main.add_widget(scroll)
        
        btn = Button(
            text='Next: Player Names',
            size_hint_y=SETUP_BUTTON_HEIGHT,
            background_color=BTN_ACTION,
            font_size=FONT_MEDIUM,
            bold=True
        )
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
            Popup(
                title='Invalid',
                content=Label(text=str(e), color=TEXT_PRIMARY),
                size_hint=POPUP_SMALL
            ).open()

class PlayerNamesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_enter(self):
        self.clear_widgets()
        self.build_ui()
    
    def build_ui(self):
        main = BoxLayout(orientation='vertical', padding=PAD_NORMAL, spacing=SPACE_NORMAL)
        
        main.add_widget(Label(
            text='Enter Player Names',
            font_size=FONT_LARGE,
            bold=True,
            size_hint_y=SETUP_HEADER_HEIGHT,
            color=TEXT_PRIMARY
        ))
        
        scroll = ScrollView(size_hint_y=SETUP_FORM_HEIGHT)
        grid = GridLayout(
            cols=2,
            spacing=SPACE_NORMAL,
            size_hint_y=None,
            row_default_height=BTN_HEIGHT_NORMAL,
            row_force_default=True
        )
        grid.bind(minimum_height=grid.setter('height'))
        
        self.t1_inputs = []
        self.t2_inputs = []
        
        grid.add_widget(Label(text=mgr.team1_name, bold=True, color=TEXT_ACCENT))
        grid.add_widget(Label(text=mgr.team2_name, bold=True, color=TEXT_ACCENT))
        
        for i in range(mgr.players_per_team):
            t1_in = TextInput(text=f'Player {i+1}', multiline=False)
            t2_in = TextInput(text=f'Player {i+1}', multiline=False)
            
            self.t1_inputs.append(t1_in)
            self.t2_inputs.append(t2_in)
            
            grid.add_widget(t1_in)
            grid.add_widget(t2_in)
        
        scroll.add_widget(grid)
        main.add_widget(scroll)
        
        btn = Button(
            text='Next: Toss',
            size_hint_y=SETUP_BUTTON_HEIGHT,
            background_color=BTN_ACTION,
            font_size=FONT_MEDIUM,
            bold=True
        )
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
        layout = BoxLayout(orientation='vertical', padding=PAD_LARGE, spacing=SPACE_LARGE)
        
        self.lbl = Label(
            text='Time for the Toss!',
            font_size=FONT_XLARGE,
            size_hint_y=0.25,
            bold=True,
            color=TEXT_PRIMARY
        )
        layout.add_widget(self.lbl)
        
        self.btn_toss = Button(
            text='FLIP COIN',
            size_hint_y=0.15,
            background_color=WARNING,
            font_size=FONT_LARGE,
            bold=True
        )
        self.btn_toss.bind(on_press=self.do_toss)
        layout.add_widget(self.btn_toss)
        
        self.choice_box = BoxLayout(spacing=SPACE_MEDIUM, size_hint_y=0.15)
        layout.add_widget(self.choice_box)
        
        layout.add_widget(Label(size_hint_y=0.45))
        self.add_widget(layout)
    
    def do_toss(self, instance):
        self.winner = random.choice([mgr.team1_name, mgr.team2_name])
        mgr.toss_winner = self.winner
        
        self.lbl.text = f'{self.winner} Won!\nChoose:'
        self.btn_toss.disabled = True
        
        btn_bat = Button(
            text='BAT',
            background_color=SUCCESS,
            font_size=FONT_MEDIUM,
            bold=True
        )
        btn_bat.bind(on_press=lambda x: self.set_choice('bat'))
        
        btn_bowl = Button(
            text='BOWL',
            background_color=DANGER,
            font_size=FONT_MEDIUM,
            bold=True
        )
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
        layout = BoxLayout(orientation='vertical', padding=PAD_LARGE, spacing=SPACE_MEDIUM)
        
        layout.add_widget(Label(
            text='Match Rules',
            font_size=FONT_LARGE,
            bold=True,
            size_hint_y=0.12,
            color=TEXT_PRIMARY
        ))
        
        rules_text = mgr.get_rules_summary()
        
        layout.add_widget(Label(
            text=rules_text,
            font_size=FONT_NORMAL,
            size_hint_y=0.68,
            halign='left',
            valign='top',
            text_size=(Window.width - 60, None),
            color=TEXT_SECONDARY
        ))
        
        btn = Button(
            text='START MATCH',
            size_hint_y=0.15,
            background_color=BTN_ACTION,
            font_size=FONT_LARGE,
            bold=True
        )
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
        layout = BoxLayout(orientation='vertical', padding=PAD_SMALL, spacing=SPACE_SMALL)
        
        # SCOREBOARD - Most prominent
        self.score_lbl = Label(
            text='0/0 (0.0)',
            font_size=FONT_HUGE,
            bold=True,
            size_hint_y=SCORING_SCORE_HEIGHT,
            color=TEXT_ACCENT
        )
        layout.add_widget(self.score_lbl)
        
        # INFO - Target, innings
        self.info_lbl = Label(
            text='',
            font_size=FONT_SMALL,
            size_hint_y=SCORING_INFO_HEIGHT,
            color=TEXT_SECONDARY
        )
        layout.add_widget(self.info_lbl)
        
        # PLAYERS - Batsmen & bowler
        self.players_lbl = Label(
            text='',
            font_size=FONT_SMALL,
            size_hint_y=SCORING_PLAYERS_HEIGHT,
            color=TEXT_PRIMARY
        )
        layout.add_widget(self.players_lbl)
        
        # RUN BUTTONS - Large and clear
        runs_grid = GridLayout(cols=4, spacing=SPACE_SMALL, size_hint_y=SCORING_RUNS_HEIGHT)
        
        for r in [0, 1, 2, 3, 4, 5, 6]:
            btn = Button(
                text=str(r),
                background_color=BTN_RUN,
                font_size=FONT_LARGE,
                bold=True
            )
            btn.bind(on_press=lambda x, run=r: self.add_runs(run))
            runs_grid.add_widget(btn)
        
        btn_out = Button(
            text='OUT',
            background_color=BTN_OUT,
            font_size=FONT_LARGE,
            bold=True
        )
        btn_out.bind(on_press=lambda x: self.add_runs(0, is_wicket=True))
        runs_grid.add_widget(btn_out)
        
        layout.add_widget(runs_grid)
        
        # EXTRAS - Wide & No-ball
        extras_box = BoxLayout(spacing=SPACE_SMALL, size_hint_y=SCORING_EXTRAS_HEIGHT)
        
        btn_wd = Button(
            text='WIDE',
            background_color=BTN_EXTRA,
            font_size=FONT_MEDIUM
        )
        btn_wd.bind(on_press=self.handle_wide)
        
        btn_nb = Button(
            text='NO BALL',
            background_color=BTN_EXTRA,
            font_size=FONT_MEDIUM
        )
        btn_nb.bind(on_press=self.handle_noball)
        
        extras_box.add_widget(btn_wd)
        extras_box.add_widget(btn_nb)
        layout.add_widget(extras_box)
        
        # CONTROLS - Undo, bowler, rules, end
        ctrl_box = BoxLayout(spacing=SPACE_SMALL, size_hint_y=SCORING_CONTROLS_HEIGHT)
        
        btn_undo = Button(
            text='UNDO',
            background_color=BTN_CONTROL,
            font_size=FONT_NORMAL
        )
        btn_undo.bind(on_press=self.do_undo)
        
        btn_bowler = Button(
            text='BOWLER',
            background_color=SECONDARY,
            font_size=FONT_NORMAL
        )
        btn_bowler.bind(on_press=self.change_bowler)
        
        btn_rules = Button(
            text='RULES',
            background_color=BTN_CONTROL,
            font_size=FONT_NORMAL
        )
        btn_rules.bind(on_press=self.show_rules)
        
        btn_end = Button(
            text='END',
            background_color=DANGER,
            font_size=FONT_NORMAL
        )
        btn_end.bind(on_press=self.end_innings_manual)
        
        ctrl_box.add_widget(btn_undo)
        ctrl_box.add_widget(btn_bowler)
        ctrl_box.add_widget(btn_rules)
        ctrl_box.add_widget(btn_end)
        layout.add_widget(ctrl_box)
        
        # HISTORY - Recent balls
        self.history_lbl = Label(
            text='',
            font_size=FONT_NORMAL,
            size_hint_y=SCORING_HISTORY_HEIGHT,
            color=TEXT_SECONDARY
        )
        layout.add_widget(self.history_lbl)
        
        self.add_widget(layout)
    
    def on_enter(self):
        self.update_display()
    
    def add_runs(self, runs, is_wicket=False):
        mgr.process_delivery(runs, is_wicket=is_wicket)
        self.update_display()
        self.check_auto_end()
    
    def handle_wide(self, instance):
        content = BoxLayout(orientation='vertical', padding=PAD_MEDIUM, spacing=SPACE_MEDIUM)
        content.add_widget(Label(
            text='Runs from wide (batsman):',
            size_hint_y=0.3,
            color=TEXT_PRIMARY
        ))
        
        runs_input = TextInput(
            text='0',
            input_filter='int',
            multiline=False,
            size_hint_y=0.3,
            font_size=FONT_LARGE
        )
        content.add_widget(runs_input)
        
        btn_box = BoxLayout(spacing=SPACE_NORMAL, size_hint_y=0.35)
        btn_cancel = Button(text='CANCEL', background_color=BTN_CONTROL)
        btn_ok = Button(text='OK', background_color=SUCCESS)
        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_ok)
        content.add_widget(btn_box)
        
        popup = Popup(
            title='Wide Ball',
            content=content,
            size_hint=POPUP_MEDIUM,
            auto_dismiss=False
        )
        
        def on_ok(instance):
            try:
                runs = int(runs_input.text) if runs_input.text else 0
                runs = max(0, min(runs, 6))
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
        content = BoxLayout(orientation='vertical', padding=PAD_MEDIUM, spacing=SPACE_MEDIUM)
        content.add_widget(Label(
            text='Runs scored (by batsman):',
            size_hint_y=0.3,
            color=TEXT_PRIMARY
        ))
        
        runs_input = TextInput(
            text='0',
            input_filter='int',
            multiline=False,
            size_hint_y=0.3,
            font_size=FONT_LARGE
        )
        content.add_widget(runs_input)
        
        btn_box = BoxLayout(spacing=SPACE_NORMAL, size_hint_y=0.35)
        btn_cancel = Button(text='CANCEL', background_color=BTN_CONTROL)
        btn_ok = Button(text='OK', background_color=SUCCESS)
        btn_box.add_widget(btn_cancel)
        btn_box.add_widget(btn_ok)
        content.add_widget(btn_box)
        
        popup = Popup(
            title='No Ball',
            content=content,
            size_hint=POPUP_MEDIUM,
            auto_dismiss=False
        )
        
        def on_ok(instance):
            try:
                runs = int(runs_input.text) if runs_input.text else 0
                runs = max(0, min(runs, 6))
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
            Popup(
                title='Cannot Undo',
                content=Label(
                    text='No actions to undo.\n\nNote: Undo cleared after innings break.',
                    color=TEXT_PRIMARY
                ),
                size_hint=POPUP_MEDIUM
            ).open()
            return
        
        if mgr.undo():
            self.update_display()
        else:
            Popup(
                title='Undo Failed',
                content=Label(text='Unable to undo.', color=TEXT_PRIMARY),
                size_hint=POPUP_SMALL
            ).open()
    
    def change_bowler(self, instance):
        content = BoxLayout(orientation='vertical', padding=PAD_MEDIUM, spacing=SPACE_SMALL)
        content.add_widget(Label(
            text='Select Bowler:',
            size_hint_y=0.2,
            color=TEXT_PRIMARY
        ))
        
        scroll = ScrollView(size_hint_y=0.6)
        btn_box = BoxLayout(orientation='vertical', spacing=SPACE_SMALL, size_hint_y=None)
        btn_box.bind(minimum_height=btn_box.setter('height'))
        
        bowl_stats = mgr.get_bowling_stats()
        for i, player in enumerate(bowl_stats):
            btn = Button(
                text=f'{player.name}',
                size_hint_y=None,
                height=BTN_HEIGHT_MEDIUM,
                background_color=SECONDARY
            )
            btn.bind(on_press=lambda x, idx=i: self.select_bowler(idx, popup))
            btn_box.add_widget(btn)
        
        scroll.add_widget(btn_box)
        content.add_widget(scroll)
        
        popup = Popup(title='Change Bowler', content=content, size_hint=POPUP_LARGE)
        popup.open()
    
    def select_bowler(self, idx, popup):
        mgr.change_bowler(idx)
        popup.dismiss()
        self.update_display()
    
    def show_rules(self, instance):
        content = BoxLayout(orientation='vertical', padding=PAD_MEDIUM, spacing=SPACE_MEDIUM)
        
        rules_text = mgr.get_rules_summary()
        content.add_widget(Label(
            text=rules_text,
            size_hint_y=0.8,
            halign='left',
            valign='top',
            text_size=(Window.width - 60, None),
            color=TEXT_SECONDARY
        ))
        
        btn = Button(
            text='Close',
            size_hint_y=0.15,
            background_color=BTN_CONTROL
        )
        content.add_widget(btn)
        
        popup = Popup(title='Match Rules', content=content, size_hint=POPUP_LARGE)
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
        
        hist = " ".join(s.ball_history[-18:])
        self.history_lbl.text = f"Recent:\n{hist}"
    
    def check_auto_end(self):
        s = mgr.state
        
        max_wickets = mgr.get_max_wickets_for_innings_end()
        
        if s.wickets >= max_wickets:
            self.handle_innings_break()
            return
        
        if s.legal_balls >= mgr.overs * 6:
            self.handle_innings_break()
            return
        
        if s.target and s.score >= s.target:
            self.manager.current = 'result'
    
    def end_innings_manual(self, instance):
        content = BoxLayout(orientation='vertical', padding=PAD_LARGE, spacing=SPACE_MEDIUM)
        
        content.add_widget(Label(
            text='End this innings?\n\nThis cannot be undone.',
            font_size=FONT_NORMAL,
            size_hint_y=0.6,
            color=TEXT_PRIMARY
        ))
        
        btn_box = BoxLayout(spacing=SPACE_MEDIUM, size_hint_y=0.35)
        
        btn_yes = Button(
            text='YES, END',
            background_color=DANGER,
            bold=True
        )
        btn_no = Button(
            text='CANCEL',
            background_color=SECONDARY
        )
        
        btn_box.add_widget(btn_no)
        btn_box.add_widget(btn_yes)
        content.add_widget(btn_box)
        
        popup = Popup(
            title='Confirm End Innings',
            content=content,
            size_hint=POPUP_MEDIUM
        )
        
        btn_yes.bind(on_press=lambda x: self.confirm_end_innings(popup))
        btn_no.bind(on_press=popup.dismiss)
        
        popup.open()
    
    def confirm_end_innings(self, popup):
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
            
            mgr.undo_stack = []
            
            s.target = s.score + 1
            s.current_innings = 2
            
            s.score = 0
            s.wickets = 0
            s.legal_balls = 0
            s.extras = 0
            s.ball_history = []
            s.striker_idx = 0
            s.non_striker_idx = 1
            s.bowler_idx = 0
            
            mgr.batting_team_name, mgr.bowling_team_name = \
                mgr.bowling_team_name, mgr.batting_team_name
            
            mgr.persist_to_disk()
            
            Popup(
                title='Innings Break',
                content=Label(
                    text=f'Target: {s.target}\nSwap sides!',
                    color=TEXT_PRIMARY
                ),
                size_hint=POPUP_MEDIUM,
                auto_dismiss=True
            ).open()
            
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
        layout = BoxLayout(orientation='vertical', padding=PAD_LARGE, spacing=SPACE_LARGE)
        
        s = mgr.state
        
        winner_text = "Match Drawn"
        winner_color = TEXT_SECONDARY
        
        if s.target:
            if s.score >= s.target:
                winner_text = f"{mgr.batting_team_name} Wins!"
                winner_color = SUCCESS
            elif s.score == s.target - 1:
                winner_text = "Match Tied!"
                winner_color = WARNING
            else:
                winner_text = f"{mgr.bowling_team_name} Wins!"
                winner_color = SUCCESS
        
        layout.add_widget(Label(
            text='MATCH COMPLETE',
            font_size=FONT_LARGE,
            bold=True,
            size_hint_y=RESULT_HEADER_HEIGHT,
            color=TEXT_PRIMARY
        ))
        
        layout.add_widget(Label(
            text=winner_text,
            font_size=FONT_XLARGE,
            color=winner_color,
            size_hint_y=RESULT_WINNER_HEIGHT,
            bold=True
        ))
        
        score_text = self.get_score_summary()
        layout.add_widget(Label(
            text=score_text,
            font_size=FONT_MEDIUM,
            size_hint_y=RESULT_SCORES_HEIGHT,
            color=TEXT_PRIMARY
        ))
        
        pom, pom_reason = self.get_player_of_match()
        layout.add_widget(Label(
            text=f'Player of Match:\n{pom}\n{pom_reason}',
            font_size=FONT_NORMAL,
            size_hint_y=RESULT_POM_HEIGHT,
            color=TEXT_ACCENT
        ))
        
        btn_box = BoxLayout(spacing=SPACE_MEDIUM, size_hint_y=RESULT_BUTTONS_HEIGHT)
        
        btn_stats = Button(
            text='View Stats',
            background_color=SECONDARY
        )
        btn_stats.bind(on_press=self.show_stats)
        
        btn_new = Button(
            text='New Match',
            background_color=BTN_ACTION,
            bold=True
        )
        btn_new.bind(on_press=self.new_match)
        
        btn_home = Button(
            text='Home',
            background_color=BTN_CONTROL
        )
        btn_home.bind(on_press=self.go_home)
        
        btn_box.add_widget(btn_stats)
        btn_box.add_widget(btn_new)
        btn_box.add_widget(btn_home)
        
        layout.add_widget(btn_box)
        layout.add_widget(Label(size_hint_y=RESULT_SPACER_HEIGHT))
        
        self.add_widget(layout)
    
    def get_score_summary(self):
        s = mgr.state
        
        if mgr.batting_team_name == mgr.team1_name:
            inn1_team = mgr.team2_name
            inn2_team = mgr.team1_name
        else:
            inn1_team = mgr.team1_name
            inn2_team = mgr.team2_name
        
        if s.innings1_data:
            inn1_text = f"{inn1_team}: {s.innings1_data.score}/{s.innings1_data.wickets} ({s.innings1_data.overs_str()})"
        else:
            inn1_text = f"{inn1_team}: Data not available"
        
        if s.innings2_data:
            inn2_text = f"{inn2_team}: {s.innings2_data.score}/{s.innings2_data.wickets} ({s.innings2_data.overs_str()})"
        else:
            inn2_text = f"{inn2_team}: {s.score}/{s.wickets} ({s.legal_balls//6}.{s.legal_balls%6})"
        
        return f"{inn1_text}\n{inn2_text}"
    
    def get_player_of_match(self):
        all_players = mgr.state.team1_stats + mgr.state.team2_stats
        
        best_player = None
        best_score = -1
        best_reason = ""
        
        for p in all_players:
            if p.balls_faced == 0 and p.legal_balls_bowled == 0:
                continue
            
            score = 0
            reasons = []
            
            if p.runs > 0:
                score += p.runs
                reasons.append(f"{p.runs} runs")
                
                if p.balls_faced >= 10 and p.strike_rate() > 150:
                    bonus = p.runs * 0.5
                    score += bonus
                    reasons.append(f"SR {p.strike_rate():.1f}")
            
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
        layout = BoxLayout(orientation='vertical', padding=PAD_NORMAL, spacing=SPACE_MEDIUM)
        
        layout.add_widget(Label(
            text='Match Statistics',
            font_size=FONT_LARGE,
            bold=True,
            size_hint_y=STATS_HEADER_HEIGHT,
            color=TEXT_PRIMARY
        ))
        
        scroll = ScrollView(size_hint_y=STATS_CONTENT_HEIGHT)
        stats_layout = BoxLayout(
            orientation='vertical',
            spacing=SPACE_MEDIUM,
            size_hint_y=None
        )
        stats_layout.bind(minimum_height=stats_layout.setter('height'))
        
        # Team 1 batting
        stats_layout.add_widget(Label(
            text=f'[b]{mgr.team1_name} - Batting[/b]',
            markup=True,
            size_hint_y=None,
            height=35,
            color=INFO
        ))
        
        for p in mgr.state.team1_stats:
            if p.balls_faced > 0:
                txt = f"{p.name}: {p.runs}({p.balls_faced})"
                if p.fours > 0 or p.sixes > 0:
                    txt += f" [{p.fours}x4, {p.sixes}x6]"
                txt += f" SR: {p.strike_rate():.1f}"
                stats_layout.add_widget(Label(
                    text=txt,
                    size_hint_y=None,
                    height=30,
                    color=TEXT_SECONDARY
                ))
        
        # Team 1 bowling
        stats_layout.add_widget(Label(
            text=f'[b]{mgr.team1_name} - Bowling[/b]',
            markup=True,
            size_hint_y=None,
            height=35,
            color=INFO
        ))
        
        for p in mgr.state.team1_stats:
            if p.legal_balls_bowled > 0:
                overs = p.legal_balls_bowled // 6
                balls = p.legal_balls_bowled % 6
                txt = f"{p.name}: {p.wickets}/{p.runs_conceded} in {overs}.{balls} ov"
                txt += f" Eco: {p.economy():.1f}"
                stats_layout.add_widget(Label(
                    text=txt,
                    size_hint_y=None,
                    height=30,
                    color=TEXT_SECONDARY
                ))
        
        stats_layout.add_widget(Label(text='', size_hint_y=None, height=20))
        
        # Team 2 batting
        stats_layout.add_widget(Label(
            text=f'[b]{mgr.team2_name} - Batting[/b]',
            markup=True,
            size_hint_y=None,
            height=35,
            color=WARNING
        ))
        
        for p in mgr.state.team2_stats:
            if p.balls_faced > 0:
                txt = f"{p.name}: {p.runs}({p.balls_faced})"
                if p.fours > 0 or p.sixes > 0:
                    txt += f" [{p.fours}x4, {p.sixes}x6]"
                txt += f" SR: {p.strike_rate():.1f}"
                stats_layout.add_widget(Label(
                    text=txt,
                    size_hint_y=None,
                    height=30,
                    color=TEXT_SECONDARY
                ))
        
        # Team 2 bowling
        stats_layout.add_widget(Label(
            text=f'[b]{mgr.team2_name} - Bowling[/b]',
            markup=True,
            size_hint_y=None,
            height=35,
            color=WARNING
        ))
        
        for p in mgr.state.team2_stats:
            if p.legal_balls_bowled > 0:
                overs = p.legal_balls_bowled // 6
                balls = p.legal_balls_bowled % 6
                txt = f"{p.name}: {p.wickets}/{p.runs_conceded} in {overs}.{balls} ov"
                txt += f" Eco: {p.economy():.1f}"
                stats_layout.add_widget(Label(
                    text=txt,
                    size_hint_y=None,
                    height=30,
                    color=TEXT_SECONDARY
                ))
        
        scroll.add_widget(stats_layout)
        layout.add_widget(scroll)
        
        btn_back = Button(
            text='Back to Result',
            size_hint_y=STATS_BUTTON_HEIGHT,
            background_color=BTN_CONTROL,
            font_size=FONT_MEDIUM
        )
        btn_back.bind(on_press=lambda x: setattr(self.manager, 'current', 'result'))
        layout.add_widget(btn_back)
        
        self.add_widget(layout)

class CricketApp(App):
    def build(self):
        Window.clearcolor = BG_DARK
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

if __name__ == '__main__':
    CricketApp().run()
