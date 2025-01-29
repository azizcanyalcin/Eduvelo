import re

class TextProcessor:
    """Handles text-related operations such as paragraph splitting and formatting."""
    
    @staticmethod
    def split_into_paragraphs(text):
        text_no_headers = re.sub(r"^##.*\n", "", text)
        return [p.strip() for p in text_no_headers.split("\n\n") if p.strip()]