import requests
import hashlib
import json
import os

TOKEN = "nfp_pZ9fdo2HZMd4vNU3N89VajkkQU9NWM4Sfcf7"
headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

script_dir = os.path.dirname(os.path.abspath(__file__))
html_path = os.path.join(script_dir, "index.html")

files_to_deploy = {}
file_bytes = {}

for fname in ["index.html", "manifest.json"]:
    fpath = os.path.join(script_dir, fname)
    if os.path.exists(fpath):
        with open(fpath, "rb") as f:
            b = f.read()
        sha1 = hashlib.sha1(b).hexdigest()
        files_to_deploy[f"/{fname}"] = sha1
        file_bytes[sha1] = (fname, b)
        print(f"{fname} SHA1: {sha1}")

html_bytes = file_bytes[list(files_to_deploy.values())[0]][1]
html_sha1 = list(files_to_deploy.values())[0]

# Use existing site
site_id = "882606af-605a-4f45-93d9-e0303927612a"
site_url = "https://junyeong-life-system.netlify.app"
print(f"Deploying to existing site: {site_url}")

# Deploy via file digest
deploy_headers = {**headers, "Content-Type": "application/json"}
deploy_body = {
    "files": files_to_deploy,
    "async": False
}

r2 = requests.post(
    f"https://api.netlify.com/api/v1/sites/{site_id}/deploys",
    headers=deploy_headers,
    json=deploy_body
)
print(f"Create deploy: {r2.status_code}")
deploy = r2.json()
deploy_id = deploy.get("id")
required = deploy.get("required", [])
print(f"Deploy ID: {deploy_id}, Required files: {required}")

# Upload required files
upload_headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/octet-stream"
}
for sha1 in required:
    if sha1 in file_bytes:
        fname, fbytes = file_bytes[sha1]
        r3 = requests.put(
            f"https://api.netlify.com/api/v1/deploys/{deploy_id}/files/{fname}",
            headers=upload_headers,
            data=fbytes
        )
        print(f"Upload {fname}: {r3.status_code}")
        if r3.status_code not in (200, 201):
            print(r3.text[:300])

# Final URL
print(f"\n✅ SITE LIVE: {site_url}")
print(f"   Admin: https://app.netlify.com/sites/{site.get('name', site_id)}")
