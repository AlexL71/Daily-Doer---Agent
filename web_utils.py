import httpx
from bs4 import BeautifulSoup
from newspaper import Article, Config as NewspaperConfig
import asyncio
from urllib.parse import urljoin, urlparse

async def get_text_from_url(url: str) -> str | None:
    try:
        news_config = NewspaperConfig()
        news_config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        news_config.request_timeout = 20
        news_config.fetch_images = False
        news_config.memoize_articles = False

        article = Article(url, config=news_config)
        
        def sync_download_and_parse():
            article.download()
            article.parse()
            return article.text

        extracted_text = await asyncio.to_thread(sync_download_and_parse)

        if not extracted_text or not extracted_text.strip():
            if article.download_exception_msg:
                 return f"Sorry, I couldn't download the article from that URL. Error: {article.download_exception_msg}"
            return "Sorry, I couldn't extract the main article content from that page."
        
        max_chars = 35000
        return extracted_text[:max_chars]

    except Exception as e:
        print(f"Error using newspaper3k for URL {url}: {e}")
        if "Article `download()` failed" in str(e) or "TooManyRedirects" in str(e):
             return "Sorry, I couldn't download the content from that URL."
        elif "timeout" in str(e).lower():
            return "Sorry, the request to the webpage timed out."
        return "Sorry, I had trouble processing that webpage."

async def get_article_links_from_homepage(homepage_url: str, limit: int = 1) -> list[str]:
    article_links = []
    found_urls = set()
    try:
        async with httpx.AsyncClient() as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = await client.get(homepage_url, headers=headers, follow_redirects=True, timeout=15.0)
            response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        site_specific_selectors_tried = False
        if "bbc.com" in homepage_url: # Example: these selectors need your verification
            site_specific_selectors_tried = True
            for link_tag in soup.select('a.gs-c-promo-heading[href^="/news/"], .lx-stream-post__header-link[href*="/news/articles/"]'):
                if 'href' in link_tag.attrs:
                    href = link_tag['href']
                    if not any(skip in href for skip in ['/live/', '/sounds/', '/av/', '/sport', '/weather']):
                        abs_url = urljoin(homepage_url, href)
                        found_urls.add(abs_url)
                    if len(found_urls) >= limit: break
        
        elif "euronews.com" in homepage_url:
            site_specific_selectors_tried = True
            for link_tag in soup.select('article .m-object__title__link, article a.media__title__link'):
                if 'href' in link_tag.attrs:
                    href = link_tag['href']
                    abs_url = urljoin(homepage_url, href)
                    if not any(skip in href for skip in ['/video', '/live', '/next/', '/programs/']) and 'euronews.com' in abs_url: # Check if it's an euronews link
                         found_urls.add(abs_url)
                    if len(found_urls) >= limit: break
        
        elif "aljazeera.com" in homepage_url: 
            site_specific_selectors_tried = True
            for link_tag in soup.select('a.u-clickable-card__link[href*="/news/"], a.fte-article__title-link[href*="/news/"]'):
                if 'href' in link_tag.attrs:
                    href = link_tag['href']
                    abs_url = urljoin(homepage_url, href)
                    found_urls.add(abs_url)
                    if len(found_urls) >= limit: break
        
        if len(found_urls) < limit or not site_specific_selectors_tried:
        

            generic_selectors = ['article h2 a', 'article h3 a', 'a.story-link', '.headline a', '.story-title a']
            for css_selector in generic_selectors:
                if len(found_urls) >= limit: break
                for link_tag in soup.select(css_selector):
                    if 'href' in link_tag.attrs:
                        href = link_tag['href']
                        abs_url = urljoin(homepage_url, href)
                        parsed_url = urlparse(abs_url)
                        if parsed_url.scheme in ['http', 'https'] and abs_url not in found_urls and \
                           not any(skip in abs_url.lower() for skip in ['/live', '/video/', '/gallery/', '/podcasts/', '/weather/', 'author/', 'topics/', 'contact', 'about', 'program', 'mailto:', 'tel:', 'javascript:']) and \
                           (parsed_url.path.count('/') >= 3 or any(kw in abs_url.lower() for kw in ['.html', 'story', 'article', 'news'])):
                            found_urls.add(abs_url)
                            if len(found_urls) >= limit: break
        
        article_links = list(found_urls)[:limit]
        return article_links

    except Exception as e:
        print(f"Error HTML scraping homepage {homepage_url} for links: {e}")
        return []
