import hashlib
import hmac
import time
import requests
from urllib.parse import urlencode

from .logging_config import get_logger


class BinanceAPIError(Exception):
    """Exception for Binance API errors."""
    def __init__(self, status_code, error_code, message):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        super().__init__(f"API Error {error_code}: {message}")


class BinanceClient:
    """
    Binance Futures Testnet API client.
    
    Handles authentication, request signing, and API communication.
    """
    
    BASE_URL = "https://testnet.binancefuture.com"
    
    def __init__(self, api_key, api_secret):
        if not api_key or not api_secret:
            raise ValueError("API key and secret are required")
        
        self.api_key = api_key
        self.api_secret = api_secret
        self.logger = get_logger('client')
        
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': self.api_key,
            'Content-Type': 'application/x-www-form-urlencoded'
        })
    
    def _generate_signature(self, params):
        """Generate HMAC SHA256 signature for request."""
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _get_timestamp(self):
        """Get current timestamp in milliseconds."""
        return int(time.time() * 1000)
    
    def _make_request(self, method, endpoint, params=None, signed=False):
        """
        Make HTTP request to Binance API.
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint
            params: Request parameters
            signed: Whether request needs signature
        
        Returns:
            Response JSON data
        """
        url = f"{self.BASE_URL}{endpoint}"
        params = params or {}
        
        if signed:
            params['timestamp'] = self._get_timestamp()
            params['signature'] = self._generate_signature(params)
        
        self.logger.debug(f"Request: {method} {endpoint}")
        self.logger.debug(f"Params: {self._sanitize_params(params)}")
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=params, timeout=30)
            elif method == 'POST':
                response = self.session.post(url, data=params, timeout=30)
            elif method == 'DELETE':
                response = self.session.delete(url, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            self.logger.debug(f"Response status: {response.status_code}")
            
            try:
                data = response.json()
            except ValueError as e:
                self.logger.error(f"Invalid JSON response: {e}")
                raise BinanceAPIError(response.status_code, 'INVALID_JSON', 'Invalid JSON response from server')
            
            if response.status_code != 200:
                error_code = data.get('code', 'UNKNOWN')
                error_msg = data.get('msg', 'Unknown error')
                self.logger.error(f"API error: {error_code} - {error_msg}")
                raise BinanceAPIError(response.status_code, error_code, error_msg)
            
            self.logger.debug(f"Response data: {data}")
            return data
            
        except requests.exceptions.Timeout:
            self.logger.error("Request timeout")
            raise BinanceAPIError(0, 'TIMEOUT', 'Request timed out')
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise BinanceAPIError(0, 'CONNECTION_ERROR', str(e))
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise BinanceAPIError(0, 'REQUEST_ERROR', str(e))
    
    def _sanitize_params(self, params):
        """Remove sensitive data from params for logging."""
        sanitized = params.copy()
        if 'signature' in sanitized:
            sanitized['signature'] = '***'
        return sanitized
    
    def get_server_time(self):
        """Get Binance server time."""
        return self._make_request('GET', '/fapi/v1/time')
    
    def get_exchange_info(self):
        """Get exchange trading rules and symbol info."""
        return self._make_request('GET', '/fapi/v1/exchangeInfo')
    
    def get_account_info(self):
        """Get current account information."""
        return self._make_request('GET', '/fapi/v2/account', signed=True)
    
    def get_symbol_price(self, symbol):
        """Get current price for a symbol."""
        params = {'symbol': symbol}
        return self._make_request('GET', '/fapi/v1/ticker/price', params=params)
    
    def place_order(self, symbol, side, order_type, quantity, price=None, 
                    time_in_force=None, reduce_only=False):
        """
        Place a new order.
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: BUY or SELL
            order_type: MARKET or LIMIT
            quantity: Order quantity
            price: Limit price (required for LIMIT orders)
            time_in_force: GTC, IOC, or FOK (default GTC for LIMIT)
            reduce_only: Whether to reduce position only
        
        Returns:
            Order response from API
        """
        params = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity,
        }
        
        if order_type == 'LIMIT':
            if price is None:
                raise ValueError("Price required for LIMIT orders")
            params['price'] = price
            params['timeInForce'] = time_in_force or 'GTC'
        
        if reduce_only:
            params['reduceOnly'] = 'true'
        
        self.logger.info(f"Placing {order_type} {side} order for {quantity} {symbol}")
        
        return self._make_request('POST', '/fapi/v1/order', params=params, signed=True)
    
    def cancel_order(self, symbol, order_id):
        """Cancel an existing order."""
        params = {
            'symbol': symbol,
            'orderId': order_id
        }
        return self._make_request('DELETE', '/fapi/v1/order', params=params, signed=True)
    
    def get_open_orders(self, symbol=None):
        """Get all open orders."""
        params = {}
        if symbol:
            params['symbol'] = symbol
        return self._make_request('GET', '/fapi/v1/openOrders', params=params, signed=True)
    
    def test_connectivity(self):
        """Test API connectivity."""
        try:
            self.get_server_time()
            return True
        except Exception:
            return False
