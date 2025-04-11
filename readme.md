### `README.md`

# AI Research Assistant

An intelligent research assistant powered by LLM agents.
This system reads, compresses, summarizes, and compares academic research papers using models like OpenAI’s GPT. It supports customizable summary styles (layman, technical, short), efficient chunk compression, caching for repeated use, token usage and cost tracking, and seamless CLI or OpenAI Assistant integration.

Built with scalability in mind — ready for multi-model support, tool expansion (e.g., explain terms, highlight figures), and UI/agent deployments.


## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ai-research-assistant.git
cd ai-research-assistant
```

### 2. Create a Virtual Environment

```bash
python3 -m venv agent1env
source agent1env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> Ensure you are using OpenAI SDK v1.0+ (`openai>=1.0.0`) and not the legacy API.

### 4. Set Up Environment Variables

Create a `.env` file:

```dotenv
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-3.5-turbo
LLM_PROVIDER=openai
MAX_TOKENS_PER_REQUEST=3000
MAX_SUMMARY_TOKENS=800
MAX_EMBED_TOKENS=8000
DEBUG_MODE=true
```

---

## How to Use

### CLI Summarization

```bash
python -m agents.run_thread --file docs/sample_paper.pdf --style layman
```

### CLI Comparison

```bash
python -m agents.run_thread --file docs/paper1.pdf --file2 docs/paper2.pdf --style technical
```

### CLI Key Terms Explain

```bash
python -m agents.run_thread --file docs/sample_paper.pdf --explain-term dropout
```

### CLI List Top Terms In a Paper

```bash
python -m agents.run_thread --file docs/sample_paper.pdf --explain-term dropout
```

### CLI Search Papers of an Author

```bash
python -m agents.run_thread --search-author "Marinelli" --folder docs/
```

---

## Assistant Tool Usage

1. Run the assistant thread:

```bash
python -m agents.run_thread --file docs/sample_paper.pdf
```

> The assistant will use tools like `summarize_pdf` or `compare_papers` automatically.

---

## Architecture Overview

```
ai-research-assistant/
│
├── agents/                     # Assistant integration, CLI, agent_runner
│   ├── llm_client.py           # Chat completion functions
│   ├── run_thread.py           # CLI + Assistant execution
│   └── agent_runner.py         # Registers assistant tools
│
├── domain/                     # Core models
│   ├── paper.py                # Paper class
│   └── chunk.py                # Chunk class
│
├── services/                   # Business logic
│   ├── summarizer.py           # Summarization and comparison
│   ├── explainer.py            # Explainer Key Terms
│   ├── metadata_extractor.py   # Extracting Titles and Authors
│   └── author_search.py        # Search papers of an author
│
├── tools/                      # Utility layer
│   ├── pdf_parser.py           # PDF extraction
│   ├── text_chunker.py         # Token-based chunking
│   ├── tools_handler.py        # Calling summarizer functions manually
│   ├── cost_tracker.py         # Token cost calculation
│   ├── author_cache.py         # Saving Papers by Author
│   ├── figure_analyzer.py      # Prototype Model
│   └── cache_manager.py        # Summary caching system
│
├── infra/                 # Config and environment
│   ├── config.py          # Centralized configuration
│   └── models.py          # Available Models
│
├── utils/                 # Utility tools for reusability
│   ├── message_utils.py   # Utils for prompt customization
│   └── token_counter.py   # Counting tokens
│
├── docs/                  # Sample test papers
├── cache/                 # Saved summary and comparison and Author-paper files
└── tests/                 # Future tests (Pytest-compatible)
```

---

## Summary Flow

1. PDF parsed → raw text extracted
2. Text chunked using `tiktoken`
3. Each chunk summarized using LLM
4. Summaries merged into final summary
5. Token cost tracked and cached by SHA-256 + style
6. Optional: full paper compressed for comparison
7. Output returned via CLI or Assistant

### Current Tool Capabilities

- `summarize_pdf` — summarizes a paper using chunking/compression
- `compare_papers` — compresses + compares two papers side-by-side
- `explain_term` — explains a term using context from the paper (or fallback)
- `search_by_author` — searches cached/indexed papers by author name


---

## Roadmap

- Add Gemini and Claude integration (multi-LLM support)
- GUI interface (Streamlit or Gradio)
- PostgreSQL/SQLite backend for paper storage and metadata
- Arxiv API integration for direct paper fetching
- Automatic chunk refinement for long-context windows (e.g., GPT-4 Turbo)
- Searchable summary history
- Embedding-based similarity analysis between papers

---

## Features

### v0.1.0
- Initial architecture and folder structure
- PDF parsing with `pdfplumber`
- Domain model for `Paper` and `Chunk`
- Text chunking using `tiktoken`

### v0.2.0
- LLM client with OpenAI SDK
- Summarization of individual chunks
- Merging chunk summaries into a full paper summary
- Summary style customization (`default`, `layman`, `short`, `technical`)

### v0.3.0
- Token usage and cost estimation
- Modular summarizer service
- Assistant tool: `summarize_pdf`
- Cache system for summaries using SHA-256 + style
- CLI with `argparse` support
- Assistant runner with tool registration
- Style parsing from messages
- CLI usage with `--file` and `--style`

### v0.4.0
- Added support for `compare_papers` tool
- Compression of full paper before comparison
- Caching of comparisons
- Cost tracking for comparisons
- Dual-input CLI via `--file` and `--file2`
- Resolved multiple tool execution in agent loops
- Logging suppression for `pdfminer` warnings
- Cleaner thread execution and assistant replies

### v0.4.1
- Accurate token-based cost estimation using model-aware pricing
- summarize_paper and compare_papers return clean JSON with:
    - summary / comparison
    - style
    - source
    - chunks
    - usage (tokens)
    - cost (dollar value)
- Removed cost calculation logic from CLI — moved to service layer
- Fully ready for UI / API consumption

### Prototype Feature (Archived) v0.5.0
- `highlight_figures()` – Initial attempt using PyMuPDF + LLM caption summarization
- Status: archived for future multimodal LLM (GPT-4V, Claude 3 Opus, etc.)
- Fails on layout inconsistencies and figure detection hallucinations
- Code preserved in `tools/prototype_figure_analyzer.py`

### v0.5.1
- Added `explain_term` tool to explain key terms from a paper
- Token-aware routing: uses full paper if small, chunks if large
- Fallback explanation if term not found in context
- Supports explanation styles (default, layman, technical, short, verbose)
- Auto-extracts top terms if no specific term is requested
- Agent and CLI support for `--explain-term`
- Output includes source label: contextual, chunked, or fallback

### v0.5.2
- Cleaned tokenizer abstraction via `TokenCounter.get_token_chunk()`
- Removed hardcoded tokenizer logic from Paper and services
- Clarified CLI behavior for optional `--explain-term`
- Improved resilience of `extract_terms()` prompt parsing
- Tagged final `TermExplainer` version as agent-ready

### v0.5.3
- Added `search_by_author` tool to find papers by author name from folder
- Created `AuthorCache` to log author→paper mappings during paper parsing
- Hooked author caching into `Paper.from_pdf()` automatically
- CLI supports `--search-author "Name"` with `--folder "path/to/folder"`
- Author cache stored in `cache/author_index.json` to avoid duplicate processing
- Agent tool: `search_by_author(name, folder)` registered and enabled
