from services.summarizer import SummarizerService
from domain.paper import Paper

def summarize_pdf(path: str, style: str = "default") -> str:
    result = SummarizerService.summarize_paper(Paper.from_pdf(path).chunk_text(), style)
    return (
        f"📄 Summary:\n{result['final_summary']}\n\n"
        f"📊 Token Usage:\nTotal Tokens: {result['total_usage']['total_tokens']}"
    )

def compare_papers(file_path_1: str, file_path_2: str, style: str = "default") -> str:
    result = SummarizerService.compare_papers(file_path_1, file_path_2, style)
    return (
        f"📄 Comparison:\n{result['comparison']}\n\n"
        f"📊 Token Usage:\nTotal Tokens: {result['total_usage']['total_tokens']}"
    )
