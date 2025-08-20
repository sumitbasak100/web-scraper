from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def scrape_webpage(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code != 200:
        return {"error": f"Failed to fetch page: {response.status_code}"}
    
    soup = BeautifulSoup(response.text, "html.parser")

    # Title
    title = soup.title.string.strip() if soup.title else ""

    # Meta description
    meta_description = ""
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        meta_description = meta["content"].strip()

    # Headings
    headings = {
        "h1": [h.get_text(strip=True) for h in soup.find_all("h1")],
        "h2": [h.get_text(strip=True) for h in soup.find_all("h2")],
        "h3": [h.get_text(strip=True) for h in soup.find_all("h3")],
        "h4": [h.get_text(strip=True) for h in soup.find_all("h4")]
    }

    # Images + alt text
    images = []
    for img in soup.find_all("img"):
        images.append({
            "src": img.get("src"),
            "alt": img.get("alt", "").strip()
        })

    # Full text (remove scripts/styles)
    for script in soup(["script", "style", "noscript"]):
        script.extract()
    text_content = soup.get_text(separator=" ", strip=True)

    # Build structured data
    data = {
        "url": url,
        "title": title,
        "meta_description": meta_description,
        "headings": headings,
        "images": images,
        "content_text": text_content[:2000]  # limit text length for API response
    }

    return data

@app.route("/scrape", methods=["GET"])
def scrape_api():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing ?url= parameter"}), 400
    
    try:
        data = scrape_webpage(url)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
