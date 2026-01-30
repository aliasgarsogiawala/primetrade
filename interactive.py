#!/usr/bin/env python3
"""
Interactive CLI for Binance Futures Trading Bot

Provides a menu-driven interface for placing orders.
"""

import os
import sys
from dotenv import load_dotenv

from bot.logging_config import setup_logging, get_logger
from bot.client import BinanceClient
from bot.orders import OrderManager


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


def colored(text, color):
    """Wrap text with color codes."""
    return f"{color}{text}{Colors.RESET}"


def print_banner():
    """Print welcome banner."""
    banner = """
    ╔══════════════════════════════════════════════════════╗
    ║                                                      ║
    ║   ██████╗ ██╗███╗   ██╗ █████╗ ███╗   ██╗ ██████╗   ║
    ║   ██╔══██╗██║████╗  ██║██╔══██╗████╗  ██║██╔════╝   ║
    ║   ██████╔╝██║██╔██╗ ██║███████║██╔██╗ ██║██║        ║
    ║   ██╔══██╗██║██║╚██╗██║██╔══██║██║╚██╗██║██║        ║
    ║   ██████╔╝██║██║ ╚████║██║  ██║██║ ╚████║╚██████╗   ║
    ║   ╚═════╝ ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝   ║
    ║                                                      ║
    ║         Futures Testnet Trading Bot                  ║
    ║                                                      ║
    ╚══════════════════════════════════════════════════════╝
    """
    print(colored(banner, Colors.CYAN))


def print_menu():
    """Print main menu."""
    print("\n" + colored("═" * 50, Colors.BLUE))
    print(colored("  MAIN MENU", Colors.BOLD))
    print(colored("═" * 50, Colors.BLUE))
    print(f"  {colored('[1]', Colors.GREEN)} Place Market Order")
    print(f"  {colored('[2]', Colors.GREEN)} Place Limit Order")
    print(f"  {colored('[3]', Colors.GREEN)} View Open Orders")
    print(f"  {colored('[4]', Colors.GREEN)} Check Account Balance")
    print(f"  {colored('[5]', Colors.GREEN)} Get Current Price")
    print(f"  {colored('[0]', Colors.RED)} Exit")
    print(colored("═" * 50, Colors.BLUE))


def get_input(prompt, validator=None, error_msg="Invalid input"):
    """Get validated input from user."""
    while True:
        try:
            value = input(colored(f"  {prompt}: ", Colors.YELLOW)).strip()
            
            if not value:
                print(colored(f"  ✗ Input cannot be empty", Colors.RED))
                continue
            
            if validator:
                value = validator(value)
            
            return value
            
        except ValueError as e:
            print(colored(f"  ✗ {error_msg}: {e}", Colors.RED))
        except KeyboardInterrupt:
            print("\n")
            return None


def validate_symbol(value):
    """Validate trading symbol."""
    value = value.upper().strip()
    if not value.endswith('USDT'):
        raise ValueError("Symbol must end with USDT (e.g., BTCUSDT)")
    return value


def validate_side(value):
    """Validate order side."""
    value = value.upper().strip()
    if value not in ['BUY', 'SELL', 'B', 'S']:
        raise ValueError("Must be BUY/B or SELL/S")
    return 'BUY' if value in ['BUY', 'B'] else 'SELL'


def validate_quantity(value):
    """Validate quantity."""
    qty = float(value)
    if qty <= 0:
        raise ValueError("Quantity must be positive")
    return qty


def validate_price(value):
    """Validate price."""
    price = float(value)
    if price <= 0:
        raise ValueError("Price must be positive")
    return price


def confirm_order(symbol, side, order_type, quantity, price=None):
    """Show order confirmation prompt."""
    print("\n" + colored("  ┌─────────────────────────────────────┐", Colors.YELLOW))
    print(colored("  │       ORDER CONFIRMATION            │", Colors.YELLOW))
    print(colored("  ├─────────────────────────────────────┤", Colors.YELLOW))
    print(colored(f"  │  Symbol:    {symbol:<22} │", Colors.YELLOW))
    print(colored(f"  │  Side:      {side:<22} │", Colors.YELLOW))
    print(colored(f"  │  Type:      {order_type:<22} │", Colors.YELLOW))
    print(colored(f"  │  Quantity:  {quantity:<22} │", Colors.YELLOW))
    if price:
        print(colored(f"  │  Price:     {price:<22} │", Colors.YELLOW))
    print(colored("  └─────────────────────────────────────┘", Colors.YELLOW))
    
    confirm = input(colored("\n  Confirm order? (y/n): ", Colors.BOLD)).strip().lower()
    return confirm in ['y', 'yes']


