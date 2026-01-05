# ===== COLOR PALETTE =====
# Background
BG_DARK = (0.09, 0.14, 0.16, 1)  # #16232A Mirage

# Primary Action
PRIMARY = (1.0, 0.36, 0.02, 1)  # #FF5B04 Blaze Orange
PRIMARY_HOVER = (0.9, 0.32, 0.02, 1)  # Slightly darker

# Secondary / Accent
SECONDARY = (0.03, 0.31, 0.34, 1)  # #075056 Deep Sea Green
SECONDARY_LIGHT = (0.05, 0.41, 0.44, 1)  # Lighter variant

# Neutral / Card
CARD_BG = (0.89, 0.93, 0.94, 1)  # #E4EEF0 Wild Sand
CARD_BG_DARK = (0.2, 0.25, 0.27, 1)  # Darker card variant

# Text Colors
TEXT_PRIMARY = (0.95, 0.95, 0.95, 1)  # Almost white
TEXT_SECONDARY = (0.7, 0.75, 0.77, 1)  # Muted light
TEXT_ACCENT = (1.0, 0.9, 0.3, 1)  # Yellow for scores
TEXT_DARK = (0.15, 0.15, 0.15, 1)  # For light backgrounds

# Status Colors
SUCCESS = (0.2, 0.8, 0.3, 1)  # Green
WARNING = (1.0, 0.7, 0.2, 1)  # Amber
DANGER = (0.9, 0.2, 0.2, 1)  # Red
INFO = (0.2, 0.5, 0.9, 1)  # Blue

# Button Specific
BTN_RUN = (0.15, 0.45, 0.85, 1)  # Blue for run buttons
BTN_OUT = (0.85, 0.15, 0.15, 1)  # Red for wicket
BTN_EXTRA = (0.75, 0.55, 0.15, 1)  # Amber for extras
BTN_CONTROL = (0.45, 0.45, 0.45, 1)  # Gray for controls
BTN_ACTION = PRIMARY  # Orange for primary actions

# ===== TYPOGRAPHY =====
# Font Sizes (in sp)
FONT_HUGE = '48sp'  # Main scoreboard
FONT_XLARGE = '36sp'  # Page titles
FONT_LARGE = '24sp'  # Section headers
FONT_MEDIUM = '18sp'  # Body text, buttons
FONT_NORMAL = '16sp'  # Regular text
FONT_SMALL = '14sp'  # Secondary info
FONT_TINY = '12sp'  # Hints, footnotes

# ===== SPACING =====
# Padding (in dp)
PAD_LARGE = 20
PAD_MEDIUM = 15
PAD_NORMAL = 10
PAD_SMALL = 8
PAD_TINY = 5

# Spacing between elements
SPACE_LARGE = 15
SPACE_MEDIUM = 10
SPACE_NORMAL = 8
SPACE_SMALL = 5

# ===== SIZING =====
# Button heights
BTN_HEIGHT_LARGE = 65
BTN_HEIGHT_MEDIUM = 50
BTN_HEIGHT_NORMAL = 45

# Screen size hints (as decimals)
SIZE_HUGE = 0.25
SIZE_LARGE = 0.18
SIZE_MEDIUM = 0.12
SIZE_NORMAL = 0.10
SIZE_SMALL = 0.08

# ===== CONSTANTS =====
# Popup sizes (as tuples)
POPUP_SMALL = (0.7, 0.3)
POPUP_MEDIUM = (0.75, 0.4)
POPUP_LARGE = (0.85, 0.6)

# ===== SCREEN-SPECIFIC LAYOUTS =====

# Scoring Screen Layout Proportions
SCORING_SCORE_HEIGHT = 0.16  # Main score display
SCORING_INFO_HEIGHT = 0.06   # Innings info
SCORING_PLAYERS_HEIGHT = 0.07  # Batsmen/bowler info
SCORING_RUNS_HEIGHT = 0.26   # Run buttons grid
SCORING_EXTRAS_HEIGHT = 0.10  # Wide/No-ball buttons
SCORING_CONTROLS_HEIGHT = 0.10  # Undo/Bowler/Rules/End
SCORING_HISTORY_HEIGHT = 0.25  # Ball history display

# Home Screen
HOME_TITLE_HEIGHT = 0.30
HOME_BTN_HEIGHT = 0.15
HOME_SPACER_HEIGHT = 0.40

# Setup Screen
SETUP_HEADER_HEIGHT = 0.08
SETUP_FORM_HEIGHT = 0.77
SETUP_BUTTON_HEIGHT = 0.12

# Result Screen
RESULT_HEADER_HEIGHT = 0.10
RESULT_WINNER_HEIGHT = 0.18
RESULT_SCORES_HEIGHT = 0.15
RESULT_POM_HEIGHT = 0.18
RESULT_BUTTONS_HEIGHT = 0.15
RESULT_SPACER_HEIGHT = 0.24

# Stats Screen
STATS_HEADER_HEIGHT = 0.10
STATS_CONTENT_HEIGHT = 0.78
STATS_BUTTON_HEIGHT = 0.12
