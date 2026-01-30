#!/usr/bin/env python3
"""
Binance Futures Testnet Trading Bot CLI

Usage:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 50000
"""

import argparse
import os
import sys
from dotenv import load_dotenv

from bot.logging_config import setup_logging, get_logger
from bot.client import BinanceClient, BinanceAPIError
from bot.orders import OrderManager
from bot.validators import ValidationError


def load_config():
    """Load API credentials from environment."""
    load_dotenv()
    
    api_key = os.getenv('BINANCE_TESTNET_API_KEY')
    api_secret = os.getenv('BINANCE_TESTNET_API_SECRET')
    
    if not api_key or not api_secret:
        print("Error: Missing API credentials")
        print("Please set BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_API_SECRET")
        print("in .env file or environment variables")
        sys.exit(1)
    
    return api_key, api_secret


def create_parser():
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description='Binance Futures Testnet Trading Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Market buy order:
    python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
  
  Limit sell order:
    python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 100000
        """
    )
    
    parser.add_argument(
        '--symbol', '-s',
        required=True,
        help='Trading pair (e.g., BTCUSDT)'
    )
    
    parser.add_argument(
        '--side',
        required=True,
        choices=['BUY', 'SELL', 'buy', 'sell'],
        help='Order side: BUY or SELL'
    )
    
    parser.add_argument(
        '--type', '-t',
        required=True,
        choices=['MARKET', 'LIMIT', 'market', 'limit'],
        dest='order_type',
        help='Order type: MARKET or LIMIT'
    )
    
    parser.add_argument(
        '--quantity', '-q',
        required=True,
        type=float,
        help='Order quantity'
    )
    
    parser.add_argument(
        '--price', '-p',
        type=float,
        default=None,
        help='Limit price (required for LIMIT orders)'
    )
    
    return parser


def print_request_summary(args):
    """Print order request summary."""
    print("\n" + "=" * 50)
    print("ORDER REQUEST")
    print("=" * 50)
    print(f"Symbol:       {args.symbol.upper()}")
    print(f"Side:         {args.side.upper()}")
    print(f"Type:         {args.order_type.upper()}")
    print(f"Quantity:     {args.quantity}")
    if args.price:
        print(f"Price:        {args.price}")
    print("=" * 50 + "\n")


def main():
    """Main entry point."""
    setup_logging()
    logger = get_logger('cli')
    
    parser = create_parser()
    args = parser.parse_args()
    
    logger.info("Starting trading bot")
    logger.info(f"Order params: symbol={args.symbol}, side={args.side}, "
                f"type={args.order_type}, qty={args.quantity}, price={args.price}")
    
    print_request_summary(args)
    
    try:
        api_key, api_secret = load_config()
        
        print("Connecting to Binance Testnet...")
        client = BinanceClient(api_key, api_secret)
        
        if not client.test_connectivity():
            print("Error: Could not connect to Binance API")
            logger.error("API connectivity test failed")
            sys.exit(1)
        
        print("Connected successfully\n")
        logger.info("API connection established")
        
        order_manager = OrderManager(client)
        
        print("Placing order...")
        result = order_manager.place_order(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price
        )
        
        print(order_manager.get_order_summary(result))
        
        if result.get('success'):
            logger.info("Order completed successfully")
            sys.exit(0)
        else:
            logger.error(f"Order failed: {result.get('error')}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        logger.exception("Unexpected error occurred")
        sys.exit(1)


if __name__ == '__main__':
    main()
