from bs4 import BeautifulSoup
import requests, pickle, re

product_list_pickle_filename = 'product_list.pickle'
products_data_pickle_filename = 'products_data.pickle'

#
# Ustawienie parametrów
#
base_url = 'https://www.rossmann.pl'
# Strony kategorii
scrape_product_list = False
get_product_list_from_file = False
save_product_list_to_file = True
product_pages = 75
category_url = '/kategoria/mezczyzna,13224'
page_prefix = '?Page='

# Strony produktów
scrape_products_pages = False
get_products_data_from_file = False
save_products_data_to_file = True
start = 0
stop = 4000

# Dane wyjściowe
columns = ['product_id',
           'name',
           'caption',
           'cat_1',
           'cat_2',
           'cat_3',
           'url',
           'capacity',
           'current_price',
           'regular_price',
           'lowest_price_last_30_days',
           'price_per_unit',
           'unit',
           'badges',
           'ingredients',
           'rating',
           'reviews',     
           ]

products_url = []

def scrape_products_urls():
    print('Pobieranie listy produktów ze strony.')
    product_list = []

    for page_number in range(1, product_pages + 1):
        response = requests.get(base_url + category_url + page_prefix + str(page_number))
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a')

            for link in links:
                href = link.get("href")
                if type(href) == str and href.startswith('/Produkt/'):
                    product_list.append(href)
            
    return product_list

def scrape_product_page(page_url):
    page_data = []
    response = requests.get(base_url + page_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # product_id
        a = re.findall(r'\d+', soup.find(attrs={'class': 'styles-module_titleCaptionCatalogNumber----8JP'}).text)[0]
        page_data.append(a)
        # name
        if soup.find(attrs={"data-testid": "product-brand"}).a is not None:
            a = soup.find(attrs={"data-testid": "product-brand"}).a.text
        else:
            a = ''
        b = soup.find(attrs={"data-testid": "product-brand"}).contents[-1]
        page_data.append(a + ' ' + b)
        # caption
        a =  soup.find(attrs={"data-testid": "product-caption"}).text
        page_data.append(a)
        # cat_1
        a = list(soup.find(attrs={"class": "styles-module_ol--FwihY"}).children)[2].text
        page_data.append(a)
        # cat_2
        a = list(soup.find(attrs={"class": "styles-module_ol--FwihY"}).children)[3].text
        page_data.append(a)
        # cat_3
        a = list(soup.find(attrs={"class": "styles-module_ol--FwihY"}).children)[4].text
        page_data.append(a)
        # url
        page_data.append(base_url + page_url)
        # capacity
        a =  soup.find(attrs={"data-testid": "product-unit"}).text.strip()
        page_data.append(a)
        # current_price
        a = soup.find(attrs={"data-testid": "product-price"}).text.strip()
        page_data.append(a)
        # regular_price
        if soup.find(attrs={"data-testid": "basic-price"}) is not None:
            a = soup.find(attrs={"data-testid": "basic-price"}).text.strip()
        else:
            a = ''
        page_data.append(a)
        # lowest_price_last_30_days
        if soup.find(attrs={"data-testid": "lowest-price-in-30-days"}) is not None:
            a = soup.find(attrs={"data-testid": "lowest-price-in-30-days"}).text.strip()
        else:
            a = ''
        page_data.append(a)
        # price_per_unit
        a = soup.find(attrs={"data-testid": "product-price-per-unit"}).text.split(" = ")[1]
        page_data.append(a)
        # unit 
        a = soup.find(attrs={"data-testid": "product-price-per-unit"}).text.split(" = ")[0]
        page_data.append(a)
        # badges
        if soup.find(attrs={"data-testid": "mega-badge"}) is not None:
            a = soup.find(attrs={"data-testid": "mega-badge"}).text
        else:
            a = ''
        page_data.append(a)
        # ingredients
        if list(soup.find(attrs={"class": "styles-module_productDescription--Y3jcw"}).children)[1].span.text == 'Składniki':
            a = list(soup.find(attrs={"class": "styles-module_productDescription--Y3jcw"}).children)[1].p.text
        else:
            a = ''
        page_data.append(a)
        # rating
        if soup.find(attrs={"class": "styles-module_generalRating--r7c+K"}) is not None:
            a = soup.find(attrs={"class": "styles-module_generalRating--r7c+K"}).text
        else:
            a = ''
        page_data.append(a)
        # reviews
        if soup.find(attrs={"class": "styles-module_reviewsCount--9rZqX"}) is not None:
            a = re.findall(r'\d+', soup.find(attrs={"class": "styles-module_reviewsCount--9rZqX"}).text)[0]
        else:
            a = ''
        page_data.append(a)
        
        return page_data


if scrape_product_list:
    products_url = scrape_products_urls()
    if save_product_list_to_file:
        with open(product_list_pickle_filename, 'wb') as file:
            pickle.dump(products_url, file)
elif get_product_list_from_file:
    print('Pobieranie listy produktów z pliku.')
    with open(product_list_pickle_filename, 'rb') as file:
        products_url = pickle.load(file)

if scrape_products_pages:
    products_data = []
    for i, page in enumerate(products_url):
        if i >= start and i <= stop:
            print('Scraping page no. ' + str(i))
            products_data.append(scrape_product_page(page))
    products_data = [columns] + products_data
    if save_products_data_to_file:
        with open(products_data_pickle_filename, 'wb') as file:
            pickle.dump(products_data, file)
elif get_products_data_from_file:
    print('Pobieranie danych produktów z pliku.')
    with open(products_data_pickle_filename, 'rb') as file:
        products_data = pickle.load(file)
