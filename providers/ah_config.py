import requests
import json

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

def extract_largest_images(data):
    largest_images = []
    for product in data['products']:
        images = product['images']
        largest_image = max(images, key=lambda img: img['width'])
        largest_images.append({
            'productId': product['webshopId'],
            'productUrl': get_product_url(product['webshopId']),
            'imageUrl': largest_image['url'],
            'imageWidth': largest_image['width'],
            'imageHeight': largest_image['height']
        })
    return largest_images

def get_product_url(product_id) -> str:
    return f'https://www.ah.nl/producten/product/wi{product_id}'