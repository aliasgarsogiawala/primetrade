# Binance Futures Testnet Trading Bot

A Python CLI application for placing orders on Binance Futures Testnet (USDT-M).

## Features

- Place Market and Limit orders
- Support for BUY and SELL sides
- Input validation
- Structured logging
- Clean error handling

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

Create a `.env` file in the project root:

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

### Place a Limit Order

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 50000
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| --symbol | Yes | Trading pair (e.g., BTCUSDT) |
| --side | Yes | Order side: BUY or SELL |
| --type | Yes | Order type: MARKET or LIMIT |
| --quantity | Yes | Order quantity |
| --price | For LIMIT | Limit price |

## Project Structure

```
primetrade/
    bot/
        __init__.py
        client.py         # Binance API client wrapper
        orders.py         # Order placement logic
        validators.py     # Input validation
        logging_config.py # Logging setup
    cli.py                # CLI entry point
    logs/                 # Log files directory
    README.md
    requirements.txt
```

## Logging

All API requests, responses, and errors are logged to `logs/trading_bot.log`.

## Assumptions

- Using Binance Futures Testnet (USDT-M) only
- Minimum order quantities follow Binance testnet rules
- Network connectivity is available
- API credentials are valid and have trading permissions
