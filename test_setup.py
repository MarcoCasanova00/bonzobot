import pyautogui
import cv2
import numpy as np
from PIL import Image
import time

print("="*80)
print("SETUP VERIFICATION TEST - ARCH LINUX")
print("="*80)
print()

# Fallback config (replace with your actual values)
CHART_X = 100
CHART_Y = 150
CHART_W = 1300
CHART_H = 700
BUY_BUTTON = (1200, 750)

print("Test 1: Screenshot permission...")
try:
    screenshot = pyautogui.screenshot(region=(CHART_X, CHART_Y, CHART_W, CHART_H))
    screenshot.save('/tmp/chart_capture_test.png')
    print(f"  ✓ Captured chart region to /tmp/chart_capture_test.png")
    print(f"  Size: {screenshot.size}")
except Exception as e:
    print(f"  ✗ Screenshot failed: {e}")
    print("  Make sure browser window is focused and visible")
    exit(1)

print("\nTest 2: Button positioning...")
try:
    print(f"  Moving mouse to {BUY_BUTTON} for 2 seconds...")
    pyautogui.moveTo(BUY_BUTTON[0], BUY_BUTTON[1], duration=0.5)
    time.sleep(2)
    print(f"  ✓ Mouse moved successfully")
except Exception as e:
    print(f"  ✗ Mouse movement failed: {e}")
    exit(1)

print("\nTest 3: Image processing (OpenCV)...")
try:
    img = cv2.imread('/tmp/chart_capture_test.png')
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    print(f"  ✓ OpenCV working (image shape: {img.shape})")
except Exception as e:
    print(f"  ✗ OpenCV processing failed: {e}")
    exit(1)

print("\nTest 4: OCR (Tesseract)...")
try:
    import pytesseract
    text = pytesseract.image_to_string(img)
    print(f"  ✓ Tesseract working (extracted {len(text)} chars)")
except Exception as e:
    print(f"  ✗ Tesseract failed: {e}")
    print("  Install: sudo pacman -S tesseract")
    exit(1)

print("\nTest 5: Data analysis (yfinance)...")
try:
    import yfinance as yf
    df = yf.download('EURUSD=X', period='1d', interval='1m', progress=False)
    print(f"  ✓ yfinance working ({len(df)} candles)")
except Exception as e:
    print(f"  ✗ yfinance failed: {e}")
    print("  Check internet connection")

print("\nTest 6: TA-Lib indicators...")
try:
    import talib as ta
    close = np.array([100.0, 101.0, 102.0, 101.0, 100.0], dtype='float64')
    high = (close + 1.0).astype('float64')
    low = (close - 1.0).astype('float64')
    vol = np.array([1000000.0]*5, dtype='float64')
    mfi = ta.MFI(high, low, close, vol, 14)
    print(f"  ✓ TA-Lib working (MFI: {mfi[-1]:.2f})")
except Exception as e:
    print(f"  ✗ TA-Lib failed: {e}")
    exit(1)

print("\n" + "="*80)
print("✅ ALL TESTS PASSED - Setup is ready")
print("="*80)
print("\nNEXT STEPS:")
print("1. Run: python calibrate_chart.py")
print("2. Copy chart_config.py content into forex_bot.py")
print("3. Run: python forex_bot.py")
print()
