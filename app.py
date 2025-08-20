from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

app = Flask(__name__)

def extract_visible_text(soup):
    texts = []
    for tag in soup.find_all(["p", "li", "span", "div"]):
        text = tag.get_text(" ", strip=True)
        if text and len(text.split()) > 3:
            texts.append(text)
    return " ".join(texts)

def scrape_webpage(url):
    try:
        with sync_playwright() as p:
            browser = p.firefox.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=20000)
            html = page.content()
            browser.close()

        soup = BeautifulSoup(html, "html.parser")
        text_content = extract_visible_text(soup)

        title = soup.title.string.strip() if soup.title else ""
        meta_description = ""
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and meta.get("content"):
            meta_description = meta["content"].strip()

        headings = {
            "h1": [h.get_text(strip=True) for h in soup.find_all("h1")],
            "h2": [h.get_text(strip=True) for h in soup.find_all("h2")],
            "h3": [h.get_text(strip=True) for h in soup.find_all("h3")],
            "h4": [h.get_text(strip=True) for h in soup.find_all("h4")]
        }

        return {
            "url": url,
            "title": title,
            "meta_description": meta_description,
            "headings": headings,
            "content_text": text_content[:5000]  # limit to avoid overload
        }

    except Exception as e:
        return {"error": str(e)}

@app.route("/scrape", methods=["GET"])
def scrape_api():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing ?url= parameter"}), 400

    data = scrape_webpage(url)
    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
