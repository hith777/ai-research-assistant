from typing import Optional
from infra.config import Config

class CostTracker:
    # Prices in USD per 1K tokens
    MODEL_PRICING = {
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-0125-preview": {"input": 0.01, "output": 0.03},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    }

    @staticmethod
    def estimate_cost(
        prompt_tokens: int,
        completion_tokens: int,
        cost_per_1k_tokens: Optional[dict] = None,
        model_name: Optional[str] = None
    ) -> float:
        """
        Estimate cost based on token usage and optional cost info.

        Args:
            prompt_tokens (int): Number of prompt tokens used.
            completion_tokens (int): Number of completion tokens used.
            cost_per_1k_tokens (dict, optional): {
                "input": float,  # $ per 1k prompt tokens
                "output": float  # $ per 1k completion tokens
            }
            model_name (str, optional): Used only if cost dict not provided.

        Returns:
            float: Estimated dollar cost for the request.
        """
        if not cost_per_1k_tokens:
            # fallback to older behavior (basic OpenAI costs from .env)
            model_name = model_name or "gpt-3.5"
            if "gpt-4" in model_name:
                input_cost = 0.03
                output_cost = 0.06
            else:
                input_cost = 0.001
                output_cost = 0.002
        else:
            input_cost = cost_per_1k_tokens.get("input", 0.001)
            output_cost = cost_per_1k_tokens.get("output", 0.002)

        cost = (prompt_tokens / 1000) * input_cost + (completion_tokens / 1000) * output_cost
        return round(cost, 6)
