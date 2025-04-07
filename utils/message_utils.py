import re
import openai

def extract_style_from_messages(thread_id: str, default: str = "default") -> str:
    """
    Attempts to extract a 'style' value from the user's messages in a thread.
    Supports patterns like [style=layman] or inline mentions.

    Args:
        thread_id (str): The OpenAI thread ID.
        default (str): Fallback style if none found.

    Returns:
        str: The extracted or default style in lowercase.
    """
    try:
        messages = openai.beta.threads.messages.list(thread_id=thread_id).data
        for msg in messages:
            if msg.role == "user" and "style=" in msg.content[0].text.value:
                match = re.search(r"style=(\w+)", msg.content[0].text.value)
                if match:
                    return match.group(1).strip().lower()
    except Exception as e:
        print(f"[WARN] Failed to extract style from thread messages: {e}")

    return default
