SUPPORTED_MODELS = {
    "openai": {
        "gpt-3.5-turbo": {
            "id": "gpt-3.5-turbo",
            "max_tokens": 16000,
            "input_cost_per_1k": 0.001,
            "output_cost_per_1k": 0.002
        },
        "gpt-4": {
            "id": "gpt-4",
            "max_tokens": 8192,
            "input_cost_per_1k": 0.03,
            "output_cost_per_1k": 0.06
        },
        "gpt-4-turbo": {
            "id": "gpt-4-turbo",
            "max_tokens": 128000,
            "input_cost_per_1k": 0.01,
            "output_cost_per_1k": 0.03
        }
    },
    # More models to come later
}
