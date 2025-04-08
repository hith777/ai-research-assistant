### `README.md`

# AI Research Assistant

An intelligent research assistant powered by LLM agents.
This system reads, compresses, summarizes, and compares academic research papers using models like OpenAI’s GPT. It supports customizable summary styles (layman, technical, short), efficient chunk compression, caching for repeated use, token usage and cost tracking, and seamless CLI or OpenAI Assistant integration.

Built with scalability in mind — ready for multi-model support, tool expansion (e.g., explain terms, highlight figures), and UI/agent deployments.


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
├── agents/                # Assistant integration, CLI, agent_runner
│   ├── llm_client.py      # Chat completion functions
│   ├── run_thread.py      # CLI + Assistant execution
│   └── agent_runner.py    # Registers assistant tools
│
├── domain/                # Core models
│   ├── paper.py           # Paper class
│   └── chunk.py           # Chunk class
│
├── services/              # Business logic
│   └── summarizer.py      # Summarization and comparison
│
├── tools/                 # Utility layer
│   ├── pdf_parser.py      # PDF extraction
│   ├── text_chunker.py    # Token-based chunking
│   ├── tools_handler.py   # Calling summarizer functions manually
│   ├── cost_tracker.py    # Token cost calculation
│   └── cache_manager.py   # Summary caching system
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
├── cache/                 # Saved summary and comparison files
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
