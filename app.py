import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random
import time

# --- USER INPUTS ---
st.sidebar.header("Settings")
NUMBER_OF_LOGOS = st.sidebar.slider(
    "Number of logos", min_value=1, max_value=100, value=5
)
PAUSE_AMOUNT = st.sidebar.slider(
    "Animation speed (seconds per frame)", min_value=0.01, max_value=1.0, value=0.1, step=0.01
)
CLOUD_MODE = st.sidebar.checkbox(
    "Cloud Mode (enable if animation is laggy/static on Streamlit Cloud)",
    value=False,
    help="Increases minimum frame time for better performance on cloud deployments"
)

# --- SETTINGS ---
WIDTH, HEIGHT = 600, 400  # Canvas size
COLORS = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']

# Directions
UP_RIGHT, UP_LEFT, DOWN_RIGHT, DOWN_LEFT = 'ur', 'ul', 'dr', 'dl'
DIRECTIONS = (UP_RIGHT, UP_LEFT, DOWN_RIGHT, DOWN_LEFT)

# Logo dictionary keys
COLOR = 'color'
X = 'x'
Y = 'y'
DIR = 'direction'

# --- STREAMLIT STATE ---
if 'logos' not in st.session_state or len(st.session_state.logos) != NUMBER_OF_LOGOS:
    st.session_state.logos = []
    for _ in range(NUMBER_OF_LOGOS):
        x = random.randint(1, WIDTH - 60)
        y = random.randint(1, HEIGHT - 30)
        if x % 2 == 1:
            x -= 1  # Make X even to match terminal logic
        st.session_state.logos.append({
            COLOR: random.choice(COLORS),
            X: x,
            Y: y,
            DIR: random.choice(DIRECTIONS)
        })
    st.session_state.corner_bounces = 0  # Reset counter when logos change

if 'corner_bounces' not in st.session_state:
    st.session_state.corner_bounces = 0

# --- STREAMLIT UI ---
st.title("Bouncing DVD Logo")
canvas_placeholder = st.empty()
counter_placeholder = st.empty()  # Corner bounces placeholder
debug_placeholder = st.empty()  # Debug info placeholder

# Monospace font to mimic terminal - try multiple common system fonts
font = None
font_paths = [
    "DejaVuSansMono.ttf",  # Local Windows/Mac
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",  # Linux/Cloud
    "/System/Library/Fonts/Courier.dfont",  # Mac
    "C:\\Windows\\Fonts\\consola.ttf",  # Windows Consolas
    "courier",  # Generic courier
]
font_size = 24

for font_path in font_paths:
    try:
        font = ImageFont.truetype(font_path, font_size)
        break
    except:
        continue

if font is None:
    # Last resort: use PIL's default font with size
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

# --- ANIMATION LOOP ---
while True:
    frame_start_time = time.time()

    img = Image.new("RGB", (WIDTH, HEIGHT), "black")
    draw = ImageDraw.Draw(img)

    for logo in st.session_state.logos:
        original_direction = logo[DIR]

        # --- CORNER BOUNCES ---
        if logo[X] <= 0 and logo[Y] <= 0:
            logo[DIR] = DOWN_RIGHT
            st.session_state.corner_bounces += 1
        elif logo[X] <= 0 and logo[Y] >= HEIGHT - 30:
            logo[DIR] = UP_RIGHT
            st.session_state.corner_bounces += 1
        elif logo[X] >= WIDTH - 60 and logo[Y] <= 0:
            logo[DIR] = DOWN_LEFT
            st.session_state.corner_bounces += 1
        elif logo[X] >= WIDTH - 60 and logo[Y] >= HEIGHT - 30:
            logo[DIR] = UP_LEFT
            st.session_state.corner_bounces += 1

        # --- EDGE BOUNCES ---
        if logo[X] <= 0 and logo[DIR] == UP_LEFT:
            logo[DIR] = UP_RIGHT
        elif logo[X] <= 0 and logo[DIR] == DOWN_LEFT:
            logo[DIR] = DOWN_RIGHT
        elif logo[X] >= WIDTH - 60 and logo[DIR] == UP_RIGHT:
            logo[DIR] = UP_LEFT
        elif logo[X] >= WIDTH - 60 and logo[DIR] == DOWN_RIGHT:
            logo[DIR] = DOWN_LEFT

        if logo[Y] <= 0 and logo[DIR] == UP_LEFT:
            logo[DIR] = DOWN_LEFT
        elif logo[Y] <= 0 and logo[DIR] == UP_RIGHT:
            logo[DIR] = DOWN_RIGHT
        elif logo[Y] >= HEIGHT - 30 and logo[DIR] == DOWN_LEFT:
            logo[DIR] = UP_LEFT
        elif logo[Y] >= HEIGHT - 30 and logo[DIR] == DOWN_RIGHT:
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

        # Draw the logo
        draw.text((logo[X], logo[Y]), "DVD", fill=logo[COLOR], font=font)

    # --- UPDATE STREAMLIT PLACEHOLDERS ---
    canvas_placeholder.image(img, width=WIDTH)
    counter_placeholder.markdown(f"**Corner bounces:** {st.session_state.corner_bounces}")

    # Adaptive frame timing to ensure Streamlit can render
    frame_time = time.time() - frame_start_time
    # Adjust minimum sleep based on environment
    MIN_SLEEP = 0.15 if CLOUD_MODE else 0.05  # Cloud needs more time for network/rendering
    actual_sleep = max(PAUSE_AMOUNT - frame_time, MIN_SLEEP)
    total_frame_time = frame_time + actual_sleep
    actual_fps = 1.0 / total_frame_time if total_frame_time > 0 else 0
    debug_placeholder.markdown(
        f"*Debug: Frame computation: {frame_time:.3f}s | Sleep: {actual_sleep:.3f}s | "
        f"Target FPS: {1/PAUSE_AMOUNT:.1f} | Actual FPS: {actual_fps:.1f}*"
    )
    time.sleep(actual_sleep)
