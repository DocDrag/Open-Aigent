from duckduckgo_search import DDGS
import json

def web_search(**kwargs):
    query = kwargs.get('query')
    if not query:
        return "Error: No query provided."
    
    # Clean the query from common LLM hallucinations like "> or extra quotes
    query = query.strip().replace('">', '').replace('"', '').replace("'", "")
    
    try:
        # Use a more direct approach with the DDGS class
        ddgs = DDGS()
        results = [r for r in ddgs.text(query, max_results=5, region="th-th")]
        
        if not results:
            # Try a broader search if no results
            results = [r for r in ddgs.text(query, max_results=3)]
            
        if not results:
            return f"No results found for '{query}'. Try a simpler search query."
            
        formatted = []
        for r in results:
            title = r.get('title', 'No Title')
            link = r.get('href', 'No Link')
            body = r.get('body', 'No Content')
            formatted.append(f"Title: {title}\nLink: {link}\nSnippet: {body}\n---")
            
        return "\n".join(formatted)
    except Exception as e:
        return f"Search error: {str(e)}"

def read_url(**kwargs):
    url = kwargs.get('url')
    if not url:
        return "Error: No URL provided."
    
    try:
        import requests
        from bs4 import BeautifulSoup
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text and clean up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Return first 2000 chars to avoid token bloat
        return text[:2000]
    except Exception as e:
        return f"Error reading URL: {str(e)}"


