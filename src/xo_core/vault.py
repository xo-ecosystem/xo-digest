"""
Vault operations module.
"""

from typing import Optional

import requests


def sign_all() -> str:
    """
    Sign all vault entries.

    Returns:
        str: Status message indicating success or failure
    """
    try:
        response = requests.post("http://localhost:8080/vault/sign-all")
        return response.text
    except requests.exceptions.Timeout:
        return "❌ Timeout while signing vault entries"
    except requests.exceptions.RequestException as e:
        return f"❌ Error signing vault entries: {str(e)}"
