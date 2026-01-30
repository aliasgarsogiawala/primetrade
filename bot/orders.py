from .client import BinanceClient, BinanceAPIError
from .validators import validate_order_params, ValidationError
from .logging_config import get_logger


class OrderManager:
    """
    Handles order placement and management.
    
    Provides a clean interface for placing and tracking orders.
    """
    
    def __init__(self, client):
        """
        Initialize OrderManager.
        
        Args:
            client: BinanceClient instance
        """
        self.client = client
        self.logger = get_logger('orders')
    
    def place_order(self, symbol, side, order_type, quantity, price=None):
        """
        Place a new order with validation.
        
        Args:
            symbol: Trading pair
            side: BUY or SELL
            order_type: MARKET or LIMIT
            quantity: Order quantity
            price: Limit price (for LIMIT orders)
        
        Returns:
            dict with order result and formatted response
        """
        try:
            validated = validate_order_params(symbol, side, order_type, quantity, price)
        except ValidationError as e:
            self.logger.error(f"Validation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'VALIDATION_ERROR'
            }
        
        self.logger.info(f"Order request: {validated}")
        
        try:
            response = self.client.place_order(
                symbol=validated['symbol'],
                side=validated['side'],
                order_type=validated['order_type'],
                quantity=validated['quantity'],
                price=validated['price']
            )
            
            result = self._format_order_response(response)
            result['success'] = True
            
            self.logger.info(f"Order placed successfully: {result['order_id']}")
            
            return result
            
        except BinanceAPIError as e:
            self.logger.error(f"Order failed: {e}")
            return {
                'success': False,
                'error': e.message,
                'error_code': e.error_code,
                'error_type': 'API_ERROR'
            }
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': 'UNKNOWN_ERROR'
            }
    
    def _format_order_response(self, response):
        """Format API response into clean output."""
        return {
            'order_id': response.get('orderId'),
            'symbol': response.get('symbol'),
            'side': response.get('side'),
            'type': response.get('type'),
            'status': response.get('status'),
            'quantity': response.get('origQty'),
            'executed_qty': response.get('executedQty'),
            'price': response.get('price'),
            'avg_price': response.get('avgPrice'),
            'time_in_force': response.get('timeInForce'),
            'reduce_only': response.get('reduceOnly'),
            'timestamp': response.get('updateTime'),
            'raw_response': response
        }
    
    def get_order_summary(self, order_result):
        """Generate human-readable order summary."""
        if not order_result.get('success'):
            return f"Order Failed: {order_result.get('error')}"
        
        lines = [
            "=" * 50,
            "ORDER EXECUTED SUCCESSFULLY",
            "=" * 50,
            f"Order ID:     {order_result.get('order_id')}",
            f"Symbol:       {order_result.get('symbol')}",
            f"Side:         {order_result.get('side')}",
            f"Type:         {order_result.get('type')}",
            f"Status:       {order_result.get('status')}",
            f"Quantity:     {order_result.get('quantity')}",
            f"Executed:     {order_result.get('executed_qty')}",
        ]
        
        if order_result.get('price') and order_result.get('price') != '0':
            lines.append(f"Price:        {order_result.get('price')}")
        
        if order_result.get('avg_price') and order_result.get('avg_price') != '0':
            lines.append(f"Avg Price:    {order_result.get('avg_price')}")
        
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def cancel_order(self, symbol, order_id):
        """Cancel an existing order."""
        try:
            response = self.client.cancel_order(symbol, order_id)
            self.logger.info(f"Order {order_id} cancelled")
            return {'success': True, 'response': response}
        except BinanceAPIError as e:
            self.logger.error(f"Cancel failed: {e}")
            return {'success': False, 'error': e.message}
    
    def get_open_orders(self, symbol=None):
        """Get list of open orders."""
        try:
            orders = self.client.get_open_orders(symbol)
            return {'success': True, 'orders': orders}
        except BinanceAPIError as e:
            self.logger.error(f"Failed to get open orders: {e}")
            return {'success': False, 'error': e.message}
