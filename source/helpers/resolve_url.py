import base64
from datetime import datetime
import json
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright, Page, Playwright, Browser
from playwright.async_api import (
    async_playwright,
    Page as AsyncPage,
    Playwright as AsyncPlaywright,
    Browser as AsyncBrowser,
)
from bs4 import BeautifulSoup, Tag
from source.models.config.logging import logger
import asyncio
import nest_asyncio
from PIL import Image
import io

from source.models.structures.url_result import UrlResult
from source.llm_exec.news_exec import (
    text_format,
    text_format_sync,
    validate_news_article,
    validate_news_article_sync,
)


def parse_publish_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z") if date_str else None
    except ValueError:
        try:
            return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
        except ValueError:
            try:
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                logger.error(f"Invalid date format: {date_str}")
                return None


def process_image(image_data: bytes) -> bytes:
    """Rescale and convert image to JPG format."""
    with Image.open(io.BytesIO(image_data)) as img:
        if img.format not in ["JPEG", "PNG", "WEBP", "GIF"]:
            return image_data  # Skip unsupported formats

        # Rescale if larger than 512x512
        if img.width > 512 or img.height > 512:
            img.thumbnail((512, 512))

        # Convert to JPG
        output = io.BytesIO()
        img.convert("RGB").save(output, format="JPEG")
        return output.getvalue()


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

        return resolved_url, content

    def _parse_content_with_soup(
        self, content
    ) -> tuple[str, dict, list[tuple[int, str]]]:
        soup = BeautifulSoup(content, "html.parser")

        # Extract metadata
        metadata = {
            meta.get("name", meta.get("property", "")): meta.get("content", "")
            for meta in soup.find_all("meta")
        }
        metadata["title"] = soup.title.string if soup.title else None
        metadata["categories"] = [
            tag.get("content", "")
            for tag in soup.find_all("meta", property="article:tag")
        ]

        # Extract image URLs and replace with placeholders
        image_urls = []
        image_index = 1
        for img in soup.find_all("img"):
            if isinstance(img, Tag):
                img_src = img.get("src")
                if img_src and not (
                    img_src.endswith(".ico")
                    or img_src.endswith(".svg")
                    or "assets" in img_src
                    or "icons" in img_src
                ):
                    image_urls.append((image_index, img_src))

                    img_title = img.get("title")
                    img_alt = img.get("alt")
                    aria_label = img.get("aria-label")

                    placeholder_parts = [f"[Image {image_index}"]
                    if img_title:
                        placeholder_parts.append(f"Title='{img_title}'")
                    if img_alt:
                        placeholder_parts.append(f"Alt='{img_alt}'")
                    if aria_label:
                        placeholder_parts.append(f"Aria-Label='{aria_label}'")

                    placeholder = " ".join(placeholder_parts) + "]"
                    img.replace_with(placeholder)
                    image_index += 1

        # Extract text
        text = soup.get_text(separator="\n", strip=True)

        return text, metadata, image_urls

    def _fetch_images_sync(self, image_urls: list[tuple[int, str]]) -> list[dict]:
        image_data = []
        for index, img_src in image_urls:
            max_retries = 3
            if img_src.startswith("data:"):
                logger.info(f"Adding inline/data image as is: {img_src}")
                image_data.append({"index": index, "url": img_src, "data": img_src})
                continue
            if not img_src.startswith("http") and self.page.url:
                host = f"{urlparse(self.page.url).scheme}://{urlparse(self.page.url).netloc}"
                img_src = urljoin(host, img_src)
            for attempt in range(max_retries):
                try:
                    with self.page.expect_response(img_src) as response_info:
                        self.page.goto(img_src)
                    response = response_info.value
                    if response.ok:
                        mime_type = response.headers.get("content-type", "image/jpeg")
                        image_bytes = response.body()
                        image_bytes = process_image(image_bytes)
                        base64_data = base64.b64encode(image_bytes).decode("utf-8")
                        image_data.append(
                            {
                                "index": index,
                                "url": img_src,
                                "data": f"data:{mime_type};base64,{base64_data}",
                            }
                        )
                        break
                except Exception as e:
                    logger.error(
                        f"Attempt {attempt + 1} failed to fetch or encode image {img_src}: {e}"
                    )
                    if attempt == max_retries - 1:
                        logger.error(
                            f"Giving up on image {img_src} after {max_retries} attempts"
                        )
        return image_data

    async def _fetch_images_async(
        self, image_urls: list[tuple[int, str]]
    ) -> list[dict]:
        image_data = []
        for index, img_src in image_urls:
            max_retries = 3
            if img_src.startswith("data:"):
                logger.info(f"Adding inline/data image as is: {img_src}")
                image_data.append({"index": index, "url": img_src, "data": img_src})
                continue
            if not img_src.startswith("http") and self.async_page.url:
                host = f"{urlparse(self.async_page.url).scheme}://{urlparse(self.async_page.url).netloc}"
                img_src = urljoin(host, img_src)
            for attempt in range(max_retries):
                try:
                    async with self.async_page.expect_response(
                        img_src
                    ) as response_info:
                        await self.async_page.goto(img_src)
                    response = await response_info.value
                    if response.ok:
                        mime_type = response.headers.get("content-type", "image/jpeg")
                        image_bytes = await response.body()
                        image_bytes = process_image(image_bytes)
                        base64_data = base64.b64encode(image_bytes).decode("utf-8")
                        image_data.append(
                            {
                                "index": index,
                                "url": img_src,
                                "data": f"data:{mime_type};base64,{base64_data}",
                            }
                        )
                        break
                except Exception as e:
                    logger.error(
                        f"Attempt {attempt + 1} failed to fetch or encode image {img_src}: {e}"
                    )
                    if attempt == max_retries - 1:
                        logger.error(
                            f"Giving up on image {img_src} after {max_retries} attempts"
                        )
        return image_data

    def _resolve_text_w_metadata_sync(
        self, content, title=None, description=None, resolve_images: bool = False
    ) -> tuple[str, dict, list[dict]]:
        text, metadata, image_urls = self._parse_content_with_soup(content)
        title = title or metadata.get("title", "")
        description = description or metadata.get("description", "")

        text = text_format_sync(text)

        # Validate content
        is_valid, explanation = validate_news_article_sync(text, title, description)
        if not is_valid:
            raise Exception(f"Content validation failed: {explanation}")

        if resolve_images:
            image_data = self._fetch_images_sync(image_urls)
        else:
            image_data = None
        return text, metadata, image_data

    async def _resolve_text_w_metadata_async(
        self, content, title=None, description=None, resolve_images: bool = False
    ) -> tuple[str, dict, list[dict]]:
        text, metadata, image_urls = self._parse_content_with_soup(content)
        title = title or metadata.get("title", "")
        description = description or metadata.get("description", "")

        text = await text_format(text)

        # Validate content
        is_valid, explanation = await validate_news_article(text, title, description)
        if not is_valid:
            raise Exception(f"Content validation failed: {explanation}")

        if resolve_images:
            image_data = await self._fetch_images_async(image_urls)
        else:
            image_data = None
        return text, metadata, image_data

    def _build_results(self, url, resolved_url, content, text, metadata, image_data):
        return UrlResult(
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
            metadata=json.dumps(metadata),
            original_content=content,
            human_readable_content=text,
            image_data=image_data,
        )

    def _resolve_url_sync(
        self, url: str, title=None, description=None, resolve_images: bool = False
    ) -> UrlResult:
        # Updated to include image data
        self._get_page_sync(url)
        self._cloudfare_sync()

        resolved_url, content = self._resolve_content_sync(url)

        if not content:
            raise Exception("Content could not be loaded")

        text, metadata, image_data = self._resolve_text_w_metadata_sync(
            content, title, description, resolve_images
        )

        results = self._build_results(
            url, resolved_url, content, text, metadata, image_data
        )

        self.page.close()
        self.page = None

        return results

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

        return resolved_url, content

    async def _resolve_url_async(
        self, url: str, title=None, description=None, resolve_images: bool = False
    ) -> UrlResult:
        if not self.async_playwright:
            self.async_playwright = await async_playwright().start()
            self.async_browser = await self.async_playwright.chromium.launch()

        await self._get_page_async(url)
        await self._cloudfare_async()

        resolved_url, content = await self._resolve_content_async(url)

        if not content:
            raise Exception("Content could not be loaded")

        text, metadata, image_data = await self._resolve_text_w_metadata_async(
            content, title, description, resolve_images
        )

        results = self._build_results(
            url, resolved_url, content, text, metadata, image_data
        )

        await self.async_page.close()
        self.async_page = None

        return results

    async def async_close(self):
        if self.async_browser is not None:
            await self.async_browser.close()
            self.async_browser = None
        if self.async_playwright is not None:
            await self.async_playwright.stop()
            self.async_playwright = None

    def close(self):
        try:
            if self.is_async:
                if asyncio.get_event_loop().is_running():
                    nest_asyncio.apply()
                    asyncio.run(self.async_close())
                else:
                    asyncio.run(self.async_close())
            else:
                if self.browser is not None:
                    self.browser.close()
                    self.browser = None
                if self.playwright is not None:
                    self.playwright.stop()
                    self.playwright = None
        except Exception as e:
            print(f"Error while closing playwright: {e}")

    def resolve_url(
        self,
        url: str,
        title: str = None,
        description: str = None,
        resolve_images: bool = False,
    ) -> UrlResult:
        if self.is_async:
            if asyncio.get_event_loop().is_running():
                nest_asyncio.apply()
                return asyncio.run(
                    self._resolve_url_async(url, title, description, resolve_images)
                )
            else:
                return asyncio.run(
                    self._resolve_url_async(url, title, description, resolve_images)
                )
        else:
            return self._resolve_url_sync(url, title, description, resolve_images)
