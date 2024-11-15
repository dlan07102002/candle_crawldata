import html
import requests
from bs4 import BeautifulSoup
import csv

category_id = 1
product_id = 1
categories = {}
products = []
category_product = []
images = []

def fetch_products_from_page(url):
    global category_id, product_id
    global categories, products, category_product, images
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Cannot fetch data from {url}")
            return False
        
        soup = BeautifulSoup(response.text, "html.parser")
        ul = soup.find("ul", class_="collection-body__grid grid-column--one-quarter")
        if not ul:
            print("No product list found.")
            return False
        
        li_list = ul.find_all("li", class_="collection-body__grid-item")
        if not li_list:
            print("No products found.")
            return False
        
        for li in li_list:
            product_name = li.find("h4", class_="mb-1").get_text(strip=True) if li.find("h4") else "Unknown Product"
            list_price = li.find("p", class_="cl-product-card__price").get_text(strip=True) if li.find("p") else "0"
            description = li.find("p", class_="small-body mb-2").text if li.find("p", class_="small-body mb-2") else "No description"
            
            detail_description_tag = soup.find("div", class_="yotpo bottomLine")
            detail_description = detail_description_tag.get("data-description", "") if detail_description_tag else None

            image_url_tag = li.find("img", class_="lazyload")
            image_url = image_url_tag["data-src"] if image_url_tag else "No image"
            
            category = li.find("span").text if li.find("span") else "Uncategorized"
            if category not in categories:
                categories[category] = category_id
                category_id += 1

            if detail_description and "<p>" in detail_description:
                detail_description = detail_description[3:-4]
            
            images.append([product_id, image_url])
            category_product.append([product_id, categories[category]])
            products.append([product_id, product_name, list_price[1:], description, detail_description])
            product_id += 1
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

url = "https://www.candle-lite.com/collections/all-products"
page = 1
MAX_PAGES = 50  # Giới hạn số trang

while page <= MAX_PAGES:
    url_page = f"{url}?page={page}"
    res = fetch_products_from_page(url_page)
    
    if not res:  # Dừng vòng lặp nếu không tìm thấy sản phẩm
        print("No more products or unable to fetch data.")
        break

    page += 1

print(f"Scraping completed at page {page}.")