def print_result(result, order_manager):
    """Print order result with formatting."""
    if result.get('success'):
        print("\n" + colored("  ✓ ORDER PLACED SUCCESSFULLY!", Colors.GREEN))
        print(colored("  ┌─────────────────────────────────────┐", Colors.GREEN))
        print(colored(f"  │  Order ID:  {result.get('order_id'):<22} │", Colors.GREEN))
        print(colored(f"  │  Status:    {result.get('status'):<22} │", Colors.GREEN))
        print(colored(f"  │  Symbol:    {result.get('symbol'):<22} │", Colors.GREEN))
        print(colored(f"  │  Side:      {result.get('side'):<22} │", Colors.GREEN))
        print(colored(f"  │  Type:      {result.get('type'):<22} │", Colors.GREEN))
        print(colored(f"  │  Quantity:  {result.get('quantity'):<22} │", Colors.GREEN))
        if result.get('price') and result.get('price') != '0':
            print(colored(f"  │  Price:     {result.get('price'):<22} │", Colors.GREEN))
        if result.get('avg_price') and result.get('avg_price') != '0.00':
            print(colored(f"  │  Avg Price: {result.get('avg_price'):<22} │", Colors.GREEN))
        print(colored("  └─────────────────────────────────────┘", Colors.GREEN))
    else:
        print("\n" + colored("  ✗ ORDER FAILED!", Colors.RED))
        print(colored("  ┌─────────────────────────────────────┐", Colors.RED))
        if result.get('error_code'):
            print(colored(f"  │  Error Code: {result.get('error_code'):<21} │", Colors.RED))
        print(colored(f"  │  {result.get('error')[:35]:<35} │", Colors.RED))
        print(colored("  └─────────────────────────────────────┘", Colors.RED))


def place_market_order(order_manager):
    """Interactive market order placement."""
    print("\n" + colored("  ── MARKET ORDER ──", Colors.BOLD))
    print(colored("  (Executes immediately at current market price)\n", Colors.CYAN))
    
    symbol = get_input("Enter symbol (e.g., BTCUSDT)", validate_symbol, "Invalid symbol")
    if not symbol:
        return
    
    print(colored("\n  Side: [B]uy or [S]ell", Colors.CYAN))
    side = get_input("Enter side", validate_side, "Invalid side")
    if not side:
        return
    
    print(colored("\n  Note: Minimum order value is $100", Colors.CYAN))
    quantity = get_input("Enter quantity", validate_quantity, "Invalid quantity")
    if not quantity:
        return
    
    if not confirm_order(symbol, side, 'MARKET', quantity):
        print(colored("\n  Order cancelled.", Colors.YELLOW))
        return
    
    print(colored("\n  Placing order...", Colors.CYAN))
    result = order_manager.place_order(symbol, side, 'MARKET', quantity)
    print_result(result, order_manager)


def place_limit_order(order_manager):
    """Interactive limit order placement."""
    print("\n" + colored("  ── LIMIT ORDER ──", Colors.BOLD))
    print(colored("  (Executes when price reaches your specified level)\n", Colors.CYAN))
    
    symbol = get_input("Enter symbol (e.g., BTCUSDT)", validate_symbol, "Invalid symbol")
    if not symbol:
        return
    
    print(colored("\n  Side: [B]uy or [S]ell", Colors.CYAN))
    side = get_input("Enter side", validate_side, "Invalid side")
    if not side:
        return
    
    print(colored("\n  Note: Minimum order value is $100", Colors.CYAN))
    quantity = get_input("Enter quantity", validate_quantity, "Invalid quantity")
    if not quantity:
        return
    
    if side == 'BUY':
        print(colored("\n  Tip: BUY LIMIT price should be BELOW current market price", Colors.CYAN))
    else:
        print(colored("\n  Tip: SELL LIMIT price should be ABOVE current market price", Colors.CYAN))
    
    price = get_input("Enter limit price", validate_price, "Invalid price")
    if not price:
        return
    
    if not confirm_order(symbol, side, 'LIMIT', quantity, price):
        print(colored("\n  Order cancelled.", Colors.YELLOW))
        return
    
    print(colored("\n  Placing order...", Colors.CYAN))
    result = order_manager.place_order(symbol, side, 'LIMIT', quantity, price)
    print_result(result, order_manager)


def view_open_orders(order_manager):
    """View all open orders."""
    print("\n" + colored("  ── OPEN ORDERS ──", Colors.BOLD))
    
    symbol = input(colored("  Enter symbol (or press Enter for all): ", Colors.YELLOW)).strip()
    symbol = symbol.upper() if symbol else None
    
    print(colored("\n  Fetching orders...", Colors.CYAN))
    result = order_manager.get_open_orders(symbol)
    
    if not result.get('success'):
        print(colored(f"\n  ✗ Error: {result.get('error')}", Colors.RED))
        return
    
    orders = result.get('orders', [])
    
    if not orders:
        print(colored("\n  No open orders found.", Colors.YELLOW))
        return
    
    print(colored(f"\n  Found {len(orders)} open order(s):\n", Colors.GREEN))
    
    for i, order in enumerate(orders, 1):
        print(colored(f"  ┌─── Order {i} ───────────────────────────┐", Colors.BLUE))
        print(colored(f"  │  ID:       {order.get('orderId'):<24} │", Colors.BLUE))
        print(colored(f"  │  Symbol:   {order.get('symbol'):<24} │", Colors.BLUE))
        print(colored(f"  │  Side:     {order.get('side'):<24} │", Colors.BLUE))
        print(colored(f"  │  Type:     {order.get('type'):<24} │", Colors.BLUE))
        print(colored(f"  │  Price:    {order.get('price'):<24} │", Colors.BLUE))
        print(colored(f"  │  Quantity: {order.get('origQty'):<24} │", Colors.BLUE))
        print(colored(f"  │  Status:   {order.get('status'):<24} │", Colors.BLUE))
        print(colored(f"  └─────────────────────────────────────────┘", Colors.BLUE))


