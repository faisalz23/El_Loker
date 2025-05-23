from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from pymongo import MongoClient
import logging
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_jobstreet(category):
    try:
        # Setup koneksi MongoDB
        client = MongoClient('mongodb+srv://eL_loker:elloker123@bigdata.fukimpx.mongodb.net/?retryWrites=true&w=majority&appName=BigData')
        logger.info("Connected to MongoDB")
        
        db = client['jobstreet2']
        collection = db['job']
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-notifications')
        
        # Initialize the Chrome WebDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        logger.info("WebDriver initialized")
        
        # JobStreet Indonesia search URL for the specified category
        url = f'https://www.jobstreet.co.id/id/{category}-jobs'
        logger.info(f"Fetching data from {url}")
        
        # Load the page
        driver.get(url)
        
        # Wait for initial page load
        time.sleep(5)
        
        # Handle cookie consent if present
        try:
            cookie_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-automation="cookie-consent-accept"]'))
            )
            cookie_button.click()
            time.sleep(2)
        except:
            logger.info("No cookie consent found or already accepted")
        
        # Scroll to load more content
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        max_scroll_attempts = 10  # Maximum number of scroll attempts
        
        while scroll_attempts < max_scroll_attempts:
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Wait for content to load
            
            # Calculate new scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            
            # Check if we've reached the bottom
            if new_height == last_height:
                scroll_attempts += 1
                if scroll_attempts >= 3:  # If we haven't seen new content in 3 attempts, break
                    break
            else:
                scroll_attempts = 0  # Reset counter if we found new content
                last_height = new_height
        
        # Wait for job cards to load
        wait = WebDriverWait(driver, 20)
        job_cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article[data-card-type="JobCard"]')))
        logger.info(f"Found {len(job_cards)} job cards for {category} after scrolling")
        
        for card in job_cards:
            try:
                # Extract job information
                try:
                    title = card.find_element(By.CSS_SELECTOR, 'h1[data-automation="jobTitle"]').text.strip()
                except:
                    try:
                        title = card.find_element(By.CSS_SELECTOR, 'h1').text.strip()
                    except:
                        try:
                            title = card.find_element(By.CSS_SELECTOR, 'a[data-automation="jobTitle"]').text.strip()
                        except:
                            title = "Not specified"
                    
                try:    
                    company = card.find_element(By.CSS_SELECTOR, 'a[data-automation="jobCompany"]').text.strip()
                except:
                    try:
                        company = card.find_element(By.CSS_SELECTOR, '[data-automation="company-name"]').text.strip()
                    except:
                        company = "Not specified"
                    
                try:
                    location = card.find_element(By.CSS_SELECTOR, 'a[data-automation="jobLocation"]').text.strip()
                except:
                    try:
                        location = card.find_element(By.CSS_SELECTOR, '[data-automation="job-location"]').text.strip()
                    except:
                        location = "Not specified"
                    
                try:
                    salary = card.find_element(By.CSS_SELECTOR, 'span[data-automation="jobSalary"]').text.strip()
                except:
                    try:
                        salary = card.find_element(By.CSS_SELECTOR, '[data-automation="job-salary"]').text.strip()
                    except:
                        salary = "Not specified"
                    
                try:
                    job_type = card.find_element(By.CSS_SELECTOR, 'span[data-automation="jobType"]').text.strip()
                except:
                    try:
                        job_type = card.find_element(By.CSS_SELECTOR, '[data-automation="job-type"]').text.strip()
                    except:
                        job_type = "Not specified"
                    
                try:
                    posted_date = card.find_element(By.CSS_SELECTOR, 'span[data-automation="jobListingDate"]').text.strip()
                except:
                    try:
                        posted_date = card.find_element(By.CSS_SELECTOR, '[data-automation="job-posted-date"]').text.strip()
                    except:
                        posted_date = "Not specified"
                
                if title != "Not specified" or company != "Not specified":
                    job_data = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'salary': salary,
                        'job_type': job_type,
                        'posted_date': posted_date,
                        'category': category,
                        'source': 'JobStreet'
                    }
                    
                    # Insert job data
                    collection.insert_one(job_data)
                    logger.info(f"Inserted job: {job_data['title']} at {job_data['company']} in category {category}")
                else:
                    logger.warning("Skipping job card with insufficient information")
                    
            except Exception as e:
                logger.error(f"Error processing job card: {str(e)}")
                continue
        
        logger.info(f"Data scraping completed for category: {category}")
        
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
    finally:
        if 'driver' in locals():
            driver.quit()
            logger.info("WebDriver closed")
        if 'client' in locals():
            client.close()
            logger.info("MongoDB connection closed")

if __name__ == "__main__":
    # List of job categories to scrape
    categories = [
        'software-engineer',
        'data-scientist',
        'marketing',
        'sales',
        'accounting',
        'human-resources',
        'customer-service',
        'design',
        'education',
        'healthcare',
        'finance',
        'management',
        'engineering',
        'information-technology',
        'manufacturing',
        'retail',
        'transportation',
        'hospitality',
        'legal',
        'media'
    ]
    
    for category in categories:
        scrape_jobstreet(category)
        time.sleep(5)  # Add delay between categories to avoid overwhelming the server
