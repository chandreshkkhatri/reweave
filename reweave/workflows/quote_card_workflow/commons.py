from pydantic import BaseModel


class QuoteCard(BaseModel):
    """Data model for a generated quote card."""
    quote_text: str
    attribution: str
    theme: str
    image_prompt: str
    caption: str
