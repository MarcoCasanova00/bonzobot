import pyautogui
import json
import os
import cv2
import numpy as np
from datetime import datetime
from PIL import Image, ImageDraw

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_input(prompt):
    print(f"\n>>> {prompt}")
    return input("Press ENTER when ready...")

clear_screen()
print("="*80)
print("       BONZOBOT - SMART CHART CALIBRATION (TRADING 212 & TRADINGVIEW)")
print("="*80)
print("\nThis script will help you set the coordinates for the bot to 'see' your chart.")
print("Make sure your browser with the chart is visible on your screen.")

print("\nSTEP 1: Detecting screen layout...")
total_size = pyautogui.size()
print(f"✓ Total screen size detected: {total_size}")

# --- CHART REGION ---
print("\n" + "="*80)
print("STEP 2: CALIBRATE MAIN CHART AREA")
print("="*80)
print("The bot needs to see the price action to detect divergences and zones.")

get_input("Move your mouse to the TOP-LEFT corner of the actual PRICE CHART area.")
chart_tl = pyautogui.position()
print(f"  Captured Top-left: {chart_tl}")

get_input("Move your mouse to the BOTTOM-RIGHT corner of the PRICE CHART area.")
chart_br = pyautogui.position()
print(f"  Captured Bottom-right: {chart_br}")

chart_x = min(chart_tl[0], chart_br[0])
chart_y = min(chart_tl[1], chart_br[1])
chart_w = abs(chart_br[0] - chart_tl[0])
chart_h = abs(chart_br[1] - chart_tl[1])

# --- INDICATOR REGION ---
print("\n" + "="*80)
print("STEP 3: CALIBRATE INDICATOR (MARKET CIPHER DOTS)")
print("="*80)
print("The bot looks for GREEN and RED dots on your indicator (e.g., Market Cipher B).")
print("If you don't have an indicator with dots, the bot will not work!")

get_input("Move your mouse to the CENTER of where the GREEN/RED DOTS appear.")
indicator_center = pyautogui.position()
print(f"  Captured Indicator Center: {indicator_center}")

# Define a 150x150 box around the center
ind_x = indicator_center[0] - 75
ind_y = indicator_center[1] - 75
ind_w = 150
ind_h = 150

# --- BUTTONS ---
print("\n" + "="*80)
print("STEP 4: CALIBRATE TRADING BUTTONS")
print("="*80)
print("On Trading 212, these are the 'COMPRA' (Buy) and 'VENDI' (Sell) buttons.")

get_input("Move your mouse to the center of the BUY (COMPRA) button.")
buy_pos = pyautogui.position()
print(f"  Captured BUY_BUTTON: {buy_pos}")

get_input("Move your mouse to the center of the SELL (VENDI) button.")
sell_pos = pyautogui.position()
print(f"  Captured SELL_BUTTON: {sell_pos}")

# --- PREVIEW GENERATION ---
print("\n" + "="*80)
print("STEP 5: GENERATING VISUAL PREVIEW")
print("="*80)
print("Capturing your screen to verify the coordinates...")

try:
    # Capture full screen for preview
    full_screen = pyautogui.screenshot()
    preview_img = full_screen.copy()
    draw = ImageDraw.Draw(preview_img)
    
    # Draw Chart Region (Blue)
    draw.rectangle([chart_x, chart_y, chart_x + chart_w, chart_y + chart_h], outline="blue", width=5)
    draw.text((chart_x + 10, chart_y + 10), "CHART AREA", fill="blue")
    
    # Draw Indicator Region (Green)
    draw.rectangle([ind_x, ind_y, ind_x + ind_w, ind_y + ind_h], outline="green", width=5)
    draw.text((ind_x + 10, ind_y + 10), "DOTS INDICATOR", fill="green")
    
    # Draw Buttons (Red)
    draw.ellipse([buy_pos[0]-10, buy_pos[1]-10, buy_pos[0]+10, buy_pos[1]+10], outline="red", width=3)
    draw.text((buy_pos[0] + 15, buy_pos[1]), "BUY", fill="red")
    
    draw.ellipse([sell_pos[0]-10, sell_pos[1]-10, sell_pos[0]+10, sell_pos[1]+10], outline="red", width=3)
    draw.text((sell_pos[0] + 15, sell_pos[1]), "SELL", fill="red")
    
    preview_path = "calibration_preview.png"
    preview_img.save(preview_path)
    print(f"✓ Preview saved to: {preview_path}")
    print("  PLEASE OPEN THIS IMAGE AND VERIFY THE BOXES ARE CORRECT!")
except Exception as e:
    print(f"✗ Failed to generate preview: {e}")

# --- SAVE CONFIG ---
config = {
    "timestamp": datetime.now().isoformat(),
    "chart_coordinates": {
        "CHART_X": chart_x, "CHART_Y": chart_y, "CHART_W": chart_w, "CHART_H": chart_h,
    },
    "indicator_region": {
        "INDICATOR_X": ind_x, "INDICATOR_Y": ind_y, "INDICATOR_W": ind_w, "INDICATOR_H": ind_h,
    },
    "buttons": {
        "BUY_BUTTON": list(buy_pos), "SELL_BUTTON": list(sell_pos),
    },
}

with open("chart_config.json", "w") as f:
    json.dump(config, f, indent=2)

with open("chart_config.py", "w") as f:
    f.write(f"CHART_X = {chart_x}\nCHART_Y = {chart_y}\nCHART_W = {chart_w}\nCHART_H = {chart_h}\n\n")
    f.write(f"INDICATOR_REGION = ({ind_x}, {ind_y}, {ind_w}, {ind_h})\n\n")
    f.write(f"BUY_BUTTON = {tuple(buy_pos)}\nSELL_BUTTON = {tuple(sell_pos)}\n")
    f.write(f"FOREX_PAIR = 'EURUSD=X'\n")

print("\n" + "="*80)
print("✅ CALIBRATION COMPLETE")
print("="*80)
print(f"1. Check 'calibration_preview.png' to verify the regions.")
print(f"2. Copy the content of 'chart_config.py' into 'forex_bot.py'.")
print(f"3. Run the bot: ./bonzobot.sh forex_bot.py")
print("="*80 + "\n")
