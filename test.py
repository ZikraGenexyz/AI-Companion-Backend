from urllib.parse import urlparse, unquote
from apis.firebase_config import storage

url = "https://storage.googleapis.com/companion-app-1b431.firebasestorage.app/mission_attachments/6BmFosJJWldIF0I5Rjgsi7NR3V44/58335923-e819-4d2b-931f-84df5296a961.jpg"

if 'https://storage.googleapis.com/companion-app-1b431.firebasestorage.app/' in url:
    storage_path = url.replace('https://storage.googleapis.com/companion-app-1b431.firebasestorage.app/', '')
    print(storage_path)
else:
    print("Not a valid URL")
