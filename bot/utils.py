"""Utility functions for the trading bot."""

from datetime import datetime


def format_timestamp(timestamp_ms):
    """Convert millisecond timestamp to readable format."""
    if not timestamp_ms:
        return None
    dt = datetime.fromtimestamp(timestamp_ms / 1000)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def format_price(price, decimals=2):
    """Format price with specified decimal places."""
    if price is None:
        return None
    try:
        return f"{float(price):,.{decimals}f}"
    except (ValueError, TypeError):
        return str(price)


def format_quantity(quantity, decimals=8):
    """Format quantity with specified decimal places."""
    if quantity is None:
        return None
    try:
        return f"{float(quantity):.{decimals}f}".rstrip('0').rstrip('.')
    except (ValueError, TypeError):
        return str(quantity)
