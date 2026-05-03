import requests
import os

# TWOJE DANE
API_KEY = 'cfa1a1adba210b47280d690f16545801313467cf8fe20ed5'
TARGET_DIR = './ObiadDlaMisia'

if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR)

# 1. POBIERANIE LISTY OSTATNICH 100 SAMPLI
url = "https://mb-api.abuse.ch/api/v1/"
data = {
    'query': 'get_recent',
    'selector': '100'
}

response = requests.post(url, data=data)
samples = response.json().get('data', [])

print(f"🐻 Misiu: Znalazłem {len(samples)} soczystych kąsków!")

# 2. POBIERANIE KAŻDEGO PLIKU
for sample in samples:
    sha256 = sample['sha256_hash']
    print(f"🛒 Pakuję do koszyka: {sha256[:10]}...")
    
    download_data = {
        'query': 'get_file',
        'sha256_hash': sha256
    }
    
    file_res = requests.post(url, data=download_data, headers={'API-KEY': API_KEY})
    
    with open(f"{TARGET_DIR}/{sha256}.zip", 'wb') as f:
        f.write(file_res.content)

print("🐻 Misiu: Zakupy zrobione! Wszystko w folderze. Pora na cyfrowe piekło!")
