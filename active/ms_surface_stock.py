import requests
from bs4 import BeautifulSoup, element
import re
import csv
import os
import pickle
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36"}


class Laptop:
    def __init__(self, url, product_name, model_name, display_name):
        self.update_time = datetime.now
        self.url = url
        self.product_name = product_name
        self.model_name = model_name
        self.display_name = display_name
        self.price_suggest = None
        self.price_new = None
        self.stock_status = None
    
    def update(self, price_suggest, price_new, stock_status):
        flg = 0

        if self.price_suggest != price_suggest:
            price_suggest_display = f"{self.price_suggest} -> {price_suggest}"
            self.price_suggest = price_suggest
            flg = 1
        else:
            price_suggest_display = self.price_suggest
        
        if self.price_new != price_new:
            price_new_display = f"{self.price_new} -> {price_new}"
            self.price_new = price_new
            flg = 1
        else:
            price_new_display = self.price_new

        if self.stock_status != stock_status:
            stock_status_display = f"{self.stock_status} -> {stock_status}"
            self.stock_status = stock_status
            flg = 1
        else:
            stock_status_display = self.stock_status

        if flg == 1:
            data = {
                'time': str(datetime.now()), 
                'price_suggest': price_suggest_display, 
                'price_new': price_new_display, 
                'stock_status': stock_status_display,
                'display_name': self.display_name
                }
            fields = ['time', 'display_name', 'price_suggest', 'price_new', 'stock_status']
            csv_path = os.path.join(BASE_DIR, 'price_data.csv')
            try:
                filesize = os.path.getsize(csv_path)
            except FileNotFoundError:
                filesize = 0

            with open(csv_path, 'a', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fields)
                if filesize == 0:
                    writer.writeheader()
                writer.writerow(data)
            

def get_response(url):
    for _ in range(10):
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            return resp
        except requests.exceptions.Timeout:
            pass


def init_data():
    url_base = "https://www.microsoftstore.com.cn/refurbishedsurface"
    product = {
        'certified-refurbished-surface-book': ('mic2173', 'mic2185'), 
        'certified-refurbished-surface-book-2': ('mic2564', 'mic2563'),
        'certified-refurbished-surface-pro-6': ('mic2602', 'mic2697'),
        'certified-refurbished-surface-pro': ('mic2405', 'mic2407', 'mic2410')
        }
    laptop_list = []
    for product_name in product:
        for model_name in product[product_name]:
            url = f"{url_base}/{product_name}/p/{model_name}"
            resp = get_response(url)
            html = resp.content.decode('utf-8')
            soup = BeautifulSoup(html,'html.parser')
            display_name = soup.find(class_="title cutline").h1.text
            laptop_list.append(Laptop(url, product_name, model_name, display_name))
    return laptop_list

data_path = os.path.join(BASE_DIR, 'surface_price.data')
if not os.path.exists(data_path):
    laptop_list = init_data()
else:
    with open(data_path, 'rb') as f:
        laptop_list = pickle.load(f)

for laptop in laptop_list:
    resp = get_response(laptop.url)
    html = resp.content.decode('utf-8')
    soup = BeautifulSoup(html,'html.parser')

    price = soup.find(class_='priceAndRank').ul.contents
    price = [str(i.string).replace('¥', '').strip() for i in price if isinstance(i, element.Tag)]
    # print(price)
    price_suggest = price[0]
    try:
        price_new = price[1]
    except IndexError:
        price_new = "null"
    stock_status = str(soup.find(class_='buy').button.string)  # 直接取到的并不是 str

    laptop.update(price_suggest, price_new, stock_status)

with open(data_path, 'wb') as f:
    pickle.dump(laptop_list, f)