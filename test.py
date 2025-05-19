from urllib.parse import urlparse, unquote
from apis.firebase_config import storage

url = "https://firebasestorage.googleapis.com/v0/b/companion-app-1b431.firebasestorage.app/o/mission_attachments%2FaGukhd3i5w6vKb1cguqSN6bMXvqu%2Fc8b667a7-b090-4b57-a3fb-10f5feb3d989.jpg?alt=media"

parsed_url = urlparse(url)
path = parsed_url.path.split('/o/')[1].split('?')[0]
storage_path = unquote(path)  # Decodes '%2F' to '/'
print(storage_path)

storage.delete(storage_path, None)