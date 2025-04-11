import re
import pdfplumber
import fitz
from collections import defaultdict
from typing import Dict, List, Optional
from agents.llm_client import LLMClient
import logging

logging.getLogger("pdfminer").setLevel(logging.ERROR)

class FigureAnalyzer:
    def __init__(self, pdf_path: str, llm: Optional[LLMClient] = None):
        self.pdf_path = pdf_path
        self.llm = llm or LLMClient()

    def extract_figure_references(self) -> Dict[str, List[str]]:
        """
        Scans PDF text for lines mentioning figures/tables.
        Returns normalized labels like: {"Figure 3": [line1, line2], ...}
        """
        figure_refs = defaultdict(set)

        pattern = r"\b(Fig\.?|Figure|Table|TABLE|FIG)\s*([IVXLCDM]+|\d+[a-zA-Z]?)"

        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    for line in text.split("\n"):
                        matches = re.findall(pattern, line, flags=re.IGNORECASE)
                        for match in matches:
                            raw_label = f"{match[0].strip()} {match[1].strip()}"
                            normalized = re.sub(r"\bFig\.?", "Figure", raw_label, flags=re.IGNORECASE).title()
                            normalized = re.sub(r"\s+", " ", normalized)
                            figure_refs[normalized].add(f"Page {i+1}: {line.strip()}")
        except Exception as e:
            print(f"[ERROR] Figure reference extraction failed: {e}")

        return {k: sorted(list(v)) for k, v in figure_refs.items()}

    
    def extract_visual_captions(self) -> Dict[str, str]:
        """
        Uses PyMuPDF to scan visual captions like 'Figure 2. ...' or 'TABLE II' with multi-line support.
        Returns: {"Figure 2": "Page 5: Figure 2. Architecture ...", "Table II": "Page 7: TABLE II Description..."}
        """
        captions = {}
        try:
            doc = fitz.open(self.pdf_path)

            single_line_pattern = re.compile(r"(Fig\.?|Figure|Table)\s*\d+[.:]?\s+.+", re.IGNORECASE)
            multiline_label_pattern = re.compile(r"^(Fig\.?|Figure|Table)\s*([IVXLCDM]+|\d+)$", re.IGNORECASE)

            for i, page in enumerate(doc):
                blocks = page.get_text("blocks")
                for j, block in enumerate(blocks):
                    text = block[4].strip()

                    # Match single-line captions
                    if single_line_pattern.match(text):
                        label_raw = text.split(".")[0].replace(":", "")
                        normalized = re.sub(r"\bFig\.?", "Figure", label_raw, flags=re.IGNORECASE).title()
                        normalized = re.sub(r"\s+", " ", normalized)
                        if normalized not in captions or len(text) > len(captions[normalized]):
                            captions[normalized] = f"Page {i+1}: {text}"

                    # Match multi-line labels like "TABLE II"
                    elif multiline_label_pattern.match(text):
                        next_block_text = ""
                        if j + 1 < len(blocks):
                            next_block_text = blocks[j + 1][4].strip()
                        if len(next_block_text.split()) >= 4:
                            label_raw = text.strip()
                            normalized = re.sub(r"\bFig\.?", "Figure", label_raw, flags=re.IGNORECASE).title()
                            normalized = re.sub(r"\s+", " ", normalized)
                            full_caption = f"{text}. {next_block_text}"
                            if normalized not in captions or len(full_caption) > len(captions[normalized]):
                                captions[normalized] = f"Page {i+1}: {full_caption}"

        except Exception as e:
            print(f"[ERROR] Caption extraction failed: {e}")

        return captions

    
    def explain_figures(self) -> Dict[str, str]:
        """
        Merges figure references and captions, sends to LLM for explanation.
        """

        captions = self.extract_visual_captions()
        explanations = {}

        for label, caption in sorted(captions.items()):
            prompt = (
                f"You are analyzing a research paper.\n"
                f"Here is a figure or table from the paper:\n\n"
                f"{caption}\n\n"
                "Based on this caption, explain what it shows and why it's important."
            )

            try:
                result = self.llm.chat_completion(prompt)
                explanations[label] = result["text"].strip()
            except Exception as e:
                print(f"[ERROR] LLM failed for {label}: {e}")
                explanations[label] = "[Explanation failed]"

        return explanations

