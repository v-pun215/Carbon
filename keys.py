import requests

url = "https://argon-keys.vercel.app/keys.txt"
url = requests.get(url).text
clientId = url.split("\n")[0]
secret = url.split("\n")[1]
redirectURL = "https://eclient-done.vercel.app"