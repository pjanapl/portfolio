from bs4 import BeautifulSoup
import requests, pickle, re
import pandas as pd

#
# Parametry ogólne
#
base_url = 'https://www.rossmann.pl'
product_list_pickle_filename = './data/male_product_list.pkl'
products_data_pickle_filename = './data/male_products_data.pkl'

#
# Parametry przeszukiwania listy stron
#
scrape_product_list = False
get_product_list_from_file = True
save_product_list_to_file = True
product_pages = 75
category_url = '/kategoria/mezczyzna,13224'
page_prefix = '?Page='

#
# Parametry przeszukiwania stron produktów
#
scrape_products_pages = True
save_products_data_to_file = True
start = 0
stop = 2000

#
# Nazwy kolumn w danych wyjściowych
#
columns = ['product_id',
           'name',
           'caption',
           'cat_1',
           'cat_2',
           'cat_3',
           'cat_4',
           'cat_5',
           'url',
           'capacity',
           'current_price_pln',
           'regular_price_pln',
           'lowest_price_last_30_days_pln',
           'price_per_unit_pln',
           'unit',
           'mega_badge',
           'ingredients',
           'rating',
           'reviews',     
           ]

products_url = []

def scrape_products_urls(base_url, category_url, page_prefix, num_of_pages):
    '''
    Funkcja pobierająca dane ze stron określonej kategorii.

    Returns:
        set: zbiór linków produktów określonej kategorii.
    '''
    product_list = []

    for page_number in range(1, num_of_pages + 1):
        print(f"Pobieranie linków ze strony {page_number} kategorii.")
        response = requests.get(base_url + category_url + page_prefix + str(page_number))
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a')

            for link in links:
                href = link.get("href")
                if type(href) == str and href.startswith('/Produkt/'):
                    product_list.append(href)

    link_set = set(product_list)
    print(f"Zwracam {len(link_set)} linków produktów.")
    return link_set

def scrape_product_page(base_url, page_url):
    '''
    Funkcja pobierająca dane ze strony określonego na podstawie linku produktu.

    Returns:
        list: lista z 19 polami danych produktu
    '''
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
        # cat_4
        if len(list(soup.find(attrs={"class": "styles-module_ol--FwihY"}).children)) > 5:
            a = list(soup.find(attrs={"class": "styles-module_ol--FwihY"}).children)[5].text
        else:
            a = ''
        page_data.append(a)
        # cat_5
        if len(list(soup.find(attrs={"class": "styles-module_ol--FwihY"}).children)) > 6:
            a = list(soup.find(attrs={"class": "styles-module_ol--FwihY"}).children)[6].text
        else:
            a = ''
        page_data.append(a)
        # url
        page_data.append(base_url + page_url)
        # capacity
        a =  soup.find(attrs={"data-testid": "product-unit"}).text.strip()
        page_data.append(a)
        # current_price
        a = soup.find(attrs={"data-testid": "product-price"}).text.strip()
        a = float(a.replace("zł", "").replace(" ", "").replace(",", "."))
        page_data.append(a)
        # regular_price
        if soup.find(attrs={"data-testid": "basic-price"}) is not None:
            a = soup.find(attrs={"data-testid": "basic-price"}).text.strip()
            a = float(a.replace("zł", "").replace(" ", "").replace(",", "."))
        else:
            a = ''
        page_data.append(a)
        # lowest_price_last_30_days
        if soup.find(attrs={"data-testid": "lowest-price-in-30-days"}) is not None:
            a = soup.find(attrs={"data-testid": "lowest-price-in-30-days"}).text.strip()
            a = float(a.replace("zł", "").replace(" ", "").replace(",", "."))
        else:
            a = ''
        page_data.append(a)
        # price_per_unit
        a = soup.find(attrs={"data-testid": "product-price-per-unit"}).text.split(" = ")[1]
        a = float(a.replace("zł", "").replace(" ", "").replace(",", "."))
        page_data.append(a)
        # unit 
        a = soup.find(attrs={"data-testid": "product-price-per-unit"}).text.split(" = ")[0]
        page_data.append(a)
        # mega_badge
        if soup.find(attrs={"data-testid": "mega-badge"}) is not None:
            a = 1
        else:
            a = 0
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

#
# Instrukcje wykonania pobierania danych ze stron kategorii.
#
if scrape_product_list:
    products_url = scrape_products_urls(base_url,
                                        category_url,
                                        page_prefix,
                                        product_pages)
    if save_product_list_to_file:
        with open(product_list_pickle_filename, 'wb') as file:
            print('Zapisuję listę poduktów.')
            pickle.dump(products_url, file)
elif get_product_list_from_file:
    print('Pobieranie listy produktów z pliku.')
    with open(product_list_pickle_filename, 'rb') as file:
        products_url = pickle.load(file)

#
# Instrukcje wykonania pobierania danych ze stron produktów.
#
if scrape_products_pages:
    products_data = []
    for i, page in enumerate(products_url):
        if i >= start and i <= stop:
            print('Pobieranie danych ze strony ' + str(i))
            products_data.append(scrape_product_page(base_url, page))
    if save_products_data_to_file:
        products_data = [p for p in products_data if p is not None]
        df = pd.DataFrame(products_data, columns = columns)
        with open(products_data_pickle_filename, 'wb') as file:
            print('Zapisuję dane poduktów.')
            pickle.dump(df, file)
