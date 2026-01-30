from decimal import Decimal, InvalidOperation

VALID_SYMBOLS = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'DOGEUSDT',
    'ADAUSDT', 'SOLUSDT', 'DOTUSDT', 'MATICUSDT', 'LTCUSDT'
]

VALID_SIDES = ['BUY', 'SELL']
VALID_ORDER_TYPES = ['MARKET', 'LIMIT']


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_symbol(symbol):
    """Validate trading symbol."""
    if not symbol:
        raise ValidationError("Symbol is required")
    
    symbol = symbol.upper().strip()
    
    if not symbol.endswith('USDT'):
        raise ValidationError(f"Invalid symbol format: {symbol}. Must end with USDT")
    
    return symbol


def validate_side(side):
    """Validate order side."""
    if not side:
        raise ValidationError("Side is required")
    
    side = side.upper().strip()
    
    if side not in VALID_SIDES:
        raise ValidationError(f"Invalid side: {side}. Must be BUY or SELL")
    
    return side


def validate_order_type(order_type):
    """Validate order type."""
    if not order_type:
        raise ValidationError("Order type is required")
    
    order_type = order_type.upper().strip()
    
    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(f"Invalid order type: {order_type}. Must be MARKET or LIMIT")
    
    return order_type


def validate_quantity(quantity):
    """Validate order quantity."""
    if quantity is None:
        raise ValidationError("Quantity is required")
    
    try:
        qty = Decimal(str(quantity))
    except (InvalidOperation, ValueError):
        raise ValidationError(f"Invalid quantity: {quantity}")
    
    if qty <= 0:
        raise ValidationError("Quantity must be greater than 0")
    
    return float(qty)


def validate_price(price, order_type):
    """Validate price for limit orders."""
    if order_type == 'LIMIT':
        if price is None:
            raise ValidationError("Price is required for LIMIT orders")
        
        try:
            p = Decimal(str(price))
        except (InvalidOperation, ValueError):
            raise ValidationError(f"Invalid price: {price}")
        
        if p <= 0:
            raise ValidationError("Price must be greater than 0")
        
        return float(p)
    
    return None


def validate_order_params(symbol, side, order_type, quantity, price=None):
    """
    Validate all order parameters.
    
    Returns a dict with validated parameters.
    """
    validated = {
        'symbol': validate_symbol(symbol),
        'side': validate_side(side),
        'order_type': validate_order_type(order_type),
        'quantity': validate_quantity(quantity),
    }
    
    validated['price'] = validate_price(price, validated['order_type'])
    
    return validated
