# Binance Futures Testnet Trading Bot

A Python CLI application for placing orders on Binance Futures Testnet (USDT-M).

## Features

- Place Market and Limit orders
- Support for BUY and SELL sides
- Input validation
- Structured logging to file
- Clean error handling for API and network failures
- **Interactive CLI mode** with menus, prompts, and colored output

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/aliasgarsogiawala/primetrade.git
cd primetrade

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys
cp .env.example .env
# Edit .env with your Binance Testnet API keys

# 5. Run
python interactive.py        # Interactive mode
python cli.py --help         # Command line mode
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/aliasgarsogiawala/primetrade.git
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

### Interactive Mode (Recommended)

Launch the interactive menu-driven interface:

```bash
python interactive.py
```

Features:
- Visual menu system
- Guided prompts for order placement
- Order confirmation before execution
- Colored output for better readability
- View open orders
- Check account balance
- Get current prices

Screenshot:
```
    ╔══════════════════════════════════════════════════════╗
    ║         Futures Testnet Trading Bot                  ║
    ╚══════════════════════════════════════════════════════╝

  ══════════════════════════════════════════════════
    MAIN MENU
  ══════════════════════════════════════════════════
    [1] Place Market Order
    [2] Place Limit Order
    [3] View Open Orders
    [4] Check Account Balance
    [5] Get Current Price
    [0] Exit
  ══════════════════════════════════════════════════
```

### Command Line Mode

For scripting or quick orders, use the standard CLI:

#### Place a Market Order

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.002
```

Output:
```
==================================================
ORDER REQUEST
==================================================
Symbol:       BTCUSDT
Side:         BUY
Type:         MARKET
Quantity:     0.002
==================================================

Connecting to Binance Testnet...
Connected successfully

Placing order...
==================================================
ORDER EXECUTED SUCCESSFULLY
==================================================
Order ID:     12040222728
Symbol:       BTCUSDT
Side:         BUY
Type:         MARKET
Status:       NEW
Quantity:     0.002
Executed:     0.000
==================================================
```

#### Place a Limit Order

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.002 --price 120000
```

#### Short Form Arguments

```bash
python cli.py -s ETHUSDT --side BUY -t MARKET -q 0.01
```

### CLI Arguments

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
├── bot/
│   ├── __init__.py         # Package exports
│   ├── client.py           # Binance API client wrapper
│   ├── orders.py           # Order placement logic
│   ├── validators.py       # Input validation
│   ├── logging_config.py   # Logging setup
│   └── utils.py            # Utility functions
├── deliverable_logs/       # Sample execution logs
│   ├── market_order.log    # Market order log
│   └── limit_order.log     # Limit order log
├── logs/                   # Runtime logs
│   └── trading_bot.log     # Main log file
├── cli.py                  # Command-line interface
├── interactive.py          # Interactive menu interface
├── .env.example            # Environment template
├── .gitignore
├── README.md
└── requirements.txt
```

## Deliverables

### Log Files

Sample execution logs are in `deliverable_logs/`:

| File | Description |
|------|-------------|
| `market_order.log` | Successful MARKET BUY order (Order ID: 12040222728) |
| `limit_order.log` | Successful LIMIT SELL order (Order ID: 12040222994) |

### What's Logged

- API request details (endpoint, params)
- API response data (order ID, status)
- Error messages with codes
- Timestamps for all operations

## Logging

All API requests, responses, and errors are logged to `logs/trading_bot.log`.

Log format:
```
2026-01-30 17:28:42 | INFO     | trading_bot.cli | Starting trading bot
2026-01-30 17:28:42 | DEBUG    | trading_bot.client | Request: POST /fapi/v1/order
2026-01-30 17:28:42 | INFO     | trading_bot.orders | Order placed successfully: 12040222728
```

Log levels:
- **DEBUG**: API requests/responses (detailed)
- **INFO**: Order status, connections
- **ERROR**: Failures and exceptions

## Error Handling

The bot handles various error conditions:

| Error Type | Example | Handling |
|------------|---------|----------|
| Validation | Invalid symbol | Clear error message before API call |
| API Error | Insufficient margin | Error code + message from Binance |
| Network | Connection timeout | Retry suggestion + logged |

Example error output:
```
==================================================
ORDER FAILED
==================================================
Code:  -4016
Error: Limit price can't be higher than 86856.21.
==================================================
```

## Validation

Input validation includes:

- **Symbol**: Must end with USDT (e.g., BTCUSDT)
- **Side**: Must be BUY or SELL
- **Order Type**: Must be MARKET or LIMIT
- **Quantity**: Must be positive number
- **Price**: Required for LIMIT orders, must be positive

## Assumptions

- Using Binance Futures Testnet (USDT-M) only
- Minimum order value is $100 (Binance requirement)
- Network connectivity is available
- API credentials have futures trading permissions
- Default time-in-force for LIMIT orders is GTC (Good Till Cancelled)

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| python-dotenv | 1.0.0 | Environment variable management |
| requests | 2.31.0 | HTTP client for API calls |

## Testing with Testnet

1. Register at https://testnet.binancefuture.com
2. Get free testnet funds from the faucet
3. Generate API keys in account settings
4. Add keys to `.env` file
5. Run orders against testnet (no real money involved)

## Bonus Feature: Interactive CLI

The interactive mode (`python interactive.py`) provides:

- Color-coded output (green=success, red=error, yellow=prompts)
- ASCII art banner
- Menu-driven navigation
- Order confirmation prompts
- Input shortcuts (B for BUY, S for SELL)
- Helpful tips for limit order pricing
- Account balance viewer
- Price checker
