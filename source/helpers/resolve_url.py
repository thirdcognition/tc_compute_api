from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from playwright.sync_api import sync_playwright, Page, Playwright, Browser
from playwright.async_api import (
    async_playwright,
    Page as AsyncPage,
    Playwright as AsyncPlaywright,
    Browser as AsyncBrowser,
)
from bs4 import BeautifulSoup
from source.llm_exec.news_exec import rewrite_text, rewrite_text_sync
from source.models.config.logging import logger
import asyncio
import nest_asyncio


class UrlResults(BaseModel):
    orig_url: Optional[str] = None
    resolved_url: Optional[str] = None
    title: Optional[str] = None
    source: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    publish_date: Optional[datetime] = None
    categories: Optional[List[str]] = None
    lang: Optional[str] = None
    human_readable_content: Optional[str] = None
    formatted_content: Optional[str] = None

    def __str__(self):
        return f"Original URL: {self.orig_url}, Resolved URL: {self.resolved_url}, Title: {self.title}, Source: {self.source}, Description: {self.description}, Image: {self.image}, Publish Date: {self.publish_date}, Categories: {self.categories}, Language: {self.lang}"


def parse_publish_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z") if date_str else None
    except ValueError:
        try:
            return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
        except ValueError:
            logger.error(f"Invalid date format: {date_str}")
            return None


