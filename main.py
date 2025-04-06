from domain.paper import Paper
from services.summarizer import SummarizerService
from tools.cost_tracker import CostTracker
from infra.config import Config

if __name__ == "__main__":
    path = "docs/sample_test_paper.pdf"
    paper = Paper.from_pdf(path)
    paper.chunk_text()

    result = SummarizerService.summarize_paper(paper.chunks, style="default")

    summary = result["final_summary"]
    usage = result["total_usage"]

    model = Config.OPENAI_MODEL
    tokens = usage.get("total_tokens", 0)

    # We'll just assume 50% input / 50% output as an estimate for now
    prompt_tokens = tokens // 2
    completion_tokens = tokens - prompt_tokens

    cost = CostTracker.estimate_cost(model, prompt_tokens, completion_tokens)

    print("\n📄 Final Summary:\n")
    print(summary)

    print("\n📊 Token Usage:")
    print(f"Total Tokens: {tokens}")
    print(f"Estimated Cost ({model}): ${cost:.6f}")

