import re
import pdfplumber
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
        Scans all pages for lines referencing figures or tables, including variants like:
        - Figure 1, Fig. 2, fig 3a, TABLE I, etc.
        Returns: {"Figure 1": [...lines...], "Table III": [...lines...], ...}
        """
        figure_refs = {}

        # Comprehensive pattern for figure/table references (incl. roman numerals)
        pattern = r"\b(?:(Fig\.?|Figure|Table|TABLE|FIG))\s*([IVXLCDM]+|\d+[a-zA-Z]?)"

        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    for line in text.split("\n"):
                        matches = re.findall(pattern, line, flags=re.IGNORECASE)
                        for match in matches:
                            label_type, label_num = match
                            normalized_label = f"{label_type.capitalize()} {label_num}".strip()
                            normalized_label = re.sub(r"\s+", " ", normalized_label)  # clean double spaces
                            if normalized_label not in figure_refs:
                                figure_refs[normalized_label] = []
                            figure_refs[normalized_label].append(f"Page {i+1}: {line.strip()}")
        except Exception as e:
            print(f"[ERROR] Figure reference extraction failed: {e}")

        return figure_refs


    def explain_figures(self) -> Dict[str, str]:
        """
        Uses the LLM to explain what each detected figure or table represents.
        Returns: Dict like { "Figure 1": "Explanation", ... }
        """
        refs = self.extract_figure_references()
        explanations = {}

        for label, lines in refs.items():
            prompt = (
                f"You are reading a research paper. The following lines reference {label}.\n"
                f"Based on these references, explain in simple terms what {label} likely represents:\n\n"
                + "\n".join(lines)
            )

            try:
                result = self.llm.chat_completion(prompt)
                explanations[label] = result["text"].strip()
            except Exception as e:
                print(f"[ERROR] LLM failed to explain {label}: {e}")
                explanations[label] = "[Explanation failed]"

        return explanations
