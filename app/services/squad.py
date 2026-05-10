import requests
import os
import random

SQUAD_BASE_URL = os.getenv("SQUAD_BASE_URL", "https://sandbox-api-d.squadco.com")
SQUAD_SECRET_KEY = os.getenv("SQUAD_SECRET_KEY")


def generate_account_number():
    return ''.join([str(random.randint(0, 9)) for _ in range(10)])


def create_virtual_account(user_id, goal_id, goal_name):
    try:
        headers = {
            "Authorization": f"Bearer {SQUAD_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "customer_identifier": f"user_{user_id}_goal_{goal_id}",
            "first_name": "StackSmart",
            "last_name": goal_name[:50],
            "mobile_num": "08100000000",
            "email": f"goal_{goal_id}@stacksmart.app",
            "bvn": "22222222222",
            "beneficiary_account": "0000000000"
        }

        response = requests.post(
            f"{SQUAD_BASE_URL}/virtual-account",
            json=payload,
            headers=headers,
            timeout=10
        )

        data = response.json()
        print(f"Squad response: {data}")

        if response.status_code == 200 and data.get('success'):
            return {
                'squad_account_ref': data['data']['virtual_account_number'],
                'account_number': data['data']['virtual_account_number'],
                'bank_name': 'GTBank (Squad)'
            }

    except Exception as e:
        print(f"Squad API error: {e}")

    # fallback for demo
    account_number = generate_account_number()
    return {
        'squad_account_ref': f"SQUAD_{user_id}_{goal_id}_{account_number}",
        'account_number': account_number,
        'bank_name': 'GTBank (Squad)'
    }