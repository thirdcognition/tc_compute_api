import os
from pydantic_settings import BaseSettings
from pydantic import Field


class EmailConfig(BaseSettings):
    # Configurable defaults
    title: str = Field(
        default_factory=lambda: os.getenv("EMAIL_TITLE", "New Episodes Generated")
    )
    footer_text: str = Field(
        default_factory=lambda: os.getenv(
            "EMAIL_FOOTER_TEXT", "Thank you for staying updated with us!"
        )
    )
    subscription_link: str = Field(
        default_factory=lambda: os.getenv(
            "EMAIL_SUBSCRIPTION_LINK", "https://example.com/preferences"
        )
    )
    preference_link: str = Field(
        default_factory=lambda: os.getenv(
            "EMAIL_PREFERENCE_LINK", "https://example.com/unsubscribe"
        )
    )

    # Styles
    background_color: str = Field(
        default_factory=lambda: os.getenv("EMAIL_BACKGROUND_COLOR", "#ffffff")
    )
    border_color: str = Field(
        default_factory=lambda: os.getenv("EMAIL_BORDER_COLOR", "#ddd")
    )
    text_color: str = Field(
        default_factory=lambda: os.getenv("EMAIL_TEXT_COLOR", "#000000")
    )
    secondary_text_color: str = Field(
        default_factory=lambda: os.getenv("EMAIL_SECONDARY_TEXT_COLOR", "#555555")
    )
    link_color: str = Field(
        default_factory=lambda: os.getenv("EMAIL_LINK_COLOR", "#007bff")
    )
    font_family: str = Field(
        default_factory=lambda: os.getenv(
            "EMAIL_FONT_FAMILY",
            "'Helvetica Neue', Helvetica, Arial, Verdana, sans-serif",
        )
    )
    header_font_size: str = Field(
        default_factory=lambda: os.getenv("EMAIL_HEADER_FONT_SIZE", "24px")
    )
    body_font_size: str = Field(
        default_factory=lambda: os.getenv("EMAIL_BODY_FONT_SIZE", "16px")
    )
    footer_font_size: str = Field(
        default_factory=lambda: os.getenv("EMAIL_FOOTER_FONT_SIZE", "12px")
    )
    padding: str = Field(default_factory=lambda: os.getenv("EMAIL_PADDING", "20px"))
    block_padding: str = Field(
        default_factory=lambda: os.getenv("EMAIL_BLOCK_PADDING", "20px")
    )
    margin_bottom: str = Field(
        default_factory=lambda: os.getenv("EMAIL_MARGIN_BOTTOM", "10px")
    )

    # Dark mode styles
    dark_background_color: str = Field(
        default_factory=lambda: os.getenv("EMAIL_DARK_BACKGROUND_COLOR", "#000000")
    )
    dark_text_color: str = Field(
        default_factory=lambda: os.getenv("EMAIL_DARK_TEXT_COLOR", "#ffffff")
    )
    dark_link_color: str = Field(
        default_factory=lambda: os.getenv("EMAIL_DARK_LINK_COLOR", "#4e9af1")
    )

    # Display controls
    show_panel_title: bool = Field(
        default_factory=lambda: os.getenv("EMAIL_SHOW_PANEL_TITLE", "true").lower()
        == "true"
    )
    show_description: bool = Field(
        default_factory=lambda: os.getenv("EMAIL_SHOW_DESCRIPTION", "true").lower()
        == "true"
    )
    show_sources: bool = Field(
        default_factory=lambda: os.getenv("EMAIL_SHOW_SOURCES", "true").lower()
        == "true"
    )
    show_footer: bool = Field(
        default_factory=lambda: os.getenv("EMAIL_SHOW_FOOTER", "true").lower()
        == "false"
    )
