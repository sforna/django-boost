"""
Views for Django Boost.

Currently only the browser-logs endpoint.
"""

import json
import logging

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .config import get_config

logger = logging.getLogger("browser")


@csrf_exempt
def browser_logs(request: HttpRequest) -> JsonResponse:
    """Receive browser console logs via POST.

    Handles both application/json and text/plain (sendBeacon) content types.
    """
    logs_data = request.POST.get("logs", [])

    if not logs_data and request.content_type != "application/json":
        try:
            decoded = json.loads(request.body.decode("utf-8"))
            logs_data = decoded.get("logs", [])
        except (json.JSONDecodeError, UnicodeDecodeError):
            logs_data = []

    if not logs_data:
        return JsonResponse({"status": "no logs"})

    enabled_levels = get_config("browser_log_levels", ["error", "warning", "info", "debug"])

    for entry in logs_data:
        level = entry.get("type", "debug")
        if level not in enabled_levels:
            continue

        message = _build_log_message(entry.get("data", []))
        logger.log(
            _map_level(level),
            message,
            extra={
                "url": entry.get("url", ""),
                "user_agent": entry.get("userAgent", ""),
                "timestamp": entry.get("timestamp", ""),
            },
        )

    return JsonResponse({"status": "logged"})


def _build_log_message(data: list) -> str:
    """Recursively build a string message from log data entries."""
    messages = []
    for value in data:
        if isinstance(value, list):
            messages.append(_build_log_message(value))
        elif isinstance(value, dict):
            messages.append(json.dumps(value))
        elif value is None:
            messages.append("null")
        elif isinstance(value, bool):
            messages.append("true" if value else "false")
        else:
            messages.append(str(value))
    return " ".join(messages)


def _map_level(level: str) -> int:
    """Map browser log types to Python logging levels."""
    mapping = {
        "error": logging.ERROR,
        "warn": logging.WARNING,
        "window_error": logging.ERROR,
        "uncaught_error": logging.ERROR,
        "unhandled_rejection": logging.ERROR,
        "info": logging.INFO,
        "debug": logging.DEBUG,
        "log": logging.DEBUG,
        "table": logging.DEBUG,
    }
    return mapping.get(level, logging.DEBUG)
