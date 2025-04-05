class Chunk:
    def __init__(self, index: int, text: str, token_count: int):
        self.index = index
        self.text = text
        self.token_count = token_count