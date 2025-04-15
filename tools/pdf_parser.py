from typing import Optional, List
import pdfplumber
import logging

logging.getLogger("pdfminer").setLevel(logging.ERROR)

class PDFParser:

    @staticmethod
    def extract_info(pdf_path: str) -> Optional["ParsedPDF"]:
        """
        Extracts text and (and placeholder figure markers) from a PDF file.
        :param pdf_path: Path to the PDF file.
        :return: ParsedPDF object containing the extracted text and simulated figure markers.
        """
        raw_text = ""
        figure_markers = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()

                    if page_text:
                        raw_text += page_text + "\n"

                        # Simulate figure markers
                        if "figure" in page_text.lower():
                            figure_markers.append(f"Figure detected on Page {i + 1}")
        except Exception as e:
            print(f"Error reading the PDF file {pdf_path}: {e}")
            return ParsedPDF(raw_text = "", figure_markers = [])
        


        return ParsedPDF(raw_text, figure_markers)

class ParsedPDF:
    def __init__(self, raw_text: str, figure_markers: list[str] = None):
        self._raw_text = raw_text
        self._figure_markers = figure_markers if figure_markers is not None else []

    @property
    def raw_text(self) -> str:
        return self._raw_text
    
    @property
    def figure_markers(self) -> List[str]:
        return self._figure_markers