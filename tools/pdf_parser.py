import os
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered


class PDFParser:
    @staticmethod
    def extract_info(pdf_path: str) -> dict:
        """
        Extracts structured markdown text and image data from a PDF using Marker.

        Args:
            pdf_path (str): Path to the PDF file.

        Returns:
            dict: {
                "raw_text": str (markdown-formatted),
                "images": List[str] (base64 or file paths depending on config),
                "metadata": dict
            }
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"File not found: {pdf_path}")

        try:
            converter = PdfConverter(artifact_dict=create_model_dict())
            rendered = converter(pdf_path)

            text, metadata, images = text_from_rendered(rendered)

            return {
                "raw_text": text,
                "images": images,
                "metadata": metadata
            }

        except Exception as e:
            print(f"[ERROR] Failed to extract PDF using Marker: {e}")
            return {
                "raw_text": "",
                "images": [],
                "metadata": {}
            }