import requests
from bs4 import BeautifulSoup, element
import re
import csv
import os
from datetime import datetime

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36"}
url = "https://www.microsoftstore.com.cn/refurbishedsurface/certified-refurbished-surface-book/p/mic2173?Icid=SurfacecertifiedrefurbishedCategory_surfacebook_201810"

try:
    resp = requests.get(url, headers=headers, timeout=10)
except requests.exceptions.Timeout:
    exit(1)
html = resp.content.decode('utf-8')
soup = BeautifulSoup(html,'html.parser')

price = soup.find(class_='priceAndRank').ul.contents
price = [i.string.replace('¥', '').strip() for i in price if isinstance(i, element.Tag)]
price_suggest = price[0]
price_new = price[1]
stock_status = soup.find(class_='buy').button.string
data = {'time': str(datetime.now()), 'price_suggest': price_suggest, 'price_new': price_new, 'stock_status': stock_status}

fields = ['time', 'price_suggest', 'price_new', 'stock_status']
try:
    filesize = os.path.getsize('price_data.csv')
except FileNotFoundError:
    filesize = 0

with open('price_data.csv', 'a', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fields)
    if filesize == 0:
        writer.writeheader()
    writer.writerow(data)
