"""Значение-изображение для вставки в документ."""

from __future__ import annotations


class ImageValue:
    """Дескриптор изображения: URL или путь к файлу. Processor вставит картинку."""

    __slots__ = ("source", "width_cm", "height_cm")

    def __init__(
        self,
        source: str,
        width_cm: float | None = None,
        height_cm: float | None = None,
    ) -> None:
        self.source = source.strip()
        self.width_cm = width_cm
        self.height_cm = height_cm
