# Mapping OpenAlgo API Request https://openalgo.in/docs
# tastytrade margin API https://developer.tastytrade.com

from database.token_db import get_br_symbol
from utils.logging import get_logger

logger = get_logger(__name__)


def transform_margin_positions(positions: list) -> list:
    """
    Transform OpenAlgo margin position format for tastytrade.

    Note: tastytrade does not provide a position-by-position basket margin
    calculator API. This function formats positions for internal logging only.
    The actual margin calculation raises NotImplementedError via margin_api.py.

    Args:
        positions: List of positions in OpenAlgo format

    Returns:
        List of formatted position dicts (for logging/debugging only)
    """
    transformed_positions = []
    skipped_positions = []

    for position in positions:
        try:
            symbol = position["symbol"]
            exchange = position["exchange"]

            br_symbol = get_br_symbol(symbol, exchange)

            if not br_symbol or str(br_symbol).lower() == "none":
                logger.warning(f"Symbol not found for: {symbol} on exchange: {exchange}")
                skipped_positions.append(f"{symbol} ({exchange})")
                continue

            br_symbol_str = str(br_symbol).strip()
            if not br_symbol_str:
                logger.warning(f"Invalid symbol format for {symbol} ({exchange})")
                skipped_positions.append(f"{symbol} ({exchange})")
                continue

            transformed_position = {
                "symbol": br_symbol_str,
                "exchange": exchange,
                "action": position["action"].upper(),
                "quantity": int(position["quantity"]),
                "price": float(position.get("price", 0)),
            }

            transformed_positions.append(transformed_position)

        except Exception as e:
            logger.error(f"Error transforming position: {position}, Error: {e}")
            skipped_positions.append(f"{position.get('symbol', 'unknown')}")
            continue

    if skipped_positions:
        logger.warning(f"Skipped {len(skipped_positions)} position(s): {', '.join(skipped_positions)}")

    return transformed_positions


def parse_margin_response(response_data: dict) -> dict:
    """
    tastytrade does not provide a basket margin calculator API endpoint.

    Account-level margin information is available via:
      GET /margin/accounts/{account-number}/requirements

    But this returns aggregate account margin, not per-position/basket margin.

    Returns:
        dict: Error response indicating the feature is not supported
    """
    logger.warning("tastytrade does not support per-position basket margin calculation")
    return {
        "status": "error",
        "message": "tastytrade does not provide a position-specific margin calculator API. "
                   "Use the Funds page to view account-level margin requirements.",
    }
