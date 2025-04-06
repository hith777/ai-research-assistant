class CostTracker:
    # Prices in USD per 1K tokens
    MODEL_PRICING = {
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-0125-preview": {"input": 0.01, "output": 0.03},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    }

    @classmethod
    def estimate_cost(cls, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        pricing = cls.MODEL_PRICING.get(model, cls.MODEL_PRICING["gpt-3.5-turbo"])
        input_cost = (prompt_tokens / 1000) * pricing["input"]
        output_cost = (completion_tokens / 1000) * pricing["output"]
        return round(input_cost + output_cost, 6)  # 6 decimal places
