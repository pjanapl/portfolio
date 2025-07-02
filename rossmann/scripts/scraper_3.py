import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time, os, pickle

url_list = pd.read_pickle('../data/reviews_data_2.pkl')
pkl_path = "../data/reviews_missing_2.pkl"

url_to_visit_num  = len(url_list)
visited = 1

def scrape_reviews(product_url):
    global visited
    print("Scraping page: " + str(visited) + '/' +  str(url_to_visit_num))
    visited += 1
    options = Options()
    #options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-position=-1920,0")
    driver = webdriver.Chrome(options = options)
    driver.get(product_url)

    wait = WebDriverWait(driver, 10)

    reviews = []

    try:
        accept_cookies_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        accept_cookies_btn.click()
        time.sleep(2)
        
        opinions_tab = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[id="opinions"]')
            )
        )

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", opinions_tab)
        time.sleep(1)
        opinions_tab.click()
        time.sleep(2)

        while True:
            try:
                show_more_button = wait.until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, '[data-testid="show-more-opinions-button"]')
                    )
                )
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", show_more_button)
                time.sleep(1)
                show_more_button.click()
                time.sleep(1)

            except TimeoutException:
                break

        opinion_blocks = driver.find_elements(By.CSS_SELECTOR, '[class="styles-module_opinion--1uo0v"]')

        for op in opinion_blocks:
            try:
                rating_raw = op.find_element(
                    By.CSS_SELECTOR, '[class="styles-module_review--hsMfO"]').text.strip()
                rating = float(rating_raw[0]) if rating_raw else None
            except:
                rating = None

            try:
                author = op.find_element(
                    By.CSS_SELECTOR, '[class="styles-module_name--hOlCo"]').text.strip()
            except:
                author = ""

            try:
                date = op.find_element(By.CSS_SELECTOR, '.styles-module_date--kdvWk').text.strip()
            except:
                date = ""

            try:
                content = op.find_element(By.CSS_SELECTOR, '[class="styles-module_comment--Jt6+s text-break  "]').text.strip()
            except:
                content = ""

            reviews.append({
                "product_url": product_url,
                "rating": rating,
                "author": author,
                "date": date,
                "content": content
            })

    finally:
        driver.quit()

    return reviews

for url in url_list:
    try:
        if os.path.exists(pkl_path):
            with open(pkl_path, "rb") as f:
                all_reviews = pickle.load(f)
        else:
            all_reviews = []

        new_reviews = scrape_reviews(url)
        all_reviews.extend(new_reviews)
        with open(pkl_path, "wb") as f:
            pickle.dump(all_reviews, f)

    except Exception as e:
        print(f"[BŁĄD] Przy {url}: {e}")

print("ZAKOŃCZONO")