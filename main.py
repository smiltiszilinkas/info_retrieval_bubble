import time  # Import the time module
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException  # Import the exception
import json
import random

def get_queries():
    """Load the queries from queries.json."""
    with open('queries.json', 'r') as file:
        data = json.load(file)
        return data.get("queries", [])

def initialize_driver():
    """Initialize and configure the Chrome WebDriver."""
    service = Service('chromedriver.exe')
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--disable-perfetto")

    # Set browser language to English (US)
    chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
    
    
    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def accept_cookies(driver):
    """Accept cookies if the cookie consent button is present."""
    try:
        # Wait for the element
        driver.implicitly_wait(5)
        only_necessary_cookies = driver.find_element(By.ID, "W0wltc")
        only_necessary_cookies.click()
    except NoSuchElementException:
        print("Cookie consent button not found.")
    except ElementNotInteractableException:
        print("Cookie consent button is not interactable.")

def search_queries(driver, queries):
    """Search each query in the Google search field."""
    # Locate the search field (first <textarea> element)
    try:
        search_field = driver.find_element(By.TAG_NAME, "textarea")
        
        for index, query in enumerate(queries):
            if index == 0: 
                print(str(index)+" ", query)
                search_field.click()
                search_field.clear()  # Clear any previous text
                search_field.send_keys(query)
                search_field.send_keys(Keys.ENTER)
                time.sleep(random.uniform(5, 10))  # Wait randomly for not getting banned for crawling
                top_stories_divs = locate_top_stories_divs(driver)
                links = []
                # Iterate through each div and look for the <a> tag inside it
                for div in top_stories_divs:
                    # Find all <a> tags inside the current <div>
                    a_tags = div.find_elements(By.TAG_NAME, "a")

                    # Check if any <a> tags were found
                    if a_tags:
                        for a_tag in a_tags:
                            link = a_tag.get_attribute("href")
                            text = a_tag.text
                            print("Found <a> tag with href:", link)
                            print("Text inside <a> tag:", text)
                            links.append({"link": link, "name": text})
                    else:
                        print("No <a> tags found inside this div.")      
                for link in links:
                    clickLink(driver, link)       
            else:
                time.sleep(random.uniform(500, 1000))  # Wait randomly between searches for realism
                print("Else")
    except NoSuchElementException:
        print("Search field not found.")
    except ElementNotInteractableException:
        print("Search field is not interactable.")

def locate_top_stories_divs(driver):
    """
    Locate the parent div five levels up from the 'Top stories' span. Returns divs 0 - main news, 1 also in the news, 2- more news
    
    Returns:
        WebElement or None
    """
    try:
        # Use XPath to find the span with exact text 'Top stories'
        top_stories_span = driver.find_element(By.XPATH, "//span[text()='Top stories']")
        # Navigate up five ancestor divs
        top_stories_parent = top_stories_span.find_element(By.XPATH, "./ancestor::div[5]")
         # Find all divs within top_stories_parent
        divs_within_top_stories = top_stories_parent.find_elements(By.XPATH, "./div")
        # Check if there is a second div within top_stories_parent
        if len(divs_within_top_stories) >= 2:
            second_div = divs_within_top_stories[1]
            g_section_element = second_div.find_element(By.XPATH, "./*")
            g_stories_divs = g_section_element.find_elements(By.XPATH, "./div")

            
            return g_stories_divs # 0 div main news, 1 div  also in the news, 2 more news
        else:
            print("The second div inside 'top_stories_parent' was not found.")
            return None

    except NoSuchElementException:
        print("'Top stories' span or its ancestor div not found.")
        return None

def clickLink(driver, link):
    """
    Function to click a link, wait 10 seconds, navigate back, and repeat.
    """
    try:
        # Open the link
        driver.get(link['link'])
        
        # Optionally print the link that is being clicked
        print(f"Clicking link: {link['name']} ({link['link']})")
        
        # Wait for 10 seconds
        time.sleep(10)
        
        # Navigate back to the previous page
        driver.back()
        
        # Wait for the page to load after navigating back
        time.sleep(2)  # Adjust as needed based on your website's load time
    
    except Exception as e:
        print(f"Error occurred while handling link {link['link']}: {e}")

def main():
    queries = get_queries()
    
    driver = initialize_driver()
    
    # Navigate to Google with English settings - hl=en: Sets the language of the Google interface to English. gl=us: Sets the region to the United States as we want english results and be focused on US politics.
    driver.get("https://www.google.com/?hl=en&gl=us")
    
    accept_cookies(driver)
    
    # Perform searches for each query
    search_queries(driver, queries)
    
    # Close the browser
    driver.quit()

if __name__ == "__main__":
    main()