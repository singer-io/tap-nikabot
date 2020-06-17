from typing import Any

# Ignore any attributes or modules that aren't defined
def __getattr__(attr: str) -> Any: ...