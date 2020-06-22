from typing import Callable, Any, TypeVar, Type, Iterator

F = TypeVar('F', bound=Callable[..., Any])


# Ignore other attributes, we just want to fix the decorator
def __getattr__(attr: str) -> Any: ...
def on_exception(wait_gen: Callable[..., Iterator[int]],
                 exception: Type[Exception],
                 max_tries: int = ...,
                 max_time: Any = ...,
                 jitter: Any = ...,
                 giveup: Any = ...,
                 on_success: Any = ...,
                 on_backoff: Any = ...,
                 on_giveup: Any = ...,
                 logger: Any = ...,
                 **wait_gen_kwargs: Any) -> Callable[[F], F]: ...
