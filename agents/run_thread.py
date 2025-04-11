import argparse
import openai
import time
from infra.config import Config
from agents.agent_runner import AssistantRegistrar
from agents.llm_client import LLMClient
#from tools.prototype_figure_analyzer import FigureAnalyzer
from domain.paper import Paper
from services.explainer import TermExplainer


class ThreadExecutor:
    def __init__(self, assistant_id: str, provider: str = None, model: str = None):
        self.provider = provider
        self.model = model
        self.assistant_id = assistant_id
        self.thread = openai.beta.threads.create()
        openai.api_key = Config.OPENAI_API_KEY

    def send_message(self, message: str):
        openai.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=message
        )

    def run(self):
        return openai.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant_id,
        )

    def wait_for_completion(self, run_id: str):
        tool_handled = False

        while True:
            run = openai.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=run_id)

            if run.status == "completed":
                return run

            elif run.status == "requires_action" and not tool_handled:
                self.handle_tool_calls(run)
                tool_handled = True  # Prevents re-processing
                time.sleep(1)        # Wait briefly before next run check

            elif run.status in {"queued", "in_progress"}:
                time.sleep(1)
                continue

            else:
                raise Exception(f"[ERROR] Unexpected run status: {run.status}")


    def handle_tool_calls(self, run):
        from services.summarizer import SummarizerService
        from domain.paper import Paper
        from tools.cache_manager import CacheManager
        from infra.config import Config
        from utils.message_utils import extract_style_from_messages

        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        outputs = []

        for tool_call in tool_calls:
            func_name = tool_call.function.name
            args = eval(tool_call.function.arguments)

            if func_name == "summarize_pdf":
                path = args["path"]
                # Extract optional style from message if included like: [style=layman]
                style = args.get("style") or extract_style_from_messages(self.thread.id)


                print(f"\n📄 Summarizing file: {path}")
                file_hash = CacheManager.get_file_hash(path)

                # 🔍 Check cache
                if CacheManager.is_cached(file_hash, style):
                    print("✅ Loaded summary from cache!")
                    result = CacheManager.load_cached_summary(file_hash, style)
                else:
                    result = SummarizerService.summarize_paper(path, style, provider=self.provider, model=self.model)

                    # 💾 Save to cache
                    CacheManager.save_summary(file_hash, style, result)
                    print("💾 Summary saved to cache.")

                # 📊 Token + cost output
                usage = result.get("total_usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                total_tokens = usage.get("total_tokens", 0)

                model = Config.OPENAI_MODEL
                cost = result.get("cost", 0.0)

                print(f"📊 Token Usage: {total_tokens} tokens")
                print(f"💸 Estimated Cost ({model}): ${cost:.6f}")

                outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": result["final_summary"]
                })
            
            elif func_name == "compare_papers":
                path1 = args["file_path_1"]
                path2 = args["file_path_2"]
                style = args.get("style") or extract_style_from_messages(self.thread.id)


                print(f"\n Comparing files:\n- {path1}\n- {path2}")
                combined_key = CacheManager.get_combined_hash(path1, path2)

                # Check cache
                if CacheManager.is_cached(combined_key, style):
                    print("Loaded comparison from cache!")
                    result = CacheManager.load_cached_summary(combined_key, style)
                else:
                    result = SummarizerService.compare_papers(path1, path2, style, provider=self.provider, model=self.model)
                    CacheManager.save_summary(combined_key, style, result)
                    print("Comparison saved to cache.")

                usage = result.get("total_usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                total_tokens = usage.get("total_tokens", 0)

                model = Config.OPENAI_MODEL
                cost = result.get("cost", 0.0)

                print(f"📊 Token Usage: {total_tokens} tokens")
                print(f"💸 Estimated Cost ({model}): ${cost:.6f}")

                outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": result["comparison"]
                })
            
            elif func_name == "explain_term":
                from services.explainer import TermExplainer
                from domain.paper import Paper

                path = args["path"]
                term = args.get("term")
                style = args.get("style", "default")

                paper = Paper.from_pdf(path)

                if term:
                    result = TermExplainer.explain_term(term, paper, style)
                    output = result["summary"]
                else:
                    terms = TermExplainer.extract_terms(paper)
                    output = "📚 Top terms in the paper:\n" + "\n".join(f"- {t}" for t in terms)

                outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": output
                })
            
            elif func_name == "search_by_author":
                from services.author_search import AuthorSearch

                name = args["name"]
                folder = args["folder"]

                results = AuthorSearch.search_by_author(name, folder)
                if not results:
                    output = f"No papers found for author '{name}'."
                else:
                    output = f"📚 Found {len(results)} papers by '{name}':\n\n"
                    for r in results:
                        output += f"📄 {r['title']}\n👥 {', '.join(r['authors'])}\n📁 {r['path']}\n\n"

                outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": output
                })
                

        openai.beta.threads.runs.submit_tool_outputs(
            thread_id=self.thread.id,
            run_id=run.id,
            tool_outputs=outputs
        )



    def get_final_response(self):
        messages = openai.beta.threads.messages.list(thread_id=self.thread.id)
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                return msg.content[0].text.value
        return None


