import pyautogui
import json
import os
from datetime import datetime

print("="*80)
print("CHART COORDINATE CALIBRATION - AUTO-EXPORT (ARCH LINUX)")
print("="*80)
print()

print("STEP 1: Detecting screen layout...")
total_size = pyautogui.size()
print(f"Total screen size: {total_size}")
print()

# Calibrate chart
print("="*80)
print("STEP 2: Calibrate chart coordinates")
print("="*80)
print()

input("Move to TOP-LEFT corner of chart window, then press ENTER: ")
chart_tl = pyautogui.position()
print(f"  Top-left: {chart_tl}")

input("Move to BOTTOM-RIGHT corner of chart window, then press ENTER: ")
chart_br = pyautogui.position()
print(f"  Bottom-right: {chart_br}")

chart_x = min(chart_tl[0], chart_br[0])
chart_y = min(chart_tl[1], chart_br[1])
chart_w = abs(chart_br[0] - chart_tl[0])
chart_h = abs(chart_br[1] - chart_tl[1])

print()
print("Chart coordinates detected:")
print(f"  CHART_X = {chart_x}")
print(f"  CHART_Y = {chart_y}")
print(f"  CHART_W = {chart_w}")
print(f"  CHART_H = {chart_h}")
print()

# Indicator region
print("="*80)
print("STEP 3: Calibrate indicator region (Market Cipher dots)")
print("="*80)
print()

input("Move to CENTER of indicator dots area, then press ENTER: ")
indicator_center = pyautogui.position()
print(f"  Center: {indicator_center}")

ind_x = indicator_center[0] - 75
ind_y = indicator_center[1] - 75
ind_w = 150
ind_h = 150

print(f"Indicator region: ({ind_x}, {ind_y}, {ind_w}, {ind_h})")
print()

# Buy button
print("="*80)
print("STEP 4: Calibrate Buy button")
print("="*80)
print()

input("Move to center of BUY button, then press ENTER: ")
buy_pos = pyautogui.position()
print(f"  BUY_BUTTON = {buy_pos}")
print()

# Sell button
print("="*80)
print("STEP 5: Calibrate Sell button")
print("="*80)
print()

input("Move to center of SELL button, then press ENTER: ")
sell_pos = pyautogui.position()
print(f"  SELL_BUTTON = {sell_pos}")
print()

# Create configuration dictionary
config = {
    "timestamp": datetime.now().isoformat(),
    "screen_layout": {
        "total_virtual_size": total_size,
    },
    "chart_coordinates": {
        "CHART_X": chart_x,
        "CHART_Y": chart_y,
        "CHART_W": chart_w,
        "CHART_H": chart_h,
    },
    "indicator_region": {
        "INDICATOR_X": ind_x,
        "INDICATOR_Y": ind_y,
        "INDICATOR_W": ind_w,
        "INDICATOR_H": ind_h,
    },
    "buttons": {
        "BUY_BUTTON": list(buy_pos),
        "SELL_BUTTON": list(sell_pos),
    },
}

# Save as JSON
json_filename = "chart_config.json"
with open(json_filename, "w") as f:
    json.dump(config, f, indent=2)

# Save as Python code
py_filename = "chart_config.py"
with open(py_filename, "w") as f:
    f.write("# ========== AUTO-GENERATED CHART CONFIGURATION ==========\n")
    f.write(f"# Generated: {datetime.now().isoformat()}\n")
    f.write("# Copy and paste this into your forex_bot.py configuration section\n\n")
    f.write(f"CHART_X = {chart_x}\n")
    f.write(f"CHART_Y = {chart_y}\n")
    f.write(f"CHART_W = {chart_w}\n")
    f.write(f"CHART_H = {chart_h}\n\n")
    f.write(f"# Indicator region\n")
    f.write(f"INDICATOR_X = {ind_x}\n")
    f.write(f"INDICATOR_Y = {ind_y}\n")
    f.write(f"INDICATOR_W = {ind_w}\n")
    f.write(f"INDICATOR_H = {ind_h}\n")
    f.write(f"INDICATOR_REGION = (INDICATOR_X, INDICATOR_Y, INDICATOR_W, INDICATOR_H)\n\n")
    f.write(f"# Button positions\n")
    f.write(f"BUY_BUTTON = {tuple(buy_pos)}\n")
    f.write(f"SELL_BUTTON = {tuple(sell_pos)}\n\n")
    f.write(f"# Forex pair\n")
    f.write(f"FOREX_PAIR = 'EURUSD=X'\n")

# Save as human-readable TXT
txt_filename = "chart_coordinates.txt"
with open(txt_filename, "w") as f:
    f.write("="*80 + "\n")
    f.write("CHART CALIBRATION RESULTS\n")
    f.write("="*80 + "\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write("SCREEN LAYOUT:\n")
    f.write(f"  Total size: {total_size}\n\n")
    f.write("CHART COORDINATES:\n")
    f.write(f"  CHART_X = {chart_x}\n")
    f.write(f"  CHART_Y = {chart_y}\n")
    f.write(f"  CHART_W = {chart_w}\n")
    f.write(f"  CHART_H = {chart_h}\n\n")
    f.write("INDICATOR REGION (Market Cipher dots):\n")
    f.write(f"  INDICATOR_REGION = ({ind_x}, {ind_y}, {ind_w}, {ind_h})\n\n")
    f.write("BUTTON POSITIONS:\n")
    f.write(f"  BUY_BUTTON = {buy_pos}\n")
    f.write(f"  SELL_BUTTON = {sell_pos}\n\n")
    f.write("="*80 + "\n")
    f.write("NEXT STEPS:\n")
    f.write("="*80 + "\n")
    f.write("1. Open 'chart_config.py' and copy all content\n")
    f.write("2. Paste into forex_bot.py CONFIG section\n")
    f.write("3. Run: python test_setup.py\n")
    f.write("4. Verify /tmp/chart_capture_test.png shows your chart\n")
    f.write("5. If verified, run: python forex_bot.py\n")

print("\n" + "="*80)
print("✅ CALIBRATION COMPLETE - FILES EXPORTED")
print("="*80)
print()
print(f"Files created:")
print(f"  1. {json_filename}       - JSON format")
print(f"  2. {py_filename}        - Python code (paste into forex_bot.py)")
print(f"  3. {txt_filename}  - Human-readable")
print()
print("NEXT STEP:")
print(f"  Open '{py_filename}' and copy all content into forex_bot.py")
print()
