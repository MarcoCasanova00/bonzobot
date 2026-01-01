import pyautogui
import cv2
import numpy as np
import pytesseract
import time
import random
import yfinance as yf
import talib as ta
import pandas as pd
from datetime import datetime, timedelta
from PIL import Image
import platform
import os
import subprocess
import re

# ========== LINUX INITIALIZATION ==========
if platform.system() == 'Linux':
    # Verify Tesseract installation
    try:
        # Check for local tessdata first
        local_tessdata = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'local_libs/usr/share/tessdata')
        if os.path.exists(local_tessdata):
            os.environ['TESSDATA_PREFIX'] = local_tessdata
            print(f"✓ Using local tessdata: {local_tessdata}")

        result = subprocess.run(['which', 'tesseract'], 
                              capture_output=True, text=True, timeout=5)
        tesseract_path = result.stdout.strip()
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            print(f"✓ Tesseract found at: {tesseract_path}")
        else:
            # Try common paths if 'which' fails
            common_paths = ['/usr/bin/tesseract', '/usr/local/bin/tesseract']
            for p in common_paths:
                if os.path.exists(p):
                    pytesseract.pytesseract.tesseract_cmd = p
                    print(f"✓ Tesseract found at: {p}")
                    break
            else:
                print("✗ Tesseract NOT found. Run: sudo pacman -S tesseract")
                # Don't exit immediately, maybe it's in the path anyway
    except Exception as e:
        print(f"Note: Tesseract path detection issue: {e}")
    
    # Test screenshot permissions
    print("Testing screen capture permissions...")
    try:
        test_shot = pyautogui.screenshot(region=(100, 100, 100, 100))
        print("✓ Screenshot permission granted\n")
    except Exception as e:
        print(f"✗ Screenshot DENIED: {e}")
        print("Make sure browser window is focused and visible")
        exit(1)

# ========== AUTO-GENERATED CHART CONFIGURATION ==========
# Generated: 2026-01-01T19:32:34.933045
# Copy and paste this into your forex_bot.py configuration section

CHART_X = 30
CHART_Y = 143
CHART_W = 1208
CHART_H = 827

# Indicator region
INDICATOR_X = 392
INDICATOR_Y = 522
INDICATOR_W = 150
INDICATOR_H = 150
INDICATOR_REGION = (INDICATOR_X, INDICATOR_Y, INDICATOR_W, INDICATOR_H)

# Button positions
BUY_BUTTON = (1180, 326)
SELL_BUTTON = (995, 324)

# Forex pair
FOREX_PAIR = 'EURUSD=X'


# ============ FALLBACK CONFIGURATION (if calibration not run yet) ============
CHART_X = 100
CHART_Y = 150
CHART_W = 1300
CHART_H = 700

INDICATOR_X = CHART_X + 50
INDICATOR_Y = CHART_Y + 500
INDICATOR_W = CHART_W - 100
INDICATOR_H = 150
INDICATOR_REGION = (INDICATOR_X, INDICATOR_Y, INDICATOR_W, INDICATOR_H)

BUY_BUTTON = (1200, 750)
SELL_BUTTON = (1100, 750)

FOREX_PAIR = 'EURUSD=X'
MIN_GREEN_AREA = 500
MIN_RED_AREA = 500
DEBUG_MODE = True  # Set to True to save indicator scans to /tmp/last_scan.png

print(f"\nConfiguration Loaded:")
print(f"  Chart region: ({CHART_X}, {CHART_Y}, {CHART_W}x{CHART_H})")
print(f"  Indicator region: {INDICATOR_REGION}")
print(f"  Buy button: {BUY_BUTTON}")
print(f"  Sell button: {SELL_BUTTON}")
print(f"  Pair: {FOREX_PAIR}")
print(f"  Platform: {platform.system()}\n")

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

# ============ SCREEN CAPTURE ============
def capture_region(x, y, w, h):
    """Grab screenshot region and return OpenCV BGR image."""
    try:
        screenshot = pyautogui.screenshot(region=(x, y, w, h))
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"Capture error: {e}")
        return None

