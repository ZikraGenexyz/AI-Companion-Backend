from urllib.parse import urlparse, unquote

url = "https://firebasestorage.googleapis.com/v0/b/companion-app-1b431.firebasestorage.app/o/mission_attachments%2F6BmFosJJWldIF0I5Rjgsi7NR3V44%2F29d418be-8381-4bad-88ac-c4c344a74b48.jpg?alt=media"

parsed_url = urlparse(url)
path = parsed_url.path.split('/o/')[1].split('?')[0]
storage_path = unquote(path)  # Decodes '%2F' to '/'
print(storage_path)