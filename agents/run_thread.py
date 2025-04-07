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
        while True:
            run = openai.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=run_id)

            if run.status == "completed":
                return run

            elif run.status == "requires_action":
                self.handle_tool_calls(run)
                continue

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

        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        outputs = []

        for tool_call in tool_calls:
            func_name = tool_call.function.name
            args = eval(tool_call.function.arguments)

            if func_name == "summarize_pdf":
                path = args["path"]
                style = "default"  # Later, this could be passed in dynamically

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


# 🎯 CLI Entry Point
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run assistant thread to summarize papers.")
    parser.add_argument("--file", type=str, help="Path to PDF to summarize")
    parser.add_argument("--message", type=str, help="Custom message to send")

    args = parser.parse_args()
    tools = AssistantRegistrar.register_tools()
    assistant_id = AssistantRegistrar.get_or_create_assistant(Config.OPENAI_MODEL, tools)

    executor = ThreadExecutor(assistant_id)

    # Build input message
    if args.file:
        message = f"Summarize this paper: {args.file}"
    elif args.message:
        message = args.message
    else:
        message = "Summarize this paper: docs/sample_test_paper.pdf"

    executor.send_message(message)
    run = executor.run()
    executor.wait_for_completion(run.id)
    response = executor.get_final_response()

    print("\n🧠 Assistant Reply:\n")
    print(response)
