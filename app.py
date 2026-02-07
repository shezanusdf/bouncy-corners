import streamlit as st
from streamlit_drawable_canvas import st_canvas
import random

# --- USER INPUTS ---
st.sidebar.header("Settings")
NUMBER_OF_LOGOS = st.sidebar.slider(
    "Number of logos", min_value=1, max_value=100, value=5
)
PAUSE_AMOUNT = st.sidebar.slider(
    "Animation speed (seconds per frame)", min_value=0.01, max_value=1.0, value=0.05, step=0.01
)

# --- SETTINGS ---
WIDTH, HEIGHT = 600, 400  # Canvas size
LOGO_WIDTH, LOGO_HEIGHT = 60, 30
COLORS = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']

# Directions
UP_RIGHT, UP_LEFT, DOWN_RIGHT, DOWN_LEFT = 'ur', 'ul', 'dr', 'dl'
DIRECTIONS = (UP_RIGHT, UP_LEFT, DOWN_RIGHT, DOWN_LEFT)

# Logo dictionary keys
COLOR = 'color'
X = 'x'
Y = 'y'
DIR = 'direction'

# --- STREAMLIT STATE INIT ---
if 'logos' not in st.session_state or len(st.session_state.logos) != NUMBER_OF_LOGOS:
    st.session_state.logos = []
    for _ in range(NUMBER_OF_LOGOS):
        x = random.randint(0, WIDTH - LOGO_WIDTH)
        y = random.randint(0, HEIGHT - LOGO_HEIGHT)
        st.session_state.logos.append({
            COLOR: random.choice(COLORS),
            X: x,
            Y: y,
            DIR: random.choice(DIRECTIONS)
        })
    st.session_state.corner_bounces = 0

if 'corner_bounces' not in st.session_state:
    st.session_state.corner_bounces = 0

# --- AUTO REFRESH ---
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=int(PAUSE_AMOUNT * 1000), limit=None, key="bouncy_loop")

# --- DRAW LOGOS ---
canvas = st_canvas(
    fill_color="black",
    stroke_width=1,
    stroke_color="black",
    background_color="black",
    width=WIDTH,
    height=HEIGHT,
    drawing_mode="rect",
    key="canvas",
)

for logo in st.session_state.logos:
    original_direction = logo[DIR]

    # --- CORNER BOUNCES ---
    if logo[X] <= 0 and logo[Y] <= 0:
        logo[DIR] = DOWN_RIGHT
        st.session_state.corner_bounces += 1
    elif logo[X] <= 0 and logo[Y] >= HEIGHT - LOGO_HEIGHT:
        logo[DIR] = UP_RIGHT
        st.session_state.corner_bounces += 1
    elif logo[X] >= WIDTH - LOGO_WIDTH and logo[Y] <= 0:
        logo[DIR] = DOWN_LEFT
        st.session_state.corner_bounces += 1
    elif logo[X] >= WIDTH - LOGO_WIDTH and logo[Y] >= HEIGHT - LOGO_HEIGHT:
        logo[DIR] = UP_LEFT
        st.session_state.corner_bounces += 1

    # --- EDGE BOUNCES ---
    if logo[X] <= 0 and logo[DIR] == UP_LEFT:
        logo[DIR] = UP_RIGHT
    elif logo[X] <= 0 and logo[DIR] == DOWN_LEFT:
        logo[DIR] = DOWN_RIGHT
    elif logo[X] >= WIDTH - LOGO_WIDTH and logo[DIR] == UP_RIGHT:
        logo[DIR] = UP_LEFT
    elif logo[X] >= WIDTH - LOGO_WIDTH and logo[DIR] == DOWN_RIGHT:
        logo[DIR] = DOWN_LEFT

    if logo[Y] <= 0 and logo[DIR] == UP_LEFT:
        logo[DIR] = DOWN_LEFT
    elif logo[Y] <= 0 and logo[DIR] == UP_RIGHT:
        logo[DIR] = DOWN_RIGHT
    elif logo[Y] >= HEIGHT - LOGO_HEIGHT and logo[DIR] == DOWN_LEFT:
        logo[DIR] = UP_LEFT
    elif logo[Y] >= HEIGHT - LOGO_HEIGHT and logo[DIR] == DOWN_RIGHT:
        logo[DIR] = UP_RIGHT

    # Change color on bounce
    if logo[DIR] != original_direction:
        logo[COLOR] = random.choice(COLORS)

    # --- MOVE LOGO ---
    if logo[DIR] == UP_RIGHT:
        logo[X] += 4
        logo[Y] -= 2
    elif logo[DIR] == UP_LEFT:
        logo[X] -= 4
        logo[Y] -= 2
    elif logo[DIR] == DOWN_RIGHT:
        logo[X] += 4
        logo[Y] += 2
    elif logo[DIR] == DOWN_LEFT:
        logo[X] -= 4
        logo[Y] += 2

    # Draw rectangle for logo
    if canvas:
        canvas.rect(
            x=logo[X],
            y=logo[Y],
            width=LOGO_WIDTH,
            height=LOGO_HEIGHT,
            fill=logo[COLOR],
        )
        # Draw "DVD" text inside rectangle
        canvas.text(
            x=logo[X]+5,
            y=logo[Y]+5,
            text="DVD",
            fill="white",
            font_size=14
        )

st.markdown(f"**Corner bounces:** {st.session_state.corner_bounces}")