class LinkResolver:
    is_async: bool = False
    playwright: Playwright = None
    browser: Browser = None
    page: Page = None
    async_playwright: AsyncPlaywright = None
    async_browser: AsyncBrowser = None
    async_page: AsyncPage = None

    def __init__(self, reformat_text=False):
        if not asyncio.get_event_loop().is_running():
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch()
        else:
            self.is_async = True

        self.reformat_text = reformat_text

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

    def _get_page_sync(self, url):
        self.page = (
            self.browser.new_page()
        )  # Use the incognito context to create a new page
        self.page.goto(url)

    def _cloudfare_sync(self):
        # Check for Cloudflare challenge
        if "cloudflare" in self.page.content().lower():
            logger.info("Cloudflare challenge detected, attempting to bypass.")
            self.page.wait_for_timeout(
                5000
            )  # Wait for 5 seconds to let Cloudflare challenge pass
            self.page.reload()
            self.page.wait_for_load_state("networkidle")

    def _resolve_content_sync(self, url) -> tuple[str, str]:
        max_tries = 5
        tries = 0
        original_url = url
        resolved_url = self.page.url

        while (resolved_url != original_url and tries < max_tries) or tries == 0:
            original_url = resolved_url
            if "chrome-error://chromewebdata/" in resolved_url:
                raise Exception("Encountered a chrome-error URL")

            # Try to accept consent using known selectors
            for selector in self.consent_accept_selectors.values():
                if self.page.locator(selector).count() > 0:
                    try:
                        self.page.click(selector)
                        self.page.wait_for_load_state("networkidle")
                    except Exception as e:
                        logger.error(f"Error clicking consent button: {e}")
                    break

            resolved_url = self.page.url
            tries += 1

        if resolved_url != original_url:
            raise Exception(
                "Final URL differs from the original URL after maximum retries"
            )

        # Get the page content
        content = self.page.content()
        self.page.close()

        return resolved_url, content

    def _resolve_text_w_metadata(self, content) -> tuple[str, dict]:
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

        # Extract title, source, description, image, publish date, categories, and language
        metadata["title"] = soup.title.string if soup.title else None
        metadata["categories"] = [
            tag.get("content", "")
            for tag in soup.find_all("meta", property="article:tag")
        ]

        return text, metadata

    def _build_results(self, url, resolved_url, text, formatted_text, metadata):
        return UrlResults(
            orig_url=url,
            resolved_url=resolved_url,
            title=metadata.get("title"),
            source=metadata.get("og:site_name"),
            description=metadata.get("description"),
            image=metadata.get("og:image"),
            publish_date=parse_publish_date(metadata.get("article:published_time")),
            categories=(
                metadata.get("categories") if metadata.get("categories") else None
            ),
            lang=metadata.get("og:locale", "EN").split("_")[0],
            human_readable_content=f"Metadata: {metadata}\n\nContent:\n{text}",
            formatted_content=(
                f"Metadata: {metadata}\n\nContent:\n{formatted_text}"
                if formatted_text
                else None
            ),
        )

    def _format_content_sync(self, text):
        formatted_text = None
        if self.reformat_text:
            try:
                formatted_text = rewrite_text_sync(text)
            except Exception as e:
                logger.error(f"Failed to format text: {e}")
        return formatted_text

    def _resolve_url_sync(self, url: str) -> UrlResults:
        self._get_page_sync(url)
        self._cloudfare_sync()

        resolved_url, content = self._resolve_content_sync(url)

        if not content:
            raise Exception("Content could not be loaded")

        text, metadata = self._resolve_text_w_metadata(content)

        formatted_text = self._format_content_sync(text)

        return self._build_results(url, resolved_url, text, formatted_text, metadata)

    async def _get_page_async(self, url):
        self.async_page = await self.async_browser.new_page()
        await self.async_page.goto(url)

    async def _cloudfare_async(self):
        content = await self.async_page.content()
        if "cloudflare" in content.lower():
            logger.info("Cloudflare challenge detected, attempting to bypass.")
            await self.async_page.wait_for_timeout(5000)
            await self.async_page.reload()
            await self.async_page.wait_for_load_state("networkidle")

    async def _resolve_content_async(self, url) -> tuple[str, str]:
        max_tries = 5
        tries = 0
        original_url = url
        resolved_url = self.async_page.url

        while (resolved_url != original_url and tries < max_tries) or tries == 0:
            original_url = resolved_url
            if "chrome-error://chromewebdata/" in resolved_url:
                raise Exception("Encountered a chrome-error URL")

            for selector in self.consent_accept_selectors.values():
                if await self.async_page.locator(selector).count() > 0:
                    try:
                        await self.async_page.click(selector)
                        await self.async_page.wait_for_load_state("networkidle")
                    except Exception as e:
                        logger.error(f"Error clicking consent button: {e}")
                    break

            resolved_url = self.async_page.url
            tries += 1

        if resolved_url != original_url:
            raise Exception(
                "Final URL differs from the original URL after maximum retries"
            )

        content = await self.async_page.content()
        await self.async_page.close()

        return resolved_url, content

    async def _resolve_url_async(self, url: str) -> UrlResults:
        if not self.async_playwright:
            self.async_playwright = await async_playwright().start()
            self.async_browser = await self.async_playwright.chromium.launch()

        await self._get_page_async(url)
        await self._cloudfare_async()

        resolved_url, content = await self._resolve_content_async(url)

        if not content:
            raise Exception("Content could not be loaded")

        text, metadata = self._resolve_text_w_metadata(content)

        formatted_text = await self._format_content_async(text)

        await self.async_browser.close()
        await self.async_playwright.stop()

        return self._build_results(url, resolved_url, text, formatted_text, metadata)

    async def _format_content_async(self, text):
        formatted_text = None
        if self.reformat_text:
            try:
                formatted_text = await rewrite_text(text)
            except Exception as e:
                logger.error(f"Failed to format text: {e}")
        return formatted_text

    async def async_close(self):
        if self.async_browser is not None:
            await self.async_browser.close()
        if self.async_playwright is not None:
            await self.async_playwright.stop()

    def close(self):
        if self.is_async:
            if asyncio.get_event_loop().is_running():
                nest_asyncio.apply()
                asyncio.run(self.async_close())
            else:
                asyncio.run(self.async_close())
        else:
            if self.browser is not None:
                self.browser.close()
            if self.playwright is not None:
                self.playwright.stop()

    def resolve_url(self, url: str) -> UrlResults:
        if self.is_async:
            if asyncio.get_event_loop().is_running():
                nest_asyncio.apply()
                return asyncio.run(self._resolve_url_async(url))
            else:
                return asyncio.run(self._resolve_url_async(url))
        else:
            return self._resolve_url_sync(url)
