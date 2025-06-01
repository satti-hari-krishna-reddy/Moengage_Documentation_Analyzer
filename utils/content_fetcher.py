import logging
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from readability import Document
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

class ContentFetcher:
    def __init__(self, url):
        self.url = url
        self.html = None

    def fetch_html(self):
        """Fetch HTML using Playwright with advanced bot evasion."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                viewport={'width': 1280, 'height': 800},
                java_script_enabled=True,
                locale='en-US',
            )

            # Make sure we store cookies to look real
            page = context.new_page()

            try:
                # Intercept requests to block unnecessary stuff (ads, trackers)
                page.route("**/*", lambda route, request: route.continue_() if request.resource_type in ['document', 'script', 'xhr'] else route.abort())

                # Go to page and wait for actual human-visible content
                page.goto(self.url, timeout=60000, wait_until="networkidle")

                # Try waiting for visible content inside .main-wrapper
                page.wait_for_selector(".article", timeout=20000) 

                # Scroll in case there's lazy-loaded stuff
                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(1500)

                self.html = page.content()
                logger.info("Successfully fetched HTML content via Playwright.")
            except Exception as e:
                logger.error(f"Playwright failed to fetch content: {e}")
                raise
            finally:
                browser.close()

    def parse_main_content(self):
        """Extract structured main content from the page using BeautifulSoup."""
        if not self.html:
            raise ValueError("No HTML content to parse.")

        soup = BeautifulSoup(self.html, 'html.parser')

        # Try to find the main content container
        main_wrapper = soup.select_one('.article') or soup.body  

        structure = []
        for tag in main_wrapper.select('h1, h2, h3, h4, h5, h6, p, ul, ol'):
            if tag.name.startswith('h'):
                structure.append(f"[{tag.name.upper()}] {tag.get_text(strip=True)}")
            elif tag.name in ['ul', 'ol']:
                for li in tag.find_all('li'):
                    structure.append(f"- {li.get_text(strip=True)}")
            elif tag.name == 'p':
                structure.append(tag.get_text(strip=True))

        return '\n'.join(structure)


    @classmethod
    def get_content(cls, url):
        fetcher = cls(url)
        fetcher.fetch_html()
        return fetcher.parse_main_content()
