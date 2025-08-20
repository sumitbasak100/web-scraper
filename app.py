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

    # Remove scripts/styles/noscripts
    for script in soup(["script", "style", "noscript"]):
        script.extract()

    # Collect structured content
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if p.get_text(strip=True)]
    lists = [li.get_text(strip=True) for li in soup.find_all("li") if li.get_text(strip=True)]
    other_text = [div.get_text(strip=True) for div in soup.find_all("div") if div.get_text(strip=True)]

    # Limit very large content
    paragraphs = paragraphs[:50]  # first 50 paragraphs
    lists = lists[:50]
    other_text = other_text[:50]

    data = {
        "url": url,
        "title": title,
        "meta_description": meta_description,
        "headings": headings,
        "content": {
            "paragraphs": paragraphs,
            "lists": lists,
            "other_text": other_text
        }
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
