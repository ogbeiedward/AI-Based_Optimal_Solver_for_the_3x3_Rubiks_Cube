"""
Take screenshots of the web UI for thesis figures 7.1, 7.2, 7.3
Requires Selenium and a running visualization server on http://localhost:5000
"""
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

FIG_DIR = "docs/figures"
os.makedirs(FIG_DIR, exist_ok=True)

# Configure Chrome options for headless screenshot
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--window-size=1400,900")

try:
    driver = webdriver.Chrome(options=chrome_options)

    print("Opening visualization at http://localhost:5000...")
    driver.get("http://localhost:5000")
    time.sleep(3)  # Wait for page load

    # Screenshot 1: Initial solved cube (Fig 7.1)
    print("Taking Fig 7.1: Initial solved cube state...")
    driver.save_screenshot(os.path.join(FIG_DIR, "screenshot_7_1_solved.png"))

    # Scramble the cube - click scramble button
    print("Scrambling cube...")
    try:
        scramble_btn = driver.find_element(By.ID, "scramble-btn")
        scramble_btn.click()
        time.sleep(2)
    except:
        print("  (Scramble button not found, continuing)")

    # Screenshot 2: Scrambled cube
    print("Taking Fig 7.2: Scrambled cube...")
    driver.save_screenshot(os.path.join(FIG_DIR, "screenshot_7_2_scrambled.png"))

    # Click Kociemba solve
    print("Starting Kociemba solve...")
    try:
        kociemba_btn = driver.find_element(By.ID, "solve-kociemba-btn")
        kociemba_btn.click()
        time.sleep(3)  # Wait for solve animation
    except:
        print("  (Kociemba button not found, trying alternate selector)")
        try:
            kociemba_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Kociemba')]")
            kociemba_btn.click()
            time.sleep(3)
        except:
            print("  (Could not find Kociemba button)")

    # Screenshot 3: During Kociemba solve
    print("Taking Fig 7.3: Kociemba solve in progress...")
    driver.save_screenshot(os.path.join(FIG_DIR, "screenshot_7_3_solving.png"))

    # Try to find and click AI Beam button
    print("Attempting to switch to AI solver...")
    try:
        ai_beam_btn = driver.find_element(By.ID, "solve-ai-beam-btn")
        ai_beam_btn.click()
        time.sleep(3)
        print("Taking Fig 7.4: AI beam search solve...")
        driver.save_screenshot(os.path.join(FIG_DIR, "screenshot_7_4_ai_beam.png"))
    except:
        print("  (AI button not found, skipping)")

    driver.quit()
    print("\nScreenshots captured successfully!")
    print(f"Saved to {FIG_DIR}/")

except Exception as e:
    print(f"Error: {e}")
    print("Make sure:")
    print("  1. Chrome/Chromium is installed")
    print("  2. Visualization server is running (python visualization/server.py)")
    print("  3. selenium is installed (pip install selenium)")
