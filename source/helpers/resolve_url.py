from typing import Tuple
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from source.models.config.logging import logger


class LinkResolver:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch()

        self.consent_accept_selectors = {
            "onetrust-cookiepro": "#onetrust-accept-btn-handler",
            "onetrust-enterprise": "#accept-recommended-btn-handler",
            "cookiebot": "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
            "cookiehub": "button.ch2-allow-all-btn",
            "typo3-wacon": ".waconcookiemanagement .cookie-accept",
            "cookiefirst": "[data-cookiefirst-action='accept']",
            "osano": ".osano-cm-accept-all",
            "orejime": ".orejime-Button--save",
            "axeptio": "#axeptio_btn_acceptAll",
            "civic-uk-cookie-control": "#ccc-notify-accept",
            "usercentrics": "[data-testid='uc-accept-all-button']",
            "cookie-yes": "[data-cky-tag='accept-button']",
            "secure-privacy": ".evSpAcceptBtn",
            "quantcast": "#qc-cmp2-ui button[mode='primary']",
            "didomi": "#didomi-notice-agree-button",
            "trustarc-truste": "#truste-consent-button",
            "non-specific-custom": "#AcceptCookiesButton, #acceptCookies, .cookie-accept, #cookie-accept, .gdpr-cookie--accept-all, button[class*='accept'], button[id*='accept'], button[class*='accept'], button[class*='agree'], button[id*='accept'], #cookiebanner button, button[class*='cookie'], button[name='agree'], button[data-action='acceptAll'], button[data-cookiebanner='accept_button'], button:has-text('Accept'), a:has-text('Accept'), span:has-text('Accept all cookies')",
        }

    def resolve_url(self, url: str) -> Tuple[str, str]:
        page = self.browser.new_page()  # Use the incognito context to create a new page
        page.goto(url)

        # Check for chrome-error URLs
        max_tries = 5
        tries = 0
        original_url = url
        final_url = page.url

        while (final_url != original_url and tries < max_tries) or tries == 0:
            original_url = final_url
            if "chrome-error://chromewebdata/" in final_url:
                raise Exception("Encountered a chrome-error URL")

            # Try to accept consent using known selectors
            for selector in self.consent_accept_selectors.values():
                if page.locator(selector).count() > 0:
                    try:
                        page.click(selector)
                        page.wait_for_load_state("networkidle")
                    except Exception as e:
                        logger.error(f"Error clicking consent button: {e}")
                    break

            final_url = page.url
            tries += 1

        if final_url != original_url:
            raise Exception(
                "Final URL differs from the original URL after maximum retries"
            )

        # Get the page content
        content = page.content()
        page.close()

        if not content:
            raise Exception("Content could not be loaded")

        # Parse the content with BeautifulSoup
        soup = BeautifulSoup(content, "html.parser")

        # Remove scripts and styles
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        # Extract text and metadata
        text = soup.get_text(separator="\n", strip=True)
        metadata = {
            meta.get("name", meta.get("property", "")): meta.get("content", "")
            for meta in soup.find_all("meta")
        }

        # Combine text and metadata
        human_readable_content = f"Metadata: {metadata}\n\nContent:\n{text}"

        return final_url, human_readable_content

    def close(self):
        self.browser.close()
        self.playwright.stop()
