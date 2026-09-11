import requests

r = requests.get("http://10.136.59.225:8000/api/health")
print("Response from Network IP:", r.status_code, r.json())
