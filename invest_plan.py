#!/usr/bin/env python3
"""
Bi-Weekly Investing Planner

A Python script that automates investing process every paycheck.
Fetches real-time stock prices and news, generates suggested buys,
and outputs an Excel workbook with portfolio analysis and allocation plans.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
import warnings

import pandas as pd
import requests
import xlsxwriter
from dotenv import load_dotenv

# Suppress pandas warnings for cleaner output
warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class InvestmentPlanner:
    """Main class for the bi-weekly investment planner."""
    
    def __init__(self, contribution: float = 1000.0, provider: str = 'finnhub', 
                 news_per_ticker: int = 3, config_file: Optional[str] = None):
        """
        Initialize the investment planner.
        
        Args:
            contribution: Bi-weekly contribution amount
            provider: API provider ('finnhub', 'polygon', 'alpha')
            news_per_ticker: Number of news articles per ticker
            config_file: Optional configuration file path
        """
        self.contribution = contribution
        self.provider = provider.lower()
        self.news_per_ticker = news_per_ticker
        self.config = self._load_config(config_file)
        
        # Initialize API client
        self.api_client = self._get_api_client()
        
        # Portfolio data
        self.holdings = self._initialize_holdings()
        self.quotes = {}
        self.news = {}
        
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            'allocation_buckets': {
                'Core / Tech': {'percentage': 25, 'tickers': ['AAPL', 'MSFT', 'GOOGL', 'AVGO']},
                'Growth / AI': {'percentage': 30, 'tickers': ['NVDA', 'AMZN', 'TSLA', 'CRWD', 'PANW']},
                'Dividend / Defensive': {'percentage': 20, 'tickers': ['UNH', 'UPS', 'VST', 'AB']},
                'Speculative / High Risk': {'percentage': 15, 'tickers': ['HIMS', 'ZYNE', 'BULL']},
                'Future Additions': {'percentage': 10, 'tickers': ['VTI', 'VOO', 'SCHD']}
            },
            'core_longterm': {
                'NVDA': {'target_percentage': 15, 'notes': 'AI leader, long-term hold'},
                'AAPL': {'target_percentage': 12, 'notes': 'Core portfolio anchor'},
                'MSFT': {'target_percentage': 10, 'notes': 'Cloud + AI growth'},
                'GOOGL': {'target_percentage': 8, 'notes': 'Advertising + AI'},
                'AVGO': {'target_percentage': 8, 'notes': 'Dividend + chip exposure'},
                'AMZN': {'target_percentage': 7, 'notes': 'Long-term e-commerce play'},
                'CRWD': {'target_percentage': 6, 'notes': 'Strong momentum stock'},
                'PANW': {'target_percentage': 5, 'notes': 'Security sector exposure'},
                'TSLA': {'target_percentage': 4, 'notes': 'High risk, long-term'},
                'UNH': {'target_percentage': 4, 'notes': 'Healthcare stability'},
                'UPS': {'target_percentage': 3, 'notes': 'Dividend yield stock'},
                'VST': {'target_percentage': 3, 'notes': 'Utility stability'},
                'AB': {'target_percentage': 2, 'notes': 'Dividend reinvestment candidate'},
                'HIMS': {'target_percentage': 2, 'notes': 'Small-cap growth potential'},
                'ZYNE': {'target_percentage': 1, 'notes': 'High risk, small position'},
                'BULL': {'target_percentage': 1, 'notes': 'High risk, consider replacing'}
            }
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    if config_file.endswith('.json'):
                        user_config = json.load(f)
                    else:
                        import yaml
                        user_config = yaml.safe_load(f)
                
                # Merge with defaults
                default_config.update(user_config)
                logger.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config file {config_file}: {e}")
                logger.info("Using default configuration")
        
        # Validate allocation percentages sum to 100%
        total_percentage = sum(bucket['percentage'] for bucket in default_config['allocation_buckets'].values())
        if abs(total_percentage - 100) > 0.01:
            raise ValueError(f"Allocation percentages must sum to 100%, got {total_percentage}%")
        
        return default_config
    
    def _get_api_client(self):
        """Initialize the appropriate API client based on provider."""
        if self.provider == 'finnhub':
            return FinnhubClient()
        elif self.provider == 'polygon':
            return PolygonClient()
        elif self.provider == 'alpha':
            return AlphaVantageClient()
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _initialize_holdings(self) -> pd.DataFrame:
        """Initialize current holdings data."""
        holdings_data = [
            {'Ticker': 'NVDA', 'Company Name': 'NVIDIA Corporation', 'Shares': 1.03, 'Avg Cost': 119.22, 'Category': 'Growth / AI'},
            {'Ticker': 'MSFT', 'Company Name': 'Microsoft Corporation', 'Shares': 0.20, 'Avg Cost': 490.00, 'Category': 'Core / Tech Blue Chip'},
            {'Ticker': 'AMZN', 'Company Name': 'Amazon.com Inc.', 'Shares': 0.11, 'Avg Cost': 193.00, 'Category': 'Growth / Consumer Tech'},
            {'Ticker': 'TSLA', 'Company Name': 'Tesla Inc.', 'Shares': 0.08, 'Avg Cost': 164.00, 'Category': 'High Volatility / Growth'},
            {'Ticker': 'CRWD', 'Company Name': 'CrowdStrike Holdings Inc.', 'Shares': 0.14, 'Avg Cost': 305.00, 'Category': 'Cybersecurity / Growth'},
            {'Ticker': 'GOOGL', 'Company Name': 'Alphabet Inc. Class A', 'Shares': 0.37, 'Avg Cost': 199.00, 'Category': 'Core / Tech'},
            {'Ticker': 'AAPL', 'Company Name': 'Apple Inc.', 'Shares': 0.51, 'Avg Cost': 223.00, 'Category': 'Core / Tech'},
            {'Ticker': 'PANW', 'Company Name': 'Palo Alto Networks Inc.', 'Shares': 0.29, 'Avg Cost': 189.00, 'Category': 'Cybersecurity'},
            {'Ticker': 'AVGO', 'Company Name': 'Broadcom Inc.', 'Shares': 0.60, 'Avg Cost': 244.00, 'Category': 'Dividend / Semi'},
            {'Ticker': 'UNH', 'Company Name': 'UnitedHealth Group Inc.', 'Shares': 0.0, 'Avg Cost': 0.0, 'Category': 'Defensive / Healthcare'},
            {'Ticker': 'UPS', 'Company Name': 'United Parcel Service Inc.', 'Shares': 0.0, 'Avg Cost': 0.0, 'Category': 'Dividend / Industrial'},
            {'Ticker': 'VST', 'Company Name': 'Vistra Corp.', 'Shares': 0.0, 'Avg Cost': 0.0, 'Category': 'Utility / Energy'},
            {'Ticker': 'HIMS', 'Company Name': 'Hims & Hers Health Inc.', 'Shares': 0.0, 'Avg Cost': 0.0, 'Category': 'Speculative / HealthTech'},
            {'Ticker': 'AB', 'Company Name': 'AllianceBernstein Holding L.P.', 'Shares': 0.44, 'Avg Cost': 32.00, 'Category': 'Dividend / Asset Mgmt'},
            {'Ticker': 'ZYNE', 'Company Name': 'Zynerba Pharmaceuticals Inc.', 'Shares': 1.00, 'Avg Cost': 1.25, 'Category': 'Speculative / Biotech'},
            {'Ticker': 'BULL', 'Company Name': 'Direxion Daily S&P 500 Bull 3X ETF', 'Shares': 3.46, 'Avg Cost': 7.07, 'Category': 'Leveraged ETF'},
        ]
        
        return pd.DataFrame(holdings_data)
    
    def fetch_market_data(self):
        """Fetch current quotes and news for all tickers."""
        logger.info(f"Fetching market data using {self.provider} provider...")
        
        all_tickers = self.holdings['Ticker'].tolist()
        
        # Fetch quotes
        logger.info(f"Fetching quotes for {len(all_tickers)} tickers...")
        self.quotes = self.api_client.fetch_quotes(all_tickers)
        
        # Fetch news
        logger.info(f"Fetching news for {len(all_tickers)} tickers...")
        self.news = self.api_client.fetch_news(all_tickers, self.news_per_ticker)
        
        logger.info(f"Successfully fetched {len(self.quotes)} quotes and news for {len(self.news)} tickers")
    
    def build_holdings_dataframe(self) -> pd.DataFrame:
        """Build the current holdings dataframe with live data."""
        holdings_df = self.holdings.copy()
        
        # Add current prices and calculate values
        holdings_df['Current Price'] = holdings_df['Ticker'].map(
            lambda x: self.quotes.get(x, {}).get('price', 0)
        )
        holdings_df['Market Value'] = holdings_df['Shares'] * holdings_df['Current Price']
        holdings_df['Cost Basis'] = holdings_df['Shares'] * holdings_df['Avg Cost']
        holdings_df['Gain/Loss $'] = holdings_df['Market Value'] - holdings_df['Cost Basis']
        holdings_df['Gain/Loss %'] = holdings_df.apply(
            lambda row: (row['Market Value'] / row['Cost Basis'] - 1) * 100 
            if row['Cost Basis'] > 0 else 0, axis=1
        )
        
        # Add data source and timestamp
        holdings_df['Data Source'] = self.provider.title()
        holdings_df['Timestamp'] = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        
        return holdings_df
    
    def calculate_biweekly_allocation(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Calculate bi-weekly allocation and suggested buys."""
        # Allocation summary
        allocation_data = []
        for bucket_name, bucket_info in self.config['allocation_buckets'].items():
            allocation_data.append({
                'Bucket': bucket_name,
                'Allocation %': bucket_info['percentage'],
                'Bi-Weekly $': self.contribution * bucket_info['percentage'] / 100
            })
        
        allocation_df = pd.DataFrame(allocation_data)
        
        # Suggested buys
        suggested_buys = []
        for bucket_name, bucket_info in self.config['allocation_buckets'].items():
            bucket_amount = self.contribution * bucket_info['percentage'] / 100
            tickers = bucket_info['tickers']
            
            if tickers:
                amount_per_ticker = bucket_amount / len(tickers)
                
                for ticker in tickers:
                    price = self.quotes.get(ticker, {}).get('price', 0)
                    shares = amount_per_ticker / price if price > 0 else 0
                    
                    suggested_buys.append({
                        'Bucket': bucket_name,
                        'Ticker': ticker,
                        'Price': price,
                        '$ Allocation': amount_per_ticker,
                        'Shares': round(shares, 4)
                    })
        
        suggested_buys_df = pd.DataFrame(suggested_buys)
        
        return allocation_df, suggested_buys_df
    
    def build_news_dataframe(self) -> pd.DataFrame:
        """Build news dataframe for watchlist."""
        news_data = []
        
        for ticker, articles in self.news.items():
            for article in articles:
                news_data.append({
                    'Ticker': ticker,
                    'Headline': article.get('headline', 'N/A'),
                    'Source': article.get('source', 'N/A'),
                    'Published': article.get('published', 'N/A'),
                    'URL': article.get('url', 'N/A')
                })
        
        return pd.DataFrame(news_data)
    
    def build_core_longterm_dataframe(self) -> pd.DataFrame:
        """Build core long-term holdings dataframe."""
        core_data = []
        
        for ticker, info in self.config['core_longterm'].items():
            core_data.append({
                'Ticker/Fund': ticker,
                'Target % in Core': info['target_percentage'],
                'Notes': info['notes']
            })
        
        return pd.DataFrame(core_data)
    
    def create_excel_workbook(self, filename: str = 'InvestmentPlan.xlsx'):
        """Create a comprehensive Excel workbook with all necessary data in organized sheets."""
        logger.info(f"Creating comprehensive Excel workbook: {filename}")
        
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#366092',
                'font_color': 'white',
                'border': 1
            })
            
            currency_format = workbook.add_format({'num_format': '$#,##0.00'})
            percentage_format = workbook.add_format({'num_format': '0.00%'})
            number_format = workbook.add_format({'num_format': '0.0000'})
            date_format = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'})
            
            # 1. DASHBOARD - Executive Summary Sheet
            self._create_dashboard_sheet(writer, workbook, header_format, currency_format, percentage_format)
            
            # 2. PORTFOLIO - Current Holdings with Performance
            self._create_portfolio_sheet(writer, workbook, currency_format, percentage_format, number_format)
            
            # 3. ALLOCATION - Bi-Weekly Investment Plan
            self._create_allocation_sheet(writer, workbook, currency_format, percentage_format, number_format)
            
            # 4. RESEARCH - Market Data & News
            self._create_research_sheet(writer, workbook, date_format)
            
            # 5. STRATEGY - Long-term Core Holdings
            self._create_strategy_sheet(writer, workbook, percentage_format)
        
        logger.info(f"Comprehensive Excel workbook created successfully: {filename}")
        return filename
    
    def _create_dashboard_sheet(self, writer, workbook, header_format, currency_format, percentage_format):
        """Create the executive dashboard sheet."""
        dashboard_sheet = workbook.add_worksheet('Dashboard')
        
        # Title
        dashboard_sheet.merge_range('A1:F1', 'Investment Portfolio Dashboard', 
                                  workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center'}))
        
        # Portfolio Summary
        holdings_df = self.build_holdings_dataframe()
        total_market_value = holdings_df['Market Value'].sum()
        total_cost_basis = holdings_df['Cost Basis'].sum()
        total_gain_loss = total_market_value - total_cost_basis
        total_gain_loss_pct = (total_gain_loss / total_cost_basis * 100) if total_cost_basis > 0 else 0
        
        dashboard_sheet.write('A3', 'Portfolio Summary', header_format)
        dashboard_sheet.write('A4', 'Total Market Value:')
        dashboard_sheet.write('B4', total_market_value, currency_format)
        dashboard_sheet.write('A5', 'Total Cost Basis:')
        dashboard_sheet.write('B5', total_cost_basis, currency_format)
        dashboard_sheet.write('A6', 'Total Gain/Loss:')
        dashboard_sheet.write('B6', total_gain_loss, currency_format)
        dashboard_sheet.write('A7', 'Total Return %:')
        dashboard_sheet.write('B7', total_gain_loss_pct / 100, percentage_format)
        
        # Bi-weekly Plan Summary
        allocation_df, suggested_buys_df = self.calculate_biweekly_allocation()
        dashboard_sheet.write('A9', 'Bi-Weekly Investment Plan', header_format)
        dashboard_sheet.write('A10', f'Contribution Amount: ${self.contribution:,.2f}')
        
        row = 11
        for _, bucket in allocation_df.iterrows():
            dashboard_sheet.write(f'A{row}', f"{bucket['Bucket']}:")
            dashboard_sheet.write(f'B{row}', bucket['Bi-Weekly $'], currency_format)
            dashboard_sheet.write(f'C{row}', f"{bucket['Allocation %']}%")
            row += 1
        
        # Top Performers
        top_performers = holdings_df.nlargest(3, 'Gain/Loss %')
        dashboard_sheet.write('A15', 'Top Performers', header_format)
        row = 16
        for _, stock in top_performers.iterrows():
            if stock['Gain/Loss %'] != 0 and pd.notna(stock['Gain/Loss %']):
                dashboard_sheet.write(f'A{row}', stock['Ticker'])
                dashboard_sheet.write(f'B{row}', f"{stock['Gain/Loss %']:.2f}%")
                row += 1
        
        # Data Source Info
        dashboard_sheet.write('A20', 'Data Source Information', header_format)
        dashboard_sheet.write('A21', f'Provider: {self.provider.title()}')
        dashboard_sheet.write('A22', f'Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        dashboard_sheet.write('A23', f'Quotes Fetched: {len(self.quotes)}')
        dashboard_sheet.write('A24', f'News Articles: {sum(len(articles) for articles in self.news.values())}')
        
        # Format columns
        dashboard_sheet.set_column('A:A', 20)
        dashboard_sheet.set_column('B:B', 15, currency_format)
        dashboard_sheet.set_column('C:C', 10)
    
    def _create_portfolio_sheet(self, writer, workbook, currency_format, percentage_format, number_format):
        """Create the portfolio holdings sheet."""
        holdings_df = self.build_holdings_dataframe()
        holdings_df.to_excel(writer, sheet_name='Portfolio', index=False)
        
        portfolio_sheet = writer.sheets['Portfolio']
        
        # Add formulas for totals
        last_row = len(holdings_df) + 1
        portfolio_sheet.write(f'A{last_row + 1}', 'TOTALS', workbook.add_format({'bold': True}))
        portfolio_sheet.write_formula(f'E{last_row + 1}', f'=SUM(E2:E{last_row})', currency_format)
        portfolio_sheet.write_formula(f'F{last_row + 1}', f'=SUM(F2:F{last_row})', currency_format)
        portfolio_sheet.write_formula(f'G{last_row + 1}', f'=SUM(G2:G{last_row})', currency_format)
        portfolio_sheet.write_formula(f'H{last_row + 1}', f'=IF(F{last_row + 1}>0,G{last_row + 1}/F{last_row + 1}-1,"")', percentage_format)
        
        # Format columns
        portfolio_sheet.set_column('A:A', 12)
        portfolio_sheet.set_column('B:B', 30)
        portfolio_sheet.set_column('C:C', 10, number_format)
        portfolio_sheet.set_column('D:D', 10, currency_format)
        portfolio_sheet.set_column('E:E', 12, currency_format)
        portfolio_sheet.set_column('F:F', 12, currency_format)
        portfolio_sheet.set_column('G:G', 12, currency_format)
        portfolio_sheet.set_column('H:H', 12, percentage_format)
        portfolio_sheet.set_column('I:I', 15)
        portfolio_sheet.set_column('J:J', 15)
        portfolio_sheet.set_column('K:K', 20)
        
        # Freeze panes and add filters
        portfolio_sheet.freeze_panes(1, 0)
        portfolio_sheet.autofilter(0, 0, len(holdings_df), len(holdings_df.columns) - 1)
    
    def _create_allocation_sheet(self, writer, workbook, currency_format, percentage_format, number_format):
        """Create the allocation and suggested buys sheet."""
        allocation_df, suggested_buys_df = self.calculate_biweekly_allocation()
        
        # Write allocation summary
        allocation_df.to_excel(writer, sheet_name='Allocation', index=False, startrow=0)
        
        # Write suggested buys
        suggested_buys_df.to_excel(writer, sheet_name='Allocation', index=False, startrow=len(allocation_df) + 3)
        
        allocation_sheet = writer.sheets['Allocation']
        allocation_sheet.write(len(allocation_df) + 1, 0, 'Suggested Buys', workbook.add_format({'bold': True}))
        
        # Add summary formulas
        last_row = len(allocation_df) + len(suggested_buys_df) + 4
        allocation_sheet.write(f'A{last_row + 1}', 'Total Allocation Check:')
        allocation_sheet.write_formula(f'B{last_row + 1}', f'=SUM(B2:B{len(allocation_df) + 1})', percentage_format)
        allocation_sheet.write(f'C{last_row + 1}', f'=SUM(C2:C{len(allocation_df) + 1})', currency_format)
        
        # Format columns
        allocation_sheet.set_column('A:A', 20)
        allocation_sheet.set_column('B:B', 12, percentage_format)
        allocation_sheet.set_column('C:C', 12, currency_format)
        allocation_sheet.set_column('D:D', 12)
        allocation_sheet.set_column('E:E', 12, currency_format)
        allocation_sheet.set_column('F:F', 12, currency_format)
        allocation_sheet.set_column('G:G', 12, number_format)
    
    def _create_research_sheet(self, writer, workbook, date_format):
        """Create the research and news sheet."""
        news_df = self.build_news_dataframe()
        news_df.to_excel(writer, sheet_name='Research', index=False)
        
        research_sheet = writer.sheets['Research']
        research_sheet.set_column('A:A', 12)
        research_sheet.set_column('B:B', 50)
        research_sheet.set_column('C:C', 20)
        research_sheet.set_column('D:D', 20, date_format)
        research_sheet.set_column('E:E', 50)
        
        # Add current prices section
        prices_row = len(news_df) + 3
        research_sheet.write(prices_row, 0, 'Current Prices', workbook.add_format({'bold': True}))
        
        row = prices_row + 1
        for ticker, quote_data in self.quotes.items():
            research_sheet.write(f'A{row}', ticker)
            research_sheet.write(f'B{row}', quote_data.get('price', 0))
            research_sheet.write(f'C{row}', quote_data.get('change', 0))
            change_pct = quote_data.get('change_percent', 0)
            if change_pct is not None:
                research_sheet.write(f'D{row}', f"{change_pct:.2f}%")
            else:
                research_sheet.write(f'D{row}', "N/A")
            row += 1
        
        # Add bucket summary
        summary_row = row + 2
        research_sheet.write(summary_row, 0, 'Investment Buckets', workbook.add_format({'bold': True}))
        
        row = summary_row + 1
        for bucket_name, bucket_info in self.config['allocation_buckets'].items():
            research_sheet.write(f'A{row}', bucket_name)
            research_sheet.write(f'B{row}', ', '.join(bucket_info['tickers']))
            research_sheet.write(f'C{row}', f"{bucket_info['percentage']}%")
            row += 1
    
    def _create_strategy_sheet(self, writer, workbook, percentage_format):
        """Create the long-term strategy sheet."""
        core_df = self.build_core_longterm_dataframe()
        core_df.to_excel(writer, sheet_name='Strategy', index=False)
        
        strategy_sheet = writer.sheets['Strategy']
        strategy_sheet.set_column('A:A', 20)
        strategy_sheet.set_column('B:B', 15, percentage_format)
        strategy_sheet.set_column('C:C', 40)
        
        # Add allocation strategy explanation
        last_row = len(core_df) + 3
        strategy_sheet.write(last_row, 0, 'Allocation Strategy', workbook.add_format({'bold': True}))
        strategy_sheet.write(last_row + 1, 0, 'This sheet outlines the long-term core holdings strategy.')
        strategy_sheet.write(last_row + 2, 0, 'Target percentages should be maintained over time through')
        strategy_sheet.write(last_row + 3, 0, 'regular rebalancing and strategic additions.')


class BaseAPIClient:
    """Base class for API clients."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'InvestmentPlanner/1.0'
        })
    
    def fetch_quotes(self, tickers: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch quotes for given tickers. To be implemented by subclasses."""
        raise NotImplementedError
    
    def fetch_news(self, tickers: List[str], limit: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch news for given tickers. To be implemented by subclasses."""
        raise NotImplementedError


class FinnhubClient(BaseAPIClient):
    """Finnhub API client."""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('FINNHUB_API_KEY')
        if not self.api_key:
            raise ValueError("FINNHUB_API_KEY environment variable not set")
        
        self.base_url = 'https://finnhub.io/api/v1'
    
    def fetch_quotes(self, tickers: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch quotes from Finnhub."""
        quotes = {}
        
        for ticker in tickers:
            try:
                url = f"{self.base_url}/quote"
                params = {'symbol': ticker, 'token': self.api_key}
                
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                quotes[ticker] = {
                    'price': data.get('c', 0),  # current price
                    'change': data.get('d', 0),  # change
                    'change_percent': data.get('dp', 0),  # change percent
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except Exception as e:
                logger.warning(f"Failed to fetch quote for {ticker}: {e}")
                quotes[ticker] = {'price': 0, 'change': 0, 'change_percent': 0, 'timestamp': 'N/A'}
        
        return quotes
    
    def fetch_news(self, tickers: List[str], limit: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch news from Finnhub."""
        news = {}
        
        for ticker in tickers:
            try:
                url = f"{self.base_url}/company-news"
                params = {
                    'symbol': ticker,
                    'from': (datetime.now() - pd.Timedelta(days=7)).strftime('%Y-%m-%d'),
                    'to': datetime.now().strftime('%Y-%m-%d'),
                    'token': self.api_key
                }
                
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                articles = response.json()[:limit]
                news[ticker] = []
                
                for article in articles:
                    news[ticker].append({
                        'headline': article.get('headline', 'N/A'),
                        'source': article.get('source', 'N/A'),
                        'published': article.get('datetime', 'N/A'),
                        'url': article.get('url', 'N/A')
                    })
                
            except Exception as e:
                logger.warning(f"Failed to fetch news for {ticker}: {e}")
                news[ticker] = []
        
        return news


class PolygonClient(BaseAPIClient):
    """Polygon.io API client."""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('POLYGON_API_KEY')
        if not self.api_key:
            raise ValueError("POLYGON_API_KEY environment variable not set")
        
        self.base_url = 'https://api.polygon.io'
    
    def fetch_quotes(self, tickers: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch quotes from Polygon.io."""
        quotes = {}
        
        for ticker in tickers:
            try:
                url = f"{self.base_url}/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}"
                params = {'apikey': self.api_key}
                
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                if 'results' in data and data['results']:
                    result = data['results']
                    quotes[ticker] = {
                        'price': result.get('value', 0),
                        'change': result.get('change', 0),
                        'change_percent': result.get('change_percent', 0),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                else:
                    quotes[ticker] = {'price': 0, 'change': 0, 'change_percent': 0, 'timestamp': 'N/A'}
                
            except Exception as e:
                logger.warning(f"Failed to fetch quote for {ticker}: {e}")
                quotes[ticker] = {'price': 0, 'change': 0, 'change_percent': 0, 'timestamp': 'N/A'}
        
        return quotes
    
    def fetch_news(self, tickers: List[str], limit: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch news from Polygon.io."""
        news = {}
        
        for ticker in tickers:
            try:
                url = f"{self.base_url}/v2/reference/news"
                params = {
                    'ticker': ticker,
                    'limit': limit,
                    'apikey': self.api_key
                }
                
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                news[ticker] = []
                
                if 'results' in data:
                    for article in data['results'][:limit]:
                        news[ticker].append({
                            'headline': article.get('title', 'N/A'),
                            'source': article.get('publisher', {}).get('name', 'N/A'),
                            'published': article.get('published_utc', 'N/A'),
                            'url': article.get('article_url', 'N/A')
                        })
                
            except Exception as e:
                logger.warning(f"Failed to fetch news for {ticker}: {e}")
                news[ticker] = []
        
        return news


class AlphaVantageClient(BaseAPIClient):
    """Alpha Vantage API client."""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if not self.api_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY environment variable not set")
        
        self.base_url = 'https://www.alphavantage.co/query'
    
    def fetch_quotes(self, tickers: List[str]) -> Dict[str, Dict[str, Any]]:
        """Fetch quotes from Alpha Vantage."""
        quotes = {}
        
        for ticker in tickers:
            try:
                params = {
                    'function': 'GLOBAL_QUOTE',
                    'symbol': ticker,
                    'apikey': self.api_key
                }
                
                response = self.session.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                if 'Global Quote' in data:
                    quote = data['Global Quote']
                    quotes[ticker] = {
                        'price': float(quote.get('05. price', 0)),
                        'change': float(quote.get('09. change', 0)),
                        'change_percent': quote.get('10. change percent', '0%').replace('%', ''),
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
                else:
                    quotes[ticker] = {'price': 0, 'change': 0, 'change_percent': 0, 'timestamp': 'N/A'}
                
            except Exception as e:
                logger.warning(f"Failed to fetch quote for {ticker}: {e}")
                quotes[ticker] = {'price': 0, 'change': 0, 'change_percent': 0, 'timestamp': 'N/A'}
        
        return quotes
    
    def fetch_news(self, tickers: List[str], limit: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch news from Alpha Vantage."""
        news = {}
        
        for ticker in tickers:
            try:
                params = {
                    'function': 'NEWS_SENTIMENT',
                    'tickers': ticker,
                    'limit': limit,
                    'apikey': self.api_key
                }
                
                response = self.session.get(self.base_url, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                news[ticker] = []
                
                if 'feed' in data:
                    for article in data['feed'][:limit]:
                        news[ticker].append({
                            'headline': article.get('title', 'N/A'),
                            'source': article.get('source', 'N/A'),
                            'published': article.get('time_published', 'N/A'),
                            'url': article.get('url', 'N/A')
                        })
                
            except Exception as e:
                logger.warning(f"Failed to fetch news for {ticker}: {e}")
                news[ticker] = []
        
        return news


def main():
    """Main function to run the investment planner."""
    parser = argparse.ArgumentParser(description='Bi-Weekly Investment Planner')
    parser.add_argument('--contribution', type=float, default=1000.0,
                       help='Bi-weekly contribution amount (default: 1000)')
    parser.add_argument('--provider', choices=['finnhub', 'polygon', 'alpha'], 
                       default='finnhub', help='API provider (default: finnhub)')
    parser.add_argument('--news-per-ticker', type=int, default=3,
                       help='Number of news articles per ticker (default: 3)')
    parser.add_argument('--config', type=str, help='Configuration file path (JSON or YAML)')
    parser.add_argument('--output', type=str, default='InvestmentPlan.xlsx',
                       help='Output Excel filename (default: InvestmentPlan.xlsx)')
    
    args = parser.parse_args()
    
    try:
        # Initialize planner
        planner = InvestmentPlanner(
            contribution=args.contribution,
            provider=args.provider,
            news_per_ticker=args.news_per_ticker,
            config_file=args.config
        )
        
        logger.info(f"Starting investment planner with {args.provider} provider")
        logger.info(f"Bi-weekly contribution: ${args.contribution:,.2f}")
        
        # Fetch market data
        planner.fetch_market_data()
        
        # Create Excel workbook
        output_file = planner.create_excel_workbook(args.output)
        
        logger.info(f"Investment plan completed successfully!")
        logger.info(f"Output file: {output_file}")
        logger.info(f"Provider used: {args.provider}")
        logger.info(f"Quotes fetched: {len(planner.quotes)}")
        logger.info(f"News articles fetched: {sum(len(articles) for articles in planner.news.values())}")
        
    except Exception as e:
        logger.error(f"Error running investment planner: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
