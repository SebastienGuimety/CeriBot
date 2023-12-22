import requests
from urllib import parse
import hashlib


def php_md5(text: str) -> str:
    result = hashlib.md5(text.encode())
    print(result.hexdigest())
    return result.hexdigest()


url = "https://api-dosi-test.univ-avignon.fr/partage/v1/Token/getToken"
payload = {
    'user': 'uapv1901981',
    'passClient': php_md5('mdp')
}

r = requests.post(url, data=payload)
print(r.text)


