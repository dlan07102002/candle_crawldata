import html
import requests
# Beautiful soup help analyzes and extract HTML and XML
from bs4 import BeautifulSoup
import csv
import time
category_id = 1
product_id = 1
categories = {}
products = []
category_product = []
images = []


def fetch_products_from_page(url):
    global category_id, product_id  # Đảm bảo sử dụng biến toàn cục
    global categories, products, category_product, images
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Cannot fetch data from {url}")
            return 
        
        soup = BeautifulSoup(response.text, "html.parser")
    
        ul = soup.find("ul", class_="collection-body__grid grid-column--one-quarter")
        if ul:
            li_list = ul.find_all("li", class_="collection-body__grid-item")
           
            for li in li_list:
                product_name = li.find("h4", class_="mb-1").get_text(strip=True)
                list_price = li.find("p", class_="cl-product-card__price").get_text(strip=True)
                
                description_tag = soup.find("div", class_="yotpo bottomLine")
               
                description = None
                # Kiểm tra và lấy dữ liệu description từ thuộc tính data-description
                if description_tag:
                    description_data = description_tag["data-description"]
                    description = description_tag["data-description"]
                    # Tạo BeautifulSoup để parse nội dung HTML trong data-description
                    inner_soup = BeautifulSoup(description_data, "html.parser")

                    # Lấy nội dung từ thẻ <span> bên trong
                    span_tag = inner_soup.find("span", {"data-sheets-value": True})
                   
                    if span_tag:
                        description = span_tag.get_text(strip=True)

                #     else:
                #         print("Can not find description")
                # else:
                #     print("Description is null")
                
                image_url_tag = li.find("img", class_="lazyload")
                image_url = image_url_tag["data-src"] if image_url_tag else "No image"
                
                category = li.find("span").text
                
                if category not in categories:
                    categories[category] = category_id
                    category_id += 1
                
              
                if(description.__contains__("<p>")):
                    description = description[3:-4]
                    
                images.append([product_id, image_url])
                category_product.append([product_id, categories[category]])
                
                products.append([product_id, product_name, list_price[1:], description])
                
                product_id += 1
                
        return "run"
                
            
    except Exception as e:
        print(e)

        
url = "https://www.candle-lite.com/collections/all-products"

page = 1
category_product = []   

while True:
    # Crawl each page
    url_page = f"{url}?page={page}"
    
    res = fetch_products_from_page(url_page)
   
    if not res:
        print("DONE")
        break

    page += 1
    time.sleep(1)
    
# Write products to .csv

with open('products.csv', mode='w', newline='', encoding='utf-8') as product_file:
    writer = csv.writer(product_file)
    writer.writerow(["Product Id", "Product Name", "List Price", "Description"])
    writer.writerows(products)

with open('categories.csv', mode='w', newline='', encoding='utf-8') as category_file:
    writer = csv.writer(category_file)
    writer.writerow(["Category Name", "Category Id"])
    for key, value in categories.items():
        writer.writerow([key, value])
        
with open('category_product.csv', mode='w', newline='', encoding='utf-8') as category_product_file:
    writer = csv.writer(category_product_file)
    writer.writerow(["Product Id", "Category Id"])
    writer.writerows(category_product)

with open('images.csv', mode='w', newline='', encoding='utf-8') as image_file:
    writer = csv.writer(image_file)
    writer.writerow(["Product Id", "Link"])
    writer.writerows(images)



