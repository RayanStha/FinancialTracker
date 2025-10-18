# Bi-Weekly Investment Planner

A Python script that automates your investing process every paycheck. It fetches real-time stock prices and recent news from APIs, generates suggested buys for each pay period, and outputs a comprehensive Excel workbook with portfolio analysis and allocation plans.

## Features

- **Real-time Market Data**: Fetches current stock prices and recent news from multiple API providers
- **Portfolio Management**: Tracks current holdings with gain/loss calculations
- **Bi-weekly Allocation**: Automatically calculates dollar-cost averaging across configurable investment buckets
- **Excel Output**: Generates a single comprehensive Excel workbook with 5 organized sheets:
  - **Dashboard**: Executive summary with portfolio overview and key metrics
  - **Portfolio**: Current holdings with performance tracking and formulas
  - **Allocation**: Bi-weekly investment plan with suggested buys
  - **Research**: Market data, news headlines, and current prices
  - **Strategy**: Long-term core holdings and allocation strategy
- **Multiple API Support**: Works with Finnhub, Polygon.io, and Alpha Vantage
- **Configurable**: Customize allocations, tickers, and buckets via JSON/YAML config files
- **Error Handling**: Graceful fallbacks when APIs fail or data is unavailable

## Installation

1. **Clone or download** this repository
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API keys**:
   - Copy `env_example.txt` to `.env`
   - Add your API keys for at least one provider:
     - [Finnhub](https://finnhub.io/) (Free: 60 calls/minute)
     - [Polygon.io](https://polygon.io/) (Free: 5 calls/minute)
     - [Alpha Vantage](https://www.alphavantage.co/) (Free: 5 calls/minute, 500 calls/day)

## Usage

### Basic Usage

```bash
python invest_plan.py
```

This will use default settings:
- $1,000 bi-weekly contribution
- Finnhub API provider
- 3 news articles per ticker
- Output: `InvestmentPlan.xlsx`

### Advanced Usage

```bash
python invest_plan.py --contribution 1500 --provider polygon --news-per-ticker 5 --output MyPlan.xlsx
```

### With Custom Configuration

```bash
python invest_plan.py --config my_config.json --contribution 2000
```

### Command Line Options

- `--contribution`: Bi-weekly contribution amount (default: 1000)
- `--provider`: API provider - `finnhub`, `polygon`, or `alpha` (default: finnhub)
- `--news-per-ticker`: Number of news articles per ticker (default: 3)
- `--config`: Path to custom configuration file (JSON or YAML)
- `--output`: Output Excel filename (default: InvestmentPlan.xlsx)

## Configuration

### Default Allocation Strategy

The script uses a 4-bucket allocation strategy:

| Bucket | Allocation | Example Tickers |
|--------|------------|-----------------|
| ETF/Index | 30% | VTI, VOO, SCHD |
| BlueChip/Core | 20% | AAPL, MSFT, AVGO, UNH, UPS |
| Growth | 30% | NVDA, CRWD, PANW, GOOGL, AMZN, TSLA |
| Speculative | 20% | HIMS, ZYNE |

### Custom Configuration

Create a JSON or YAML file to customize your allocation strategy:

```json
{
  "allocation_buckets": {
    "ETF/Index": {
      "percentage": 40,
      "tickers": ["VTI", "VOO", "SCHD", "QQQ"]
    },
    "BlueChip/Core": {
      "percentage": 30,
      "tickers": ["AAPL", "MSFT", "AVGO", "UNH", "UPS", "JNJ"]
    },
    "Growth": {
      "percentage": 20,
      "tickers": ["NVDA", "CRWD", "PANW", "GOOGL", "AMZN", "TSLA"]
    },
    "Speculative": {
      "percentage": 10,
      "tickers": ["HIMS", "ZYNE", "ARKK"]
    }
  }
}
```

**Important**: Allocation percentages must sum to 100%.

## Output Files

### Excel Workbook Structure

The script generates a single comprehensive Excel file with 5 organized sheets:

#### 1. Dashboard
- **Executive Summary**: Portfolio overview with total market value, cost basis, and performance
- **Bi-Weekly Plan Summary**: Quick view of allocation across investment buckets
- **Top Performers**: Best performing stocks in your portfolio
- **Data Source Info**: Provider used, last updated timestamp, and data statistics

#### 2. Portfolio
- All portfolio positions with real-time prices
- Calculated market values, cost basis, and gain/loss
- Auto-sum totals and portfolio-level performance formulas
- Frozen headers and auto-filters for easy navigation

#### 3. Allocation
- **Allocation Summary**: Shows how your contribution is distributed across buckets
- **Suggested Buys**: Specific tickers, prices, dollar amounts, and calculated shares
- **Total Allocation Check**: Formulas to verify percentages sum to 100%

#### 4. Research
- Recent headlines for each ticker with sources and links
- Current prices with daily changes and percentages
- Investment bucket summary showing ticker categorization

#### 5. Strategy
- Target allocation strategy for long-term core holdings
- Percentage targets and notes for each position
- Strategy explanation and rebalancing guidance

## API Providers

### Finnhub (Recommended)
- **Free Tier**: 60 calls/minute
- **Sign up**: [finnhub.io](https://finnhub.io/)
- **Best for**: High-frequency usage, reliable data

### Polygon.io
- **Free Tier**: 5 calls/minute
- **Sign up**: [polygon.io](https://polygon.io/)
- **Best for**: Comprehensive market data

### Alpha Vantage
- **Free Tier**: 5 calls/minute, 500 calls/day
- **Sign up**: [alphavantage.co](https://www.alphavantage.co/)
- **Best for**: News sentiment analysis

## Default Portfolio

The script includes these default holdings (you can customize via config):

**Core Holdings**: NVDA, MSFT, AMZN, TSLA, CRWD, GOOGL, AAPL, PANW, AVGO, UNH, UPS, VST, HIMS, AB, ZYNE

**ETFs**: VTI, VOO, SCHD

## Error Handling

The script includes robust error handling:
- API failures don't crash the program
- Missing data is filled with "N/A" or 0 values
- Timeout protection for API calls
- Graceful degradation when services are unavailable

## Example Output

After running the script, you'll see output like:

```
2024-01-15 10:30:00 - INFO - Starting investment planner with finnhub provider
2024-01-15 10:30:00 - INFO - Bi-weekly contribution: $1,000.00
2024-01-15 10:30:01 - INFO - Fetching market data using finnhub provider...
2024-01-15 10:30:02 - INFO - Fetching quotes for 18 tickers...
2024-01-15 10:30:05 - INFO - Fetching news for 18 tickers...
2024-01-15 10:30:08 - INFO - Successfully fetched 18 quotes and news for 18 tickers
2024-01-15 10:30:08 - INFO - Creating Excel workbook: InvestmentPlan.xlsx
2024-01-15 10:30:10 - INFO - Excel workbook created successfully: InvestmentPlan.xlsx
2024-01-15 10:30:10 - INFO - Investment plan completed successfully!
2024-01-15 10:30:10 - INFO - Output file: InvestmentPlan.xlsx
2024-01-15 10:30:10 - INFO - Provider used: finnhub
2024-01-15 10:30:10 - INFO - Quotes fetched: 18
2024-01-15 10:30:10 - INFO - News articles fetched: 54
```

## Troubleshooting

### Common Issues

1. **API Key Errors**: Make sure your `.env` file contains valid API keys
2. **Rate Limiting**: Free API tiers have limits; consider upgrading or using multiple providers
3. **Missing Data**: Some tickers may not have data; the script will handle this gracefully
4. **Excel File Issues**: Make sure you have write permissions in the output directory

### Getting API Keys

1. **Finnhub**: Sign up at [finnhub.io](https://finnhub.io/) - instant free tier
2. **Polygon.io**: Sign up at [polygon.io](https://polygon.io/) - requires email verification
3. **Alpha Vantage**: Sign up at [alphavantage.co](https://www.alphavantage.co/) - instant free tier

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the script.

## License

This project is open source and available under the MIT License.
