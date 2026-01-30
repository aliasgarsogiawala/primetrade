# Binance Futures Testnet Trading Bot

A Python CLI application for placing orders on Binance Futures Testnet (USDT-M).

## Features

- Place Market and Limit orders
- Support for BUY and SELL sides
- Input validation
- Structured logging to file
- Clean error handling for API and network failures

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd primetrade
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API credentials

Copy the example env file and add your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your testnet API keys:

```
BINANCE_TESTNET_API_KEY=your_api_key_here
BINANCE_TESTNET_API_SECRET=your_api_secret_here
```

Get your testnet credentials from: https://testnet.binancefuture.com

## Usage

### Place a Market Order

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

Output:
```
==================================================
ORDER REQUEST
==================================================
Symbol:       BTCUSDT
Side:         BUY
Type:         MARKET
Quantity:     0.001
==================================================

Connecting to Binance Testnet...
Connected successfully

Placing order...
==================================================
ORDER EXECUTED SUCCESSFULLY
==================================================
Order ID:     4397283641
Symbol:       BTCUSDT
Side:         BUY
Type:         MARKET
Status:       FILLED
Quantity:     0.001
Executed:     0.001
Avg Price:    104523.50
==================================================
```

### Place a Limit Order

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 110000
```

### Short Form Arguments

```bash
python cli.py -s ETHUSDT --side BUY -t MARKET -q 0.01
```

### Arguments

| Argument | Short | Required | Description |
|----------|-------|----------|-------------|
| --symbol | -s | Yes | Trading pair (e.g., BTCUSDT, ETHUSDT) |
| --side | | Yes | Order side: BUY or SELL |
| --type | -t | Yes | Order type: MARKET or LIMIT |
| --quantity | -q | Yes | Order quantity |
| --price | -p | For LIMIT | Limit price (required for LIMIT orders) |

## Project Structure

```
primetrade/
    bot/
        __init__.py
        client.py         # Binance API client wrapper
        orders.py         # Order placement logic
        validators.py     # Input validation
        logging_config.py # Logging setup
        utils.py          # Utility functions
    cli.py                # CLI entry point
    logs/                 # Log files directory
    README.md
    requirements.txt
```

## Logging

All API requests, responses, and errors are logged to `logs/trading_bot.log`.

Log format:
```
2026-01-30 13:45:22 | INFO     | trading_bot.cli | Starting trading bot
2026-01-30 13:45:22 | DEBUG    | trading_bot.client | Request: POST /fapi/v1/order
```

Sample log files are included in `logs/` directory:
- `market_order_example.log` - Example market order execution
- `limit_order_example.log` - Example limit order execution

## Error Handling

The bot handles various error conditions:

- **Validation errors**: Invalid symbol, side, order type, or quantity
- **API errors**: Insufficient balance, invalid API key, rate limits
- **Network errors**: Connection timeouts, DNS failures

Example error output:
```
Order Failed: Margin is insufficient.
```

## Assumptions

- Using Binance Futures Testnet (USDT-M) only
- Minimum order quantities follow Binance testnet rules (e.g., 0.001 BTC)
- Network connectivity is available
- API credentials are valid and have futures trading permissions
- Default time-in-force for LIMIT orders is GTC (Good Till Cancelled)

## Dependencies

- python-dotenv: Environment variable management
- requests: HTTP client for API calls

## Testing with Testnet

1. Register at https://testnet.binancefuture.com
2. Get free testnet funds from the faucet
3. Generate API keys in account settings
4. Add keys to `.env` file
5. Run orders against testnet (no real money involved)
