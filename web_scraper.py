from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Selenium WebDriver
driver = webdriver.Chrome()

def open_url(url):
    """
    Opens a URL using Selenium and returns a BeautifulSoup object for the page source.
    """
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup
    except Exception as e:
        logging.error(f"Error loading URL {url}: {e}")
        return None

def clean_cell(text):
    """
    Cleans a text cell by removing unwanted characters.
    """
    replacements = {'\n': ' ', '*': ' ', '\u2019': "'", '  ': ' '}
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.strip()

def export_to_json(data, file_name):
    """
    Exports a list of dictionaries to a JSON file.
    """
    if not os.path.exists("info_folder"):
        os.makedirs("info_folder")

    df = pd.DataFrame(data)
    for col in df.columns:
        df[col] = df[col].apply(clean_cell)

    file_path = os.path.join("info_folder", file_name)
    df.to_json(file_path, orient='records', force_ascii=False)
    logging.info(f"Data successfully exported to {file_path}")

def return_product_page_urls():
    """
    Returns a list of product page URLs by parsing the product category pages.
    """
    category_urls = [
        "https://eco-essentials.com/product-category/men",  
        "https://eco-essentials.com/product-category/women", 
        "https://eco-essentials.com/product-category/fabrics", 
        "https://eco-essentials.com/product-category/accessories"
    ]
    product_page_urls = []

    for url in category_urls:
        page = open_url(url)
        if not page:
            continue

        ul_element = page.find('div', class_="columns-3").find('ul', class_="products columns-3")
        if ul_element:
            for list_element in ul_element.find_all('li'):
                a_tag = list_element.find('a')
                if a_tag:
                    product_page_urls.append(a_tag['href'])

    logging.info(f"Found {len(product_page_urls)} product URLs.")
    return product_page_urls


def extract_text(selector, page):
    element = page.select_one(selector)
    return element.text.strip() if element else ""
    
def search_product_page(url):
    """
    Extracts product details from a given product page URL.
    """
    page = open_url(url)
    if not page:
        return {}

    product_info = {
        "SKU": extract_text("span.sku", page),
        "Summary": extract_text("div.woocommerce-product-details__short-description", page),
        "Description": extract_text("div.woocommerce-Tabs-panel--description p", page),
        "Additional_Info": extract_text("div.woocommerce-Tabs-panel--additional_information", page),
        "Price": extract_text("div.summary.entry-summary p.price bdi", page).replace("$CAD ", ""),
        "URL": url
    }

    return product_info

def search_all_product_pages():
    """
    Scrapes all product pages and exports the data to a JSON file.
    """
    product_page_urls = return_product_page_urls()
    product_pages_info = []

    for product_url in product_page_urls:
        product_info = search_product_page(product_url)
        if product_info:
            product_pages_info.append(product_info)
        time.sleep(1)  # Rate-limiting to avoid server overload

    export_to_json(product_pages_info, "product.json")

def return_blog_page_urls(page_count):
    """
    Returns a list of blog page URLs by parsing the blog listing pages.
    """
    base_url = "https://eco-essentials.com/blog/page/"
    blog_urls = []

    for i in range(1, page_count + 1):
        page = open_url(f"{base_url}{i}")
        if not page:
            continue

        articles = page.find_all('article')
        for article in articles:
            a_tag = article.find('a')
            if a_tag:
                blog_urls.append(a_tag['href'])

    logging.info(f"Found {len(blog_urls)} blog URLs.")
    return blog_urls

def search_blog_page(url):
    """
    Extracts blog details from a given blog page URL.
    """
    page = open_url(url)
    if not page:
        return {}

    blog_info = {
        "Title": extract_text("main.site-main h1", page),
        "Date Created": extract_text("main.site-main time", page),
        "Content": extract_text("main.site-main div.entry-content", page),
        "URL": url
    }

    return blog_info

def search_all_blog_pages(page_count):
    """
    Scrapes all blog pages and exports the data to a JSON file.
    """
    blog_urls = return_blog_page_urls(page_count)
    blog_info_list = []

    for blog_url in blog_urls:
        blog_info = search_blog_page(blog_url)
        if blog_info:
            blog_info_list.append(blog_info)
        time.sleep(1)  # Rate-limiting to avoid server overload

    export_to_json(blog_info_list, "blog.json")

# Uncomment to execute scraping
search_all_product_pages()
search_all_blog_pages(12)

# Ensure the WebDriver is properly closed
driver.quit()
