class CoxbuildException(Exception):
    def __init__(self, message: str, cause: Exception | None = None) -> None:
        super().__init__()
        self.message = message
        self.cause = cause

    def __str__(self) -> str:
        return f"{self.message}{f' ({repr(self.cause)})' if self.cause else ''}"

    def __repr__(self) -> str:
        return str(self)
