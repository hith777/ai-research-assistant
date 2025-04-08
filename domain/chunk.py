class Chunk:
    def __init__(self, index: int, text: str, token_count: int):
        self._index = index
        self._text = text
        self._token_count = token_count
    
    @property
    def index(self) -> int:
        return self._index
    
    @property
    def text(self) -> str:
        return self._text
    
    @property
    def token_count(self) -> int:
        return self._token_count