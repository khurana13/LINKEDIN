from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

class LinkedInBot:
    def __init__(self, update_status_callback=None):
        """Initialize the LinkedIn automation bot"""
        self.driver = None
        self.update_status = update_status_callback or (lambda msg: print(msg))
        self.is_running = False
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger('linkedin_bot')

    def initialize_driver(self):
        """Set up the Chrome browser driver"""
        try:
            self.update_status("Initializing Chrome driver...")
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            return True
        except Exception as e:
            self.update_status(f"Error initializing driver: {e}")
            self.logger.error(f"Driver initialization error: {e}")
            return False

    def login(self, email, password):
        """Log in to LinkedIn with provided credentials"""
        try:
            self.update_status("Opening LinkedIn login page...")
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(2)

            self.update_status("Entering login credentials...")
            username_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")

            username_field.send_keys(email)
            password_field.send_keys(password)

            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()

            # Wait for login to complete
            time.sleep(3)

            # Check if login was successful
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "global-nav"))
                )
                self.update_status("✅ Login successful!")
                self.logger.info("Login successful")
                return True
            except:
                self.update_status("❌ Login failed. Please check your credentials.")
                self.logger.error("Login failed")
                return False

        except Exception as e:
            self.update_status(f"Error during login: {e}")
            self.logger.error(f"Login error: {e}")
            return False

    def search_and_connect(self, search_query, num_requests, include_note=False, custom_note=""):
        """Search for profiles and send connection requests"""
        if not self.driver:
            self.update_status("⚠️ Browser not initialized. Please log in first.")
            return False

        try:
            # Search for the query
            self.update_status(f"🔎 Searching for '{search_query}'...")
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[contains(@class, 'search-global-typeahead__input')]"))
            )
            search_box.clear()
            search_box.send_keys(search_query)
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)

            # Navigate to the People tab
            self.update_status("📍 Navigating to People tab...")
            try:
                people_tab = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'People')]"))
                )
                people_tab.click()
                time.sleep(3)
            except Exception as e:
                self.update_status("⚠️ Could not find People tab, may already be on results")
                self.logger.warning(f"People tab navigation: {e}")

            self.is_running = True
            requests_sent = 0

            while requests_sent < num_requests and self.is_running:
                # Find "Connect" buttons
                connect_buttons = self.driver.find_elements(By.XPATH, "//button[contains(., 'Connect')]")

                if not connect_buttons:
                    self.update_status("🔄 No Connect buttons found, scrolling...")
                    for _ in range(3):  # Smooth short scrolls
                        self.driver.execute_script("window.scrollBy(0, 300);")
                        time.sleep(1)

                    time.sleep(2)  # Wait for elements to load
                    continue  # Retry finding buttons

                self.update_status(f"📌 Found {len(connect_buttons)} potential connections")

                for button in connect_buttons:
                    if requests_sent >= num_requests or not self.is_running:
                        break

                    try:
                        # Scroll to button smoothly
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                        time.sleep(1)

                        # Click "Connect" button
                        button.click()
                        time.sleep(2)

                        # Handle note if required
                        if include_note:
                            try:
                                add_note_button = WebDriverWait(self.driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Add a note')]"))
                                )
                                add_note_button.click()
                                
                                note_text = custom_note if custom_note else "Hi, I'd like to connect with you!"
                                note_field = WebDriverWait(self.driver, 5).until(
                                    EC.presence_of_element_located((By.XPATH, "//textarea[@name='message']"))
                                )
                                note_field.send_keys(note_text)

                                send_button = WebDriverWait(self.driver, 5).until(
                                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Send')]"))
                                )
                                send_button.click()
                                self.update_status("✅ Sent request with note")
                            except Exception as e:
                                self.logger.warning(f"Note addition failed: {e}")
                                send_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Send')]")
                                send_button.click()
                                self.update_status("✅ Sent request without note (note addition failed)")
                        else:
                            send_button = self.driver.find_element(By.XPATH, "//button[contains(., 'Send')]")
                            send_button.click()
                            self.update_status("✅ Sent request without note")

                        requests_sent += 1
                        self.update_status(f"📩 Progress: {requests_sent}/{num_requests} requests sent")
                        time.sleep(3)

                    except Exception as e:
                        self.logger.error(f"⚠️ Error clicking 'Connect': {e}")
                        self.update_status("⚠️ Skipping a failed request...")
                        continue

            self.update_status(f"🎉 Successfully sent {requests_sent} connection requests!")
            self.is_running = False
            return True

        except Exception as e:
            self.update_status(f"❌ Error in search and connect process: {e}")
            self.logger.error(f"Search and connect error: {e}")
            self.is_running = False
            return False

    def stop(self):
        """Stop the automation process"""
        self.is_running = False
        self.update_status("⏹️ Stopping automation...")

    def close(self):
        """Close the browser and clean up"""
        if self.driver:
            self.update_status("🚪 Closing browser...")
            try:
                self.driver.quit()
                self.driver = None
                self.update_status("✅ Browser closed")
            except Exception as e:
                self.update_status(f"⚠️ Error closing browser: {e}")
