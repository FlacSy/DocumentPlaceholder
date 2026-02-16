from __future__ import annotations

from typing import Any, Callable


class FunctionRegistry:
    """Extensible registry for config functions.

    Register a new function with the ``@FunctionRegistry.register`` decorator::

        @FunctionRegistry.register("MY_FUNC")
        def my_func(*args):
            ...
    """

    _functions: dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str):
        """Decorator that registers *func* under *name*."""

        def decorator(func: Callable) -> Callable:
            cls._functions[name] = func
            return func

        return decorator

    @classmethod
    def call(cls, name: str, args: list[Any]) -> Any:
        if name not in cls._functions:
            raise ValueError(f"Unknown function: {name}")
        return cls._functions[name](*args)

    @classmethod
    def has(cls, name: str) -> bool:
        return name in cls._functions