# ============ VISUAL DETECTION ============
def detect_dots(img):
    """Detect green/red Market Cipher dots via HSV color mask."""
    if img is None:
        return None
    
    try:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Green dot detection
        green_lower = np.array([40, 100, 100])
        green_upper = np.array([80, 255, 255])
        green_mask = cv2.inRange(hsv, green_lower, green_upper)
        green_area = np.sum(green_mask > 0)
        
        # Red dot detection (wrap around hue)
        red_lower1 = np.array([0, 100, 100])
        red_upper1 = np.array([10, 255, 255])
        red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
        
        red_lower2 = np.array([170, 100, 100])
        red_upper2 = np.array([180, 255, 255])
        red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
        
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)
        red_area = np.sum(red_mask > 0)
        
        if DEBUG_MODE:
            cv2.imwrite('/tmp/last_indicator_scan.png', img)
        
        if green_area > MIN_GREEN_AREA:
            return 'green'
        if red_area > MIN_RED_AREA:
            return 'red'
        return None
    except Exception as e:
        print(f"Dot detection error: {e}")
        return None

def detect_divergence(chart_img):
    """Detect divergence via OCR of recent prices."""
    if chart_img is None:
        return False
    
    try:
        gray = cv2.cvtColor(chart_img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        text = pytesseract.image_to_string(enhanced, config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789.')
        
        numbers = re.findall(r'\d+\.?\d*', text)
        if len(numbers) < 2:
            return False
        
        prices = [float(x) for x in numbers[-5:]]
        
        if len(prices) >= 2:
            has_lower_low = prices[-1] < prices[-2]
            return has_lower_low
        return False
    except Exception as e:
        print(f"Divergence detection error: {e}")
        return False

def detect_zone_retrace(chart_img):
    """Detect supply/demand zones via horizontal line detection."""
    if chart_img is None:
        return False
    
    try:
        gray = cv2.cvtColor(chart_img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=50, maxLineGap=10)
        
        if lines is None:
            return False
        
        horiz_lines = [l for l in lines if abs(l[0][1] - l[0][3]) < 5]
        
        return len(horiz_lines) > 2
    except Exception as e:
        print(f"Zone detection error: {e}")
        return False

# ============ BACKEND VERIFICATION (Yahoo Finance) ============
def yfinance_verify(signal):
    """Verify signal using free Yahoo Finance 1-min data."""
    try:
        end = datetime.now()
        start = end - timedelta(days=2)
        
        print(f"Fetching {FOREX_PAIR} data from yfinance...")
        df = yf.download(FOREX_PAIR, start=start, end=end, interval='1m', progress=False)
        
        if df.empty:
            print(f"No data for {FOREX_PAIR}. yfinance may be delayed.")
            return False
        
        # yfinance 1.0+ returns multi-level columns; flatten them
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        
        df = df.dropna()
        
        # Ensure arrays are float64 for TA-Lib
        high = df['High'].values.astype('float64')
        low = df['Low'].values.astype('float64')
        close = df['Close'].values.astype('float64')
        volume = df['Volume'].values.astype('float64') if 'Volume' in df.columns else np.ones(len(df), dtype='float64')
        
        df['MFI'] = ta.MFI(high, low, close, volume, timeperiod=14)
        
        from scipy.signal import argrelextrema
        lows_idx = argrelextrema(df['Low'].values, np.less, order=3)[0]
        
        if len(lows_idx) < 2:
            print("Not enough recent lows for divergence check")
            return False
        
        recent_lows_price = df['Low'].iloc[lows_idx[-2:]]
        recent_lows_mfi = df['MFI'].iloc[lows_idx[-2:]]
        
        bullish_div = (recent_lows_price.iloc[-1] < recent_lows_price.iloc[-2] and 
                      recent_lows_mfi.iloc[-1] > recent_lows_mfi.iloc[-2])
        
        highs_idx = argrelextrema(df['High'].values, np.greater, order=3)[0]
        bearish_div = False
        if len(highs_idx) >= 2:
            recent_highs_price = df['High'].iloc[highs_idx[-2:]]
            recent_highs_mfi = df['MFI'].iloc[highs_idx[-2:]]
            bearish_div = (recent_highs_price.iloc[-1] > recent_highs_price.iloc[-2] and 
                          recent_highs_mfi.iloc[-1] < recent_highs_mfi.iloc[-2])
        
        df['Body'] = np.abs(df['Close'] - df['Open'])
        atr = ta.ATR(high, low, close, 14)
        recent_bodies = df['Body'].tail(10)
        large_candle = recent_bodies.max() > atr[-1] * 1.5 if len(atr) > 0 and not np.isnan(atr[-1]) else False
        
        verified = False
        if signal == 'green' and (bullish_div or large_candle):
            verified = True
            print(f"✓ Green signal verified: Bullish Div={bullish_div}, Large Candle={large_candle}")
        elif signal == 'red' and (bearish_div or large_candle):
            verified = True
            print(f"✓ Red signal verified: Bearish Div={bearish_div}, Large Candle={large_candle}")
        else:
            print(f"✗ {signal} signal NOT verified by yfinance")
        
        return verified
    
    except Exception as e:
        print(f"yfinance verify error: {e}")
        print("Falling back to visual-only signal (risky)")
        return False

# ============ EXECUTION ============
def execute_trade(signal, button_pos):
    """Click buy/sell with human-like delays and offsets."""
    try:
        x = button_pos[0] + random.randint(-8, 8)
        y = button_pos[1] + random.randint(-5, 5)
        
        pyautogui.moveTo(x, y, duration=random.uniform(0.3, 0.8))
        time.sleep(random.uniform(0.4, 1.2))
        pyautogui.click()
        
        print(f"\n{'='*60}")
        print(f"TRADE EXECUTED: {signal.upper()} at {time.strftime('%H:%M:%S')}")
        print(f"Clicked at ({x}, {y}) - (COMPRA/VENDI button)")
        print(f"{'='*60}\n")
        
        return True
    except Exception as e:
        print(f"Execution error: {e}")
        return False

# ============ MAIN BOT LOOP ============
def main():
    """Main bot loop: scan, detect, verify, execute."""
    print("\n" + "="*60)
    print("FOREX BOT STARTED - Market Cipher B Trader")
    print("="*60)
    print(f"Chart Region: ({CHART_X}, {CHART_Y}, {CHART_W}x{CHART_H})")
    print(f"Indicator Region: {INDICATOR_REGION}")
    print(f"Buy Button: {BUY_BUTTON} | Sell Button: {SELL_BUTTON}")
    print(f"Pair: {FOREX_PAIR}")
    print(f"Platform: {platform.system()}")
    print(f"Failsafe: Press Ctrl+C to STOP")
    print("="*60)
    
    # Market Holiday Check
    now = datetime.now()
    if now.month == 1 and now.day == 1:
        print("⚠️ WARNING: Today is January 1st (New Year's Day).")
        print("   Forex markets are CLOSED. The bot will not find any new signals.")
        print("   Price action on your chart is likely frozen.\n")
    elif now.weekday() >= 5: # Saturday or Sunday
        print("⚠️ WARNING: It is the weekend.")
        print("   Forex markets are CLOSED. The bot will not find any new signals.\n")

    print("Starting in 5 seconds...\n")
    time.sleep(5)
    
    trade_count = 0
    last_signal_time = 0
    SIGNAL_COOLDOWN = 300
    
    while True:
        try:
            chart_img = capture_region(CHART_X, CHART_Y, CHART_W, CHART_H)
            dots_img = capture_region(*INDICATOR_REGION)
            
            if chart_img is None or dots_img is None:
                print(f"[{time.strftime('%H:%M:%S')}] Capture failed, retrying...")
                time.sleep(10)
                continue
            
            signal = detect_dots(dots_img)
            div_found = detect_divergence(chart_img)
            zone_found = detect_zone_retrace(chart_img)
            
            if signal:
                print(f"[{time.strftime('%H:%M:%S')}] Signal: {signal} | Divergence: {div_found} | Zone: {zone_found}")
            else:
                print(f"[{time.strftime('%H:%M:%S')}] Scanning... (No signal detected)")
            
            current_time = time.time()
            if (signal and div_found and zone_found and 
                (current_time - last_signal_time) > SIGNAL_COOLDOWN):
                
                print(f"[{time.strftime('%H:%M:%S')}] All visual conditions met. Verifying with yfinance...")
                
                if yfinance_verify(signal):
                    button = BUY_BUTTON if signal == 'green' else SELL_BUTTON
                    if execute_trade(signal, button):
                        trade_count += 1
                        last_signal_time = current_time
                        print(f"Total trades executed: {trade_count}")
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] Backend verification FAILED - skipping trade")
            
            scan_delay = 60 + random.uniform(-15, 15)
            time.sleep(scan_delay)
        
        except KeyboardInterrupt:
            print("\n\nBot stopped by user.")
            break
        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(10)

if __name__ == '__main__':
    main()