def check_balance(client):
    """Check account balance."""
    print("\n" + colored("  ── ACCOUNT BALANCE ──", Colors.BOLD))
    print(colored("\n  Fetching account info...", Colors.CYAN))
    
    try:
        account = client.get_account_info()
        
        print(colored("\n  ┌─────────────────────────────────────┐", Colors.GREEN))
        print(colored("  │         ACCOUNT SUMMARY             │", Colors.GREEN))
        print(colored("  ├─────────────────────────────────────┤", Colors.GREEN))
        
        total_balance = float(account.get('totalWalletBalance', 0))
        available = float(account.get('availableBalance', 0))
        unrealized_pnl = float(account.get('totalUnrealizedProfit', 0))
        
        print(colored(f"  │  Total Balance:    ${total_balance:>14,.2f} │", Colors.GREEN))
        print(colored(f"  │  Available:        ${available:>14,.2f} │", Colors.GREEN))
        
        pnl_color = Colors.GREEN if unrealized_pnl >= 0 else Colors.RED
        pnl_str = f"${unrealized_pnl:>14,.2f}"
        print(f"  │  Unrealized PnL:   {colored(pnl_str, pnl_color)} │")
        
        print(colored("  └─────────────────────────────────────┘", Colors.GREEN))
        
    except Exception as e:
        print(colored(f"\n  ✗ Error fetching balance: {e}", Colors.RED))


def get_price(client):
    """Get current price for a symbol."""
    print("\n" + colored("  ── CURRENT PRICE ──", Colors.BOLD))
    
    symbol = get_input("Enter symbol (e.g., BTCUSDT)", validate_symbol, "Invalid symbol")
    if not symbol:
        return
    
    print(colored("\n  Fetching price...", Colors.CYAN))
    
    try:
        data = client.get_symbol_price(symbol)
        price = float(data.get('price', 0))
        
        print(colored(f"\n  ┌─────────────────────────────────────┐", Colors.GREEN))
        print(colored(f"  │  {symbol:<12} ${price:>18,.2f}   │", Colors.GREEN))
        print(colored(f"  └─────────────────────────────────────┘", Colors.GREEN))
        
    except Exception as e:
        print(colored(f"\n  ✗ Error fetching price: {e}", Colors.RED))


def load_config():
    """Load API credentials."""
    load_dotenv()
    
    api_key = os.getenv('BINANCE_TESTNET_API_KEY')
    api_secret = os.getenv('BINANCE_TESTNET_API_SECRET')
    
    if not api_key or not api_secret:
        print(colored("\n  ✗ Error: Missing API credentials!", Colors.RED))
        print(colored("  Please set BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_API_SECRET", Colors.YELLOW))
        print(colored("  in .env file or environment variables\n", Colors.YELLOW))
        sys.exit(1)
    
    return api_key, api_secret


def main():
    """Main interactive loop."""
    setup_logging()
    logger = get_logger('interactive')
    
    print_banner()
    
    print(colored("  Connecting to Binance Testnet...", Colors.CYAN))
    
    try:
        api_key, api_secret = load_config()
        client = BinanceClient(api_key, api_secret)
        
        if not client.test_connectivity():
            print(colored("  ✗ Could not connect to Binance API", Colors.RED))
            sys.exit(1)
        
        print(colored("  ✓ Connected successfully!", Colors.GREEN))
        logger.info("Interactive CLI started")
        
        order_manager = OrderManager(client)
        
        while True:
            print_menu()
            
            choice = input(colored("  Select option: ", Colors.BOLD)).strip()
            
            if choice == '1':
                place_market_order(order_manager)
            elif choice == '2':
                place_limit_order(order_manager)
            elif choice == '3':
                view_open_orders(order_manager)
            elif choice == '4':
                check_balance(client)
            elif choice == '5':
                get_price(client)
            elif choice == '0':
                print(colored("\n  Goodbye! Happy trading!\n", Colors.CYAN))
                logger.info("Interactive CLI closed")
                break
            else:
                print(colored("\n  ✗ Invalid option. Please try again.", Colors.RED))
            
            input(colored("\n  Press Enter to continue...", Colors.CYAN))
    
    except KeyboardInterrupt:
        print(colored("\n\n  Goodbye!\n", Colors.CYAN))
        sys.exit(0)
    except Exception as e:
        print(colored(f"\n  ✗ Fatal error: {e}", Colors.RED))
        logger.exception("Fatal error in interactive CLI")
        sys.exit(1)


if __name__ == '__main__':
    main()
