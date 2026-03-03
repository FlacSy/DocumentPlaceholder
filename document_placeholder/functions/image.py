"""Функции для вставки изображений в документ."""

from __future__ import annotations

from document_placeholder.functions import FunctionRegistry
from document_placeholder.image_value import ImageValue

_reg = FunctionRegistry.register


@_reg("IMAGE")
def image(
    source: str,
    width_cm: float | None = None,
    height_cm: float | None = None,
) -> ImageValue:
    """Вставить изображение по URL или пути к файлу.

    source: URL (https://...) или путь к файлу (.png, .jpg, ...)
    width_cm, height_cm: размер в см (опционально). Если не заданы — 5 см по ширине.
    """
    w = float(width_cm) if width_cm is not None else 5.0
    h = float(height_cm) if height_cm is not None else None
    return ImageValue(source=source, width_cm=w, height_cm=h)
