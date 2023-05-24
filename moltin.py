import requests


def main():
    moltin_access_token = get_moltin_token()

    get_products(moltin_access_token)

    url = 'https://api.moltin.com/v2/carts/1/items'

    payload = {
        'data': {
            'id': '00622eba-324d-4792-9800-4b7149d78e0f',
            'type': 'cart_item',
            'quantity': 1
        }
    }
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=payload, headers=headers)

    url = 'https://api.moltin.com/v2/carts/1'
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
    }
    response = requests.get(url, headers=headers)

    url = 'https://api.moltin.com/v2/carts/1/items'
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
    }
    response = requests.get(url, headers=headers)


def get_moltin_token(client_key, secret_key):
    url = 'https://api.moltin.com/oauth/access_token'

    payload = {
        'client_id': client_key,
        'client_secret': secret_key,
        'grant_type': 'client_credentials',
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    moltin_access_token = response.json()['access_token']

    return moltin_access_token


def get_products(moltin_access_token):
    url = 'https://api.moltin.com/pcm/products'
    headers = {
        'Authorization': f'Bearer {moltin_access_token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()['data']


def get_product(moltin_access_token, product_id):
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
    }
    product_url = f'https://api.moltin.com/pcm/products/{product_id}'
    response = requests.get(product_url, headers=headers)
    response.raise_for_status()

    return response.json()['data']


def get_stock(moltin_access_token, product_id):
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
    }
    product_url = f'https://api.moltin.com/v2/inventories/{product_id}'
    response = requests.get(product_url, headers=headers)
    response.raise_for_status()

    return response.json()['data']['available']


def get_price(moltin_access_token, product_id):
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
    }
    payload = {
        'include': 'prices'
    }
    product_url = f'https://api.moltin.com/catalog/products/{product_id}'
    response = requests.get(product_url, headers=headers, params=payload)
    response.raise_for_status()
    price = response.json()['data']['attributes']['price']

    return price


def get_product_image(moltin_access_token, product_id):
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
    }

    url = f'https://api.moltin.com/pcm/products/{product_id}/relationships/main_image'
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    image_id = response.json()['data']['id']

    url = f'https://api.moltin.com/v2/files/{image_id}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    image_link = response.json()['data']['link']['href']

    return image_link


if __name__ == '__main__':
    main()
