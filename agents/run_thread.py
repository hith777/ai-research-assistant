import argparse
import openai
import time
from infra.config import Config
from agents.agent_runner import AssistantRegistrar


class ThreadExecutor:
    def __init__(self, assistant_id: str):
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
        from tools.cost_tracker import CostTracker
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
                    # ⏳ Process normally
                    paper = Paper.from_pdf(path)
                    paper.chunk_text()
                    result = SummarizerService.summarize_paper(paper.chunks, style)

                    # 💾 Save to cache
                    CacheManager.save_summary(file_hash, style, result)
                    print("💾 Summary saved to cache.")

                # 📊 Token + cost output
                usage = result.get("total_usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                total_tokens = usage.get("total_tokens", 0)

                model = Config.OPENAI_MODEL
                cost = CostTracker.estimate_cost(model, prompt_tokens, completion_tokens)

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
                    result = SummarizerService.compare_papers(path1, path2, style)
                    CacheManager.save_summary(combined_key, style, result)
                    print("Comparison saved to cache.")

                usage = result.get("total_usage", {})
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                total_tokens = usage.get("total_tokens", 0)

                model = Config.OPENAI_MODEL
                cost = CostTracker.estimate_cost(model, prompt_tokens, completion_tokens)

                print(f"📊 Token Usage: {total_tokens} tokens")
                print(f"💸 Estimated Cost ({model}): ${cost:.6f}")

                outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": result["comparison"]
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

    args = parser.parse_args()

    tools = AssistantRegistrar.register_tools()
    assistant_id = AssistantRegistrar.get_or_create_assistant(Config.OPENAI_MODEL, tools)
    executor = ThreadExecutor(assistant_id)

    # Build message
    if args.message:
        message = args.message

    elif args.file and args.file2:
        message = f"Compare these two papers: {args.file} and {args.file2} [style={args.style}]"

    elif args.file:
        message = f"Summarize this paper: {args.file} [style={args.style}]"

    else:
        message = "Summarize this paper: sample_papers/sample_test_paper.pdf"

    # Run assistant thread
    executor.send_message(message)
    run = executor.run()
    executor.wait_for_completion(run.id)
    response = executor.get_final_response()

    print("\n🧠 Assistant Reply:\n")
    print(response)


