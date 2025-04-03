from tools.pdf_parser import PDFParser
class Paper:
    def __init__(self, title: str, authors: list[str], abstract: str, source: str, raw_text: str):
        self._title = title
        self._authors = authors
        self._abstract = abstract
        self._source = source
        self._raw_text = raw_text
    
    @classmethod
    def from_pdf(cls, pdf_path: str) -> "Paper":
        parsed_file = PDFParser.extract_info(pdf_path)

        raw_text = parsed_file.raw_text

        #simulate the extraction of title, authors, and abstract
        title = input("Enter the title of the paper: ")
        authors_input= input("Enter the authors of the paper (comma separated): ")
        authors = [author.strip() for author in authors_input.split(',')]
        abstract = input("Enter the abstract of the paper: ")

        return cls(title=title, authors=authors, abstract=abstract, source=pdf_path, raw_text=raw_text)

    @property
    def title(self) -> str:
        return self._title
    
    @property
    def authors(self) -> list[str]:
        return self._authors

    @property
    def abstract(self) -> str:
        return self._abstract
    
    @property
    def source(self) -> str:
        return self._source
    
    @property
    def raw_text(self) -> str:
        return self._raw_text