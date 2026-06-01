import requests
import hashlib
import json
import os

TOKEN = "nfp_pZ9fdo2HZMd4vNU3N89VajkkQU9NWM4Sfcf7"
headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

script_dir = os.path.dirname(os.path.abspath(__file__))
html_path = os.path.join(script_dir, "index.html")

with open(html_path, "rb") as f:
    html_bytes = f.read()

html_sha1 = hashlib.sha1(html_bytes).hexdigest()
print(f"File SHA1: {html_sha1}")

# Create site
r = requests.post(
    "https://api.netlify.com/api/v1/sites",
    headers=headers,
    json={"name": "junyeong-life-system"}
)
print(f"Create site: {r.status_code}")
if r.status_code not in (200, 201, 422):
    print(r.text)
    exit(1)

if r.status_code == 422:
    # Name taken, try with random suffix
    import random, string
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    r = requests.post(
        "https://api.netlify.com/api/v1/sites",
        headers=headers,
        json={"name": f"junyeong-life-system-{suffix}"}
    )
    print(f"Create site (retry): {r.status_code}")

site = r.json()
site_id = site["id"]
site_url = site.get("ssl_url") or site.get("url", "")
print(f"Site ID: {site_id}")
print(f"Site URL: {site_url}")

# Deploy via file digest
deploy_headers = {**headers, "Content-Type": "application/json"}
deploy_body = {
    "files": {
        "/index.html": html_sha1
    },
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

# Upload the file if required
if html_sha1 in required:
    upload_headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/octet-stream"
    }
    r3 = requests.put(
        f"https://api.netlify.com/api/v1/deploys/{deploy_id}/files/index.html",
        headers=upload_headers,
        data=html_bytes
    )
    print(f"Upload file: {r3.status_code}")
    if r3.status_code not in (200, 201):
        print(r3.text[:300])

# Final URL
print(f"\n✅ SITE LIVE: {site_url}")
print(f"   Admin: https://app.netlify.com/sites/{site.get('name', site_id)}")
