"""Interface with the :mod:`olmOCR2` package."""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Callable, Optional


class OCRClientError(RuntimeError):
    """Exception raised when the OCR backend cannot be used."""


@dataclass
class OCRClient:
    """Thin wrapper around the ``olmOCR2`` library.

    The real ``olmOCR2`` package is not bundled with this project.  Instead, we
    attempt to import it dynamically and look for a handful of common entry
    points.  If the package is not available or does not expose a supported
    function, a helpful :class:`OCRClientError` is raised so the GUI can present
    a friendly error message to the user.
    """

    _callable: Optional[Callable[[str], str]] = None

    def __post_init__(self) -> None:
        if self._callable is None:
            self._callable = self._discover_backend()

    def _discover_backend(self) -> Callable[[str], str]:
        """Return a callable that performs OCR using ``olmOCR2``.

        The actual API surface of ``olmOCR2`` varies between versions, so we try
        a few common attribute names.  The callable must accept a path to an
        image on disk and return the recognised text as a string.
        """

        try:
            module = importlib.import_module("olmOCR2")
        except ModuleNotFoundError as exc:  # pragma: no cover - requires package
            raise OCRClientError(
                "The 'olmOCR2' package is required to perform OCR. "
                "Install it with 'pip install olmOCR2'."
            ) from exc

        candidate_names = (
            "ocr_image",
            "extract_text",
            "ocr",
            "read",
            "recognize",
        )

        for name in candidate_names:
            attr = getattr(module, name, None)
            if callable(attr):
                return attr  # type: ignore[return-value]

        # Some versions expose a class-based API.  Try to instantiate common
        # class names that provide an ``ocr``/``recognize`` method.
        class_candidates = (
            "OCR",
            "OlmOCR",
            "Reader",
            "Client",
        )

        for cls_name in class_candidates:
            cls = getattr(module, cls_name, None)
            if cls is None:
                continue
            instance = cls()
            for method_name in ("ocr", "ocr_image", "extract_text", "recognize"):
                method = getattr(instance, method_name, None)
                if callable(method):
                    return method  # type: ignore[return-value]

        raise OCRClientError(
            "Could not find a supported OCR entry point in 'olmOCR2'. "
            "Ensure you are using a compatible version."
        )

    def extract_text(self, image_path: str) -> str:
        """Return the text recognised from ``image_path``.

        Parameters
        ----------
        image_path:
            Path to an image that should be passed to the OCR backend.
        """

        if self._callable is None:  # pragma: no cover - defensive
            self._callable = self._discover_backend()

        return self._callable(image_path)


__all__ = ["OCRClient", "OCRClientError"]