# CLI Entry Point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run assistant thread to summarize or compare papers.")
    parser.add_argument("--file", type=str, help="Path to PDF to summarize or compare (required).")
    parser.add_argument("--file2", type=str, help="Second PDF for comparison (if running compare_papers).")
    parser.add_argument("--style", type=str, default="default", help="Style for summarization or comparison.")
    parser.add_argument("--message", type=str, help="Optional custom message to send to the assistant.")
    parser.add_argument("--provider", type=str, help="LLM provider (openai, gemini, claude, etc.)")
    parser.add_argument("--model", type=str, help="Model to use (gpt-4, pro, claude-2, etc.)")
    parser.add_argument("--health-check", action="store_true", help="Run a health check for the selected LLM provider/model")
    parser.add_argument("--experimental-highlight-figures", action="store_true", help="(Prototype) Attempt to explain figures/tables")
    parser.add_argument("--explain-term", nargs="?", const="", help="Explain a term using paper context (leave blank to extract keywords)")
    parser.add_argument("--search-author", type=str, help="Search local PDFs for papers by this author")
    parser.add_argument("--folder", type=str, help="Folder path for searching PDFs")





    args = parser.parse_args()

    tools = AssistantRegistrar.register_tools()
    assistant_id = AssistantRegistrar.get_or_create_assistant(Config.OPENAI_MODEL, tools)
    executor = ThreadExecutor(assistant_id, provider=args.provider, model=args.model)

    # Build message
    if args.message:
        message = args.message

    elif args.file and args.file2:
        message = f"Compare these two papers: {args.file} and {args.file2} [style={args.style}]"

    elif args.file:
        message = f"Summarize this paper: {args.file} [style={args.style}]"

    else:
        message = "Summarize this paper: sample_papers/sample_test_paper.pdf"
    
    if args.health_check:
        result = LLMClient.health_check(args.provider, args.model)
        print(f"\n🔧 LLM Health Check:\nProvider: {result['provider']}\nModel: {result['model']}\nStatus: {result['status']}\nMessage: {result['message']}")
        exit()
    
    if args.file and args.explain_term is not None:
        from domain.paper import Paper
        from services.explainer import TermExplainer

        paper = Paper.from_pdf(args.file)

        if args.explain_term.strip():
            result = TermExplainer.explain_term(args.explain_term.strip(), paper)
            print(f"\n🧠 Explanation for '{result['term']}':\n{result['summary']}")
            print(f"🔎 Source: {result['source']}")
        else:
            print("📚 Top terms found in the paper:")
            keywords = TermExplainer.extract_terms(paper)
            if not keywords:
                print("[!] No terms found — the paper might be too short or LLM failed.")
            else:
                for i, term in enumerate(keywords, 1):
                    print(f"{i}. {term}")
        exit()

    if args.search_author and args.folder:
        from services.author_search import AuthorSearch

        results = AuthorSearch.search_by_author(args.search_author, args.folder)

        if not results:
            print(f"No papers found for author: {args.search_author}")
        else:
            print(f"\n📚 Found {len(results)} papers by '{args.search_author}':\n")
            for r in results:
                print(f"📄 {r['title']}")
                print(f"👥 Authors: {', '.join(r['authors'])}")
                print(f"📁 Path: {r['path']}\n")

        exit()


    
    #Experimental feature to analyze figures and tables
    # if args.file and args.highlight_figures:

    #     print(f"\n🔎 Analyzing figures in: {args.file}")
    #     analyzer = FigureAnalyzer(args.file)
    #     explanations = analyzer.explain_figures()

    #     if not explanations:
    #         print("⚠️ No figure or table references found.")
    #     else:
    #         print("\n📊 Figure/Table Explanations:\n")
    #         for label, explanation in explanations.items():
    #             print(f"--- {label} ---")
    #             print(explanation)
    #             print()
    #     exit()



    # Run assistant thread
    executor.send_message(message)
    run = executor.run()
    executor.wait_for_completion(run.id)
    response = executor.get_final_response()

    print("\n🧠 Assistant Reply:\n")
    print(response)


