"""runtime/factory.py

Factory for creating MockX Gateway instances.

This module provides the main entry point for creating gateway instances
with the appropriate adapter based on the current configuration.
"""

import logging
from typing import Optional

from ..adapters.paper import PaperAdapter
from ..adapters.prod import ProdAdapter
from ..core.errors import ExchangeError
from ..core.facade import MockXGateway

logger = logging.getLogger(__name__)


class ExchangeFactory:
    """Factory for creating MockX Gateway instances.

    This factory class provides a centralized way to create MockX Gateway
    instances with explicit configuration parameters. It encapsulates the
    logic for choosing between paper and production modes, and handles
    the initialization of the correct adapter.

    The factory pattern here serves several purposes:
    1. **Explicit Configuration**: Accepts clear, typed parameters instead of hidden environment variables
    2. **Adapter Selection**: Chooses the correct backend (MockExchange vs CCXT)
    3. **Error Handling**: Provides clear error messages for configuration issues
    4. **Logging**: Tracks gateway creation for debugging and monitoring

    This design ensures that users can create gateways with explicit parameters,
    making the library predictable and easy to test while providing flexibility
    for different use cases.
    """

    @staticmethod
    def create_paper_gateway(
        base_url: str = "http://localhost:8000",
        api_key: str = "dev-key",
        timeout: float = 10.0,
    ) -> MockXGateway:
        """Create a paper mode gateway with explicit configuration.

        Creates a gateway that connects to MockExchange for safe testing and
        development. This is the recommended way to create paper mode gateways
        as it requires explicit configuration parameters.

        Args:
            base_url: MockExchange API base URL
            api_key: API key for authentication with MockExchange
            timeout: Request timeout in seconds

        Returns:
            MockXGateway: Paper mode gateway instance

        Example:
            >>> gateway = MockXFactory.create_paper_gateway(
            ...     base_url="http://localhost:8000",
            ...     api_key="your-api-key"
            ... )
        """
        logger.info(
            "Creating paper mode gateway",
            extra={"base_url": base_url, "timeout": timeout},
        )

        adapter = PaperAdapter(base_url, api_key, timeout)
        gateway = MockXGateway(adapter)

        logger.info(
            "Paper mode gateway created successfully",
            extra={"capabilities": len(gateway.has), "mode": "paper"},
        )

        return gateway

    @staticmethod
    def create_prod_gateway(
        exchange_id: str,
        api_key: Optional[str] = None,
        secret: Optional[str] = None,
        sandbox: bool = False,
        **kwargs,
    ) -> MockXGateway:
        """Create a production mode gateway with explicit configuration.

        Creates a gateway that connects to real exchanges via CCXT for live trading.
        This requires valid API credentials for the specified exchange.

        Args:
            exchange_id: CCXT exchange identifier (e.g., 'binance', 'coinbase', 'kraken')
            api_key: API key for the exchange
            secret: Secret key for the exchange
            sandbox: Use sandbox/testnet if available (recommended for testing)
            **kwargs: Additional CCXT configuration options

        Returns:
            MockXGateway: Production mode gateway instance

        Raises:
            ExchangeError: If exchange configuration is invalid

        Example:
            >>> gateway = ExchangeFactory.create_prod_gateway(
            ...     exchange_id="binance",
            ...     api_key="your-binance-api-key",
            ...     secret="your-binance-secret",
            ...     sandbox=True
            ... )
        """
        logger.info(
            "Creating production mode gateway",
            extra={"exchange_id": exchange_id, "sandbox": sandbox},
        )

        config = {"sandbox": sandbox, **kwargs}

        if api_key:
            config["apiKey"] = api_key
        if secret:
            config["secret"] = secret

        try:
            adapter = ProdAdapter(exchange_id, config)
            gateway = MockXGateway(adapter)

            logger.info(
                "Production mode gateway created successfully",
                extra={
                    "exchange_id": exchange_id,
                    "capabilities": len(gateway.has),
                    "mode": "production",
                },
            )

            return gateway
        except Exception as e:
            logger.error(f"Failed to create production gateway: {str(e)}")
            raise ExchangeError(f"Failed to create {exchange_id} gateway: {str(e)}")
