from bs4 import BeautifulSoup

def clean_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    allowed = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li']
    for tag in soup.find_all(True):
        if tag.name not in allowed:
            tag.unwrap()
        else:
            tag.attrs = {}
    return str(soup)
