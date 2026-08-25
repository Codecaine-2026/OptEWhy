from typing import Protocol


class ChatResponder(Protocol):
    def respond(self, message: str) -> str: ...
