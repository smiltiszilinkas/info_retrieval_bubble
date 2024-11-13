import time  # Import the time module
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException  # Import the exception
import json
import random


# Specify the path to your ChromeDriver
service = Service('chromedriver.exe')

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-logging")  # Disable logging
chrome_options.add_argument("--disable-perfetto")  # Disable performance tracing

# Initialize the Chrome WebDriver using the Service object
driver = webdriver.Chrome(service=service, options=chrome_options)

# Navigate to a website
driver.get("https://www.google.com")

# Wait for the page to load (you may need to add some wait for the element to appear)
driver.implicitly_wait(10)  # This will wait up to 10 seconds for elements to appear
time.sleep(5)

# Close the browser after a few seconds
driver.quit()
