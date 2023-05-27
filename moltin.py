import requests


def add_product_to_cart(moltin_access_token, product_id, amount, customer_id):
    url = f'https://api.moltin.com/v2/carts/{customer_id}/items'

    payload = {
        'data': {
            'id': product_id,
            'type': 'cart_item',
            'quantity': amount
        }
    }
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()


def get_cart_items(moltin_access_token, customer_id):
    url = f'https://api.moltin.com/v2/carts/{customer_id}/items'
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    cart_items = response.json()['data']

    url = f'https://api.moltin.com/v2/carts/{customer_id}'
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    items_sum = response.json()['data']['meta']['display_price']['with_tax']['amount']

    return cart_items, items_sum


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


def delete_cart_item(moltin_access_token, chat_id, product_id):
    headers = {
        'Authorization': f'Bearer {moltin_access_token}',
    }
    cart_url = f'https://api.moltin.com/v2/carts/{chat_id}/items/{product_id}'
    response = requests.delete(cart_url, headers=headers)
    response.raise_for_status()


def create_and_check_customer(moltin_access_token, name, email):
    headers = {
        'Authorization': f'Bearer {moltin_access_token}'
    }
    payload = {
        'data': {
            'type': 'customer',
            'name': name,
            'email': email,
            'password': '',
        },
    }
    url = 'https://api.moltin.com/v2/customers'
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    customer_id = response.json()['data']['id']

    url = f'https://api.moltin.com/v2/customers/{customer_id}'
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    return response.json()['data']
