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
            },
            {
                "type": "function",
                "function": {
                    "name": "compare_papers",
                    "description": "Compares two research papers and returns key similarities and differences.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path_1": {
                                "type": "string",
                                "description": "Path to the first PDF"
                            },
                            "file_path_2": {
                                "type": "string",
                                "description": "Path to the second PDF"
                            },
                            "style": {
                                "type": "string",
                                "description": "Style of the comparison (default, layman, detailed)",
                                "default": "default"
                            }
                        },
                        "required": ["file_path_1", "file_path_2"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "explain_term",
                    "description": "Explain a technical term using the paper or fallback to general knowledge.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "PDF file path"
                            },
                            "term": {
                                "type": "string",
                                "description": "Term to explain from the paper"
                            },
                            "style": {
                                "type": "string",
                                "description": "Tone: default, layman, technical, short, verbose"
                            }
                        },
                        "required": ["path", "term"]
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

            assistant = openai.beta.assistants.create(
                name="Research Paper Assistant",
                instructions=(
                    "You are a research assistant that helps with analyzing academic papers. "
                    "You can summarize research papers in different styles and compare two papers "
                    "based on their methods, goals, and findings using the registered functions. "
                    "Use the tools available to complete the user's request accurately and concisely."
                ),
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
