from playwright.sync_api import sync_playwright


class GoogleNewsResolver:
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

    def resolve_url(self, url: str) -> str:
        page = self.browser.new_page()  # Use the incognito context to create a new page
        page.goto(url)

        # Try to accept consent using known selectors
        for selector in self.consent_accept_selectors.values():
            if page.locator(selector).count() > 0:
                try:
                    page.click(selector)
                    page.wait_for_load_state("networkidle")
                except Exception as e:
                    print(f"Error clicking consent button: {e}")
                break

        # Get the final URL
        final_url = page.url
        page.close()
        return final_url

    def close(self):
        self.browser.close()
        self.playwright.stop()
