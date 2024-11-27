import time  # Import the time module
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
import json
import random
import os

excluded_domains = ['wikipedia', 'instagram.com', 'facebook.com', "x.com", "twitter.com" ]
nr_of_links_clikable = 4

def get_queries(name):
    """Load the queries from queries.json."""
    with open('queries.json', 'r') as file:
        data = json.load(file)
        return data.get(name, [])

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
        for index, query in enumerate(queries):
            driver.get("https://www.google.com/?hl=en&gl=us")
            search_field = driver.find_element(By.TAG_NAME, "textarea")
            print(str(index)+" ", query)
            search_field.click()
            search_field.clear()  # Clear any previous text
            search_field.send_keys(query)
            search_field.send_keys(Keys.ENTER)
            time.sleep(random.uniform(5, 10))  # Wait randomly for not getting banned for crawling
            search_query_divs = locate_query_divs(driver)
            links = []
            # Iterate through each div and look for the <a> tag inside it
            for div in search_query_divs:
                # Find all <a> tags inside the current <div>
                a_tags = div.find_elements(By.TAG_NAME, "a")

                # Check if any <a> tags were found
                if a_tags:
                    for a_tag in a_tags:
                        link = a_tag.get_attribute("href")
                        text = a_tag.text
                        if not any(domain in link for domain in excluded_domains): 
                            print("Found <a> tag with href:", link)
                            print("Text inside <a> tag:", text)
                            links.append({"link": link, "name": text})
                else:
                    print("No <a> tags found inside this div.")
            links_clicked = 0      
            for index in range(len(links)):
                link = links[index]
                if links_clicked < nr_of_links_clikable: 
                    links_clicked +=1
                    clickLink(driver, link)       
    except NoSuchElementException:
        print("Search field not found.")
    except ElementNotInteractableException:
        print("Search field is not interactable.")

def locate_query_divs(driver):
    """
    Locates the divs of search query. Search results divs.
    
    Returns:
        WebElement or None
    """
    try:
        # Use XPath to find the span with exact text 'Top stories'
        top_stories_span = driver.find_element(By.XPATH, "//span[text()='Top stories']")
        # Navigate up 8 ancestor divs
        parent = top_stories_span.find_element(By.XPATH, "./ancestor::div[8]")
        # Find all divs of search query, first one represents 'Top stories'
        divs = parent.find_elements(By.XPATH, "./div")

        return divs[1:]

    except NoSuchElementException:
        print("Divs for this query have not been found.")
        return None

def save_links_to_json(links):
    """
    Saves links in the json
    """
     
    # Directory to save the JSON files
    output_dir = "neutral_queries_jsons"
    os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists

    # filename
    base_filename = "links"
    extension = ".json"
    counter = 0

    # Find filename, if doesn't exist create one
    while True:
        if counter == 0:
            output_file = os.path.join(output_dir, f"{base_filename}{extension}")
        else:
            output_file = os.path.join(output_dir, f"{base_filename}{counter}{extension}")
        if not os.path.exists(output_file):
            break
        counter += 1

    # Save the links to the unique JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(links, f, ensure_ascii=False, indent=4)

    print(f"Saved {len(links)} links to {output_file}")

def search_query_save_results(driver, neutral_queries):
    """Search each query in the Google search field. And save links to json."""
    # array to store links
    array = []
    try:        
        for index, query in enumerate(neutral_queries):
            driver.get("https://www.google.com/?hl=en&gl=us")
            search_field = driver.find_element(By.TAG_NAME, "textarea")
            search_field.click()
            search_field.clear()  # Clear any previous text
            search_field.send_keys(query)
            search_field.send_keys(Keys.ENTER)
            time.sleep(random.uniform(5, 10))  # Wait randomly for not getting banned for crawling
            search_query_divs = locate_query_divs(driver)
            links = []
            # Iterate through each div and look for the <a> tag inside it
            for div in search_query_divs:
                # Find all <a> tags inside the current <div>
                a_tags = div.find_elements(By.TAG_NAME, "a")

                # Check if any <a> tags were found
                if a_tags:
                    for a_tag in a_tags:
                        link = a_tag.get_attribute("href")
                        text = a_tag.text
                        if not any(domain in link for domain in excluded_domains):
                            links.append({"link": link, "name": text})
            array.append(links)

        # save neutral links to json, only single for now
        save_links_to_json(array)
            

    except NoSuchElementException:
        print("Search field not found.")
    except ElementNotInteractableException:
        print("Search field is not interactable.")

def clickLink(driver, link):
    """
    Function to click a link, wait 10 seconds, navigate back, and repeat.
    """
    try:
        #save current path 
        current_url = driver.current_url
        # Open the link
        driver.get(link['link'])
        
        # Optionally print the link that is being clicked
        print(f"Clicking link: {link['name']} ({link['link']})")
        
        # Wait for 10 seconds
        time.sleep(10)
        
        # Navigate back to the previous search page
        driver.get(current_url)
        
        # Wait for the page to load after navigating back
        time.sleep(2)
    
    except Exception as e:
        print(f"Error occurred while handling link {link['link']}: {e}")

def main():
    queries = get_queries('queries')
    
    driver = initialize_driver()
    
    # Navigate to Google with English settings - hl=en: Sets the language of the Google interface to English. gl=us: Sets the region to the United States as we want english results and be focused on US politics.
    driver.get("https://www.google.com/?hl=en&gl=us")
    accept_cookies(driver)
    
    # Perform searches for each query
    search_queries(driver, queries)
    
    #get neutral queries and save to the json
    neutral_queries = get_queries('neutral_queries')
    search_query_save_results(driver, neutral_queries)

    # Close the browser
    driver.quit()

if __name__ == "__main__":
    main()