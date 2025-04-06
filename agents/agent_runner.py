import openai
from infra.config import Config


class AssistantRegistrar:
    @staticmethod
    def register_tools() -> list:
        return [
            {
                "type": "function",
                "function": {
                    "name": "summarize_pdf",
                    "description": "Summarizes a research paper PDF given its local path.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "The full path to the PDF file on disk"
                            }
                        },
                        "required": ["path"]
                    }
                }
            }
        ]
    
    @staticmethod
    def get_or_create_assistant(model: str, tools: list) -> str:
        """
        Retrieves the saved Assistant ID if available, otherwise creates a new assistant
        with the given tools and model, saves its ID locally, and returns it.

        This prevents repeated assistant creation and ensures consistent reuse
        across sessions.

        Args:
            model (str): The model name to use for the assistant (e.g., gpt-4).
            tools (list): A list of tool schemas to register with the assistant.

        Returns:
            str: The assistant ID to use for future interactions.
        """
        try:
            with open(".assistant_id", "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            print("⚠️ Assistant ID not found. Creating a new assistant...")

            openai.api_key = Config.OPENAI_API_KEY
            assistant = openai.beta.assistants.create(
                name="Paper Summarizer",
                instructions="You summarize research papers using a registered summarize_pdf function.",
                tools=tools,
                model=model
            )

            with open(".assistant_id", "w") as f:
                f.write(assistant.id)

            print("Assistant created and saved.")
            return assistant.id




# CLI entry point
if __name__ == "__main__":
    tools = AssistantRegistrar.register_tools()
    assistant_id = AssistantRegistrar.get_or_create_assistant(Config.OPENAI_MODEL, tools)

    # 🔐 Save assistant ID to a local file
    with open(".assistant_id", "w") as f:
        f.write(assistant_id)
    print("Assistant ID saved to .assistant_id")
