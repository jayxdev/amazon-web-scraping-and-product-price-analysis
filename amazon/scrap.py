import requests
from bs4 import BeautifulSoup
import sys
import time
import csv
import random

search_query = 'iphone'  # Search query
countries_domain = ["in", "co.uk", "com", "ca", "de", "fr", "it", "es", "jp", "au", "nl", "br", "mx", "sg", "ae", "sa", "tr"]

main_url = 'https://www.amazon.{}'

# Headers to mimic a browser visit
headers_list = [
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'},
    {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0'},
    {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'},
    {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'}
]

headers = random.choice(headers_list)

# Function to get the search results
def get_search_results(search_query, country):
    # Retry mechanism
    max_retries = 5
    for attempt in range(max_retries):
        country_url=main_url.format(country)
        response = requests.get(country_url+"/s?k={}&ref=nb_sb_noss_2".format(search_query), headers=headers)
        if response.status_code == 200:
            break
        else:
            print(f'Attempt {attempt + 1} failed for {country}. Status code: {response.status_code}')
            time.sleep(2)  # Wait for 2 seconds before retrying
    else:
        print(f'Failed to retrieve search results.{country}')
        return
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all product containers
    products = soup.find_all('div', {'data-component-type': 's-search-result'})
    file_name=search_query+"_"+country+'.csv'
    # Open a CSV file to write the data
    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(['Title', 'Price', 'Discount', 'Rating', 'Number of Ratings', 'Delivery Details'])
            
        for product in products:
            # Extract the product title
            title = product.h2.get_text(strip=True)
            
            # Extract the product price
            price = product.find('span', {'class': 'a-offscreen'})
            price = price.get_text(strip=True) if price else "N/A"
            price=price.replace('₹','')
            
            # Extract the product discount
            discount = product.find('span', string=lambda x: x and '%' in x)
            discount = discount.get_text(strip=True) if discount else "No discount"
            discount = ''.join(filter(str.isdigit, discount)) if discount != "No discount" else "0"
            
            # Extract the product rating
            rating = product.find('span', {'class': 'a-icon-alt'})
            rating = rating.get_text(strip=True) if rating else "No rating"
            
            # Extract the number of ratings
            num_ratings = product.find('span', {'class': 'a-size-base'})
            num_ratings = num_ratings.get_text(strip=True) if num_ratings else "No ratings"
            
            # Extract the delivery details
            delivery = product.find('span', {'class': 'a-color-base a-text-bold'})
            delivery = delivery.get_text(strip=True) if delivery else "No delivery details"
               
            # Write the product row
            writer.writerow([title, price, discount, rating, num_ratings, delivery])
    print(f'File saved: {file_name} with {len(products)} products')

for country in countries_domain:
    get_search_results(search_query, country)
    time.sleep(10)  # Wait for 2 seconds before the next country