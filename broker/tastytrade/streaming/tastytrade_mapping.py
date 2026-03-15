"""
tastytrade-specific exchange and capability mappings for WebSocket streaming.

tastytrade is a US broker. Instruments are categorized by asset class, not
by exchange segment the way Indian brokers work. The "exchange" field in
OpenAlgo maps to tastytrade instrument types for routing purposes.
"""


class tastytradeExchangeMapper:
    """Maps exchange/segment codes between OpenAlgo and tastytrade formats."""

    # OpenAlgo exchange code → tastytrade instrument type
    EXCHANGE_MAP = {
        "EQUITY": "Equity",
        "OPTIONS": "Equity Option",
        "OPTION": "Equity Option",
        "EQUITY_OPTION": "Equity Option",
        "FUTURES": "Future",
        "FUTURE": "Future",
        "FUTURES_OPTION": "Future Option",
        "FUTURE_OPTION": "Future Option",
        "CRYPTO": "Cryptocurrency",
        "CRYPTOCURRENCY": "Cryptocurrency",
    }

    # Numeric IDs used internally for subscription routing
    # Aligned with tastytrade's instrument categories
    EXCHANGE_SEGMENTS = {
        1: "EQUITY",
        2: "OPTIONS",
        3: "FUTURES",
        4: "FUTURES_OPTION",
        5: "CRYPTO",
    }

    SEGMENT_TO_ID = {v: k for k, v in EXCHANGE_SEGMENTS.items()}

    @classmethod
    def get_instrument_type(cls, exchange_code: str) -> str:
        """
        Get tastytrade instrument type from OpenAlgo exchange code.

        Args:
            exchange_code: OpenAlgo exchange code (e.g. 'EQUITY', 'OPTIONS')

        Returns:
            str: tastytrade instrument type (e.g. 'Equity', 'Future')
        """
        return cls.EXCHANGE_MAP.get(exchange_code.upper(), "Equity")

    @classmethod
    def get_exchange_segment(cls, exchange_code: str) -> int:
        """
        Get numeric segment ID from exchange code.

        Args:
            exchange_code: OpenAlgo exchange code

        Returns:
            int: Segment ID (defaults to 1 = EQUITY)
        """
        return cls.SEGMENT_TO_ID.get(exchange_code.upper(), 1)

    @classmethod
    def get_exchange_from_segment(cls, segment_id: int) -> str:
        """
        Get exchange code from segment ID.

        Args:
            segment_id: Numeric segment ID

        Returns:
            str: OpenAlgo exchange code
        """
        return cls.EXCHANGE_SEGMENTS.get(segment_id, "EQUITY")


class tastytradeCapabilityRegistry:
    """Registry for tastytrade-specific streaming capabilities."""

    # tastytrade supports up to 5 levels of market depth for all segments
    DEPTH_CAPABILITIES = {
        "EQUITY": {"supported_levels": [5], "default_level": 5, "max_level": 5},
        "OPTIONS": {"supported_levels": [5], "default_level": 5, "max_level": 5},
        "FUTURES": {"supported_levels": [5], "default_level": 5, "max_level": 5},
        "FUTURES_OPTION": {"supported_levels": [5], "default_level": 5, "max_level": 5},
        "CRYPTO": {"supported_levels": [5], "default_level": 5, "max_level": 5},
    }

    MODE_CAPABILITIES = {
        "LTP": 1,    # Last Traded Price only
        "QUOTE": 2,  # Full quote with OHLC
        "DEPTH": 3,  # Market depth (5 levels)
    }

    @classmethod
    def is_depth_level_supported(cls, exchange: str, depth_level: int) -> bool:
        exchange = exchange.upper()
        if exchange not in cls.DEPTH_CAPABILITIES:
            return False
        return depth_level in cls.DEPTH_CAPABILITIES[exchange]["supported_levels"]

    @classmethod
    def get_fallback_depth_level(cls, exchange: str, requested_level: int) -> int:
        exchange = exchange.upper()
        if exchange not in cls.DEPTH_CAPABILITIES:
            return 5
        capabilities = cls.DEPTH_CAPABILITIES[exchange]
        if requested_level in capabilities["supported_levels"]:
            return requested_level
        return capabilities["default_level"]

    @classmethod
    def get_max_depth_level(cls, exchange: str) -> int:
        exchange = exchange.upper()
        if exchange not in cls.DEPTH_CAPABILITIES:
            return 5
        return cls.DEPTH_CAPABILITIES[exchange]["max_level"]

    @classmethod
    def is_mode_supported(cls, mode_name: str) -> bool:
        return mode_name.upper() in cls.MODE_CAPABILITIES

    @classmethod
    def get_mode_value(cls, mode_name: str) -> int:
        return cls.MODE_CAPABILITIES.get(mode_name.upper())
