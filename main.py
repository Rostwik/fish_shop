import os

import requests
from dotenv import load_dotenv


def main():
    load_dotenv()
    client_id = os.getenv('MOLTIN_CLIENT_KEY')
    url = 'https://api.moltin.com/oauth/access_token'

    payload = {
        'client_id': client_id,
        'grant_type': 'implicit'
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()

    moltin_access_token = response.json()['access_token']

    print(moltin_access_token)

    url = 'https://api.moltin.com/v2/products/'
    headers = {
        'Authorization': f'Bearer {moltin_access_token}'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    print(response.json()['data'])


if __name__ == '__main__':
    main()
