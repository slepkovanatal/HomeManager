import requests
import json
import re

from functools import singledispatch

HEADERS = {
    'x-application': 'AHWEBSHOP',
    'user-agent': 'Appie/8.22.3',
    'content-type': 'application/json; charset=UTF-8',
}

def get_anonymous_access_token():
    response = requests.post(
        'https://api.ah.nl/mobile-auth/v1/auth/token/anonymous',
        headers=HEADERS,
        json={"clientId": "appie"}
    )
    if not response.ok:
        response.raise_for_status()
    return response.json()

_access_token = get_anonymous_access_token()

def search_products(query=None, page=0, size=50, sort='RELEVANCE') -> json:
    response = requests.get(
        'https://api.ah.nl/mobile-services/product/search/v2?sortOn=RELEVANCE',
        params={"sortOn": sort, "page": page, "size": size, "query": query},
        headers={**HEADERS, "Authorization": "Bearer {}".format(_access_token.get('access_token'))}
    )
    if not response.ok:
        response.raise_for_status()
    return response.json()

def fetch_product_data(url: str):
    if not url.startswith("https://www.ah.nl"):
        return None

    product_id = fetch_product_id(url)

    response = requests.get(f'https://api.ah.nl/mobile-services/product/detail/v4/fir/{product_id}',
                            headers={**HEADERS, "Authorization": "Bearer {}".format(_access_token.get('access_token'))})
    if not response.ok:
        response.raise_for_status()
    return response.json()

def extract_product_data(product):
    images = product['images']
    largest_image = max(images, key=lambda img: img['width'])
    return {
        'productId': product['webshopId'],
        'productUrl': get_product_url(product['webshopId']),
        'price': product["priceBeforeBonus"],
        'imageUrl': largest_image['url']
    }

@singledispatch
def extract_products_data(arg):
    raise NotImplementedError(f"Unsupported type: {type(arg)}")

@extract_products_data.register
def _(query: str):
    data = search_products(query)

    products_data = []
    for product in data['products']:
        products_data.append(extract_product_data(product))
    return products_data

@extract_products_data.register
def _(product_urls: list):
    product_datas = []
    for url in product_urls:
        product = fetch_product_data(url)
        if product is not None:
            product_datas.append(extract_product_data(product))
    return product_datas

def get_product_url(product_id) -> str:
    return f'https://www.ah.nl/producten/product/wi{product_id}'

def fetch_product_id(url: str) -> str | None:
    match = re.search(r'wi(\d{6})', url)
    if match:
        return match.group(1)
    return None