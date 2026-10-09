import http.server
import socketserver
import threading
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options as EdgeOptions

# 1. Start HTTP Server on port 8765
PORT = 8765
Handler = http.server.SimpleHTTPRequestHandler

class QuietHandler(Handler):
    def log_message(self, format, *args):
        pass

server = socketserver.TCPServer(('127.0.0.1', PORT), QuietHandler)
server_thread = threading.Thread(target=server.serve_forever)
server_thread.daemon = True
server_thread.start()
print(f'Server running at http://127.0.0.1:{PORT}')

# 2. Configure headless Edge
options = EdgeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Edge(options=options)
driver.get(f'http://127.0.0.1:{PORT}/index.html')
time.sleep(2)

print('Page title:', driver.title)

# Check slides count
slides = driver.find_elements(By.CSS_SELECTOR, '.slide')
print('Total slides found:', len(slides))
assert len(slides) == 12, f'Expected 12 slides, found {len(slides)}'

# Helper to get state
def get_state():
    return driver.execute_script('''
        return {
            slideIndex: window.presentation.currentSlideIndex,
            step: window.presentation.currentStep,
            maxSteps: window.presentation.slideStepCounts[window.presentation.currentSlideIndex]
        };
    ''')

state = get_state()
print('Initial state:', state)
assert state['slideIndex'] == 0 and state['step'] == 0

body = driver.find_element(By.TAG_NAME, 'body')

# Test Spacebar advance
body.send_keys(Keys.SPACE)
time.sleep(0.4)
state = get_state()
print('After 1 Spacebar:', state)
assert state['slideIndex'] == 0 and state['step'] == 1

body.send_keys(Keys.SPACE)
time.sleep(0.4)
state = get_state()
print('After 2 Spacebars:', state)
assert state['slideIndex'] == 0 and state['step'] == 2

# Advance to slide 1 (Slide 2), step 0
body.send_keys(Keys.SPACE)
time.sleep(0.6)
state = get_state()
print('After 3 Spacebars (next slide):', state)
assert state['slideIndex'] == 1 and state['step'] == 0

# Test reverse with Left Arrow
body.send_keys(Keys.ARROW_LEFT)
time.sleep(0.5)
state = get_state()
print('After Left Arrow (returned to slide 0, step 2):', state)
assert state['slideIndex'] == 0 and state['step'] == 2

# Test reverse step on slide 0
body.send_keys(Keys.ARROW_LEFT)
time.sleep(0.4)
state = get_state()
print('After Left Arrow (step backward to step 1):', state)
assert state['slideIndex'] == 0 and state['step'] == 1

# Forward to Slide 4 (Handshake)
driver.execute_script('window.presentation.goToSlide(3, 0);')
time.sleep(0.4)
print('Jumped to Slide 4 (Handshake):', get_state())

for s in range(3):
    body.send_keys(Keys.SPACE)
    time.sleep(0.3)
    print(f'Handshake step {s+1}:', get_state())

os.makedirs('test_screenshots', exist_ok=True)
driver.save_screenshot('test_screenshots/slide_4_handshake.png')
print('Saved test_screenshots/slide_4_handshake.png')

# Slide 6 (TCP Delivery)
driver.execute_script('window.presentation.goToSlide(5, 3);')
time.sleep(0.4)
driver.save_screenshot('test_screenshots/slide_6_delivery.png')
print('Saved test_screenshots/slide_6_delivery.png')

# Slide 7 (UDP Gaming)
driver.execute_script('window.presentation.goToSlide(6, 3);')
time.sleep(0.4)
driver.save_screenshot('test_screenshots/slide_7_gaming.png')
print('Saved test_screenshots/slide_7_gaming.png')

# Slide 8 (UDP Delivery with packet loss)
driver.execute_script('window.presentation.goToSlide(7, 4);')
time.sleep(0.4)
driver.save_screenshot('test_screenshots/slide_8_udp_delivery.png')
print('Saved test_screenshots/slide_8_udp_delivery.png')

# Slide 10 (Comparison Table)
driver.execute_script('window.presentation.goToSlide(9, 3);')
time.sleep(0.4)
driver.save_screenshot('test_screenshots/slide_10_comparison.png')
print('Saved test_screenshots/slide_10_comparison.png')

# Slide 11 (Design Choice)
driver.execute_script('window.presentation.goToSlide(10, 3);')
time.sleep(0.4)
driver.save_screenshot('test_screenshots/slide_11_choice.png')
print('Saved test_screenshots/slide_11_choice.png')

# Slide 12 (Takeaway & Conclusion)
driver.execute_script('window.presentation.goToSlide(11, 2);')
time.sleep(0.4)
driver.save_screenshot('test_screenshots/slide_12_takeaway.png')
print('Saved test_screenshots/slide_12_takeaway.png')

# Test Overview Modal
body.send_keys('o')
time.sleep(0.4)
overview_open = driver.execute_script('return document.getElementById("overview-modal").classList.contains("open");')
print('Overview open:', overview_open)
assert overview_open == True
driver.save_screenshot('test_screenshots/overview_modal.png')
print('Saved test_screenshots/overview_modal.png')

body.send_keys(Keys.ESCAPE)
time.sleep(0.3)
overview_open = driver.execute_script('return document.getElementById("overview-modal").classList.contains("open");')
assert overview_open == False
print('Overview closed with ESC.')

driver.quit()
server.shutdown()
print('*** ALL VALIDATION CHECKS PASSED PERFECTLY! ***')
