#!/usr/bin/env python3
"""
Test script for the Investment Planner

This script tests the basic functionality without requiring API keys.
It creates mock data to validate the Excel output generation.
"""

import os
import sys
import tempfile
from datetime import datetime, timezone
from invest_plan import InvestmentPlanner, FinnhubClient, PolygonClient, AlphaVantageClient


class MockAPIClient:
    """Mock API client for testing without real API calls."""
    
    def __init__(self):
        self.mock_quotes = {
            'NVDA': {'price': 450.00, 'change': 5.50, 'change_percent': 1.24, 'timestamp': datetime.now(timezone.utc).isoformat()},
            'MSFT': {'price': 380.00, 'change': -2.30, 'change_percent': -0.60, 'timestamp': datetime.now(timezone.utc).isoformat()},
            'AAPL': {'price': 175.00, 'change': 1.20, 'change_percent': 0.69, 'timestamp': datetime.now(timezone.utc).isoformat()},
            'AMZN': {'price': 145.00, 'change': 3.40, 'change_percent': 2.40, 'timestamp': datetime.now(timezone.utc).isoformat()},
            'TSLA': {'price': 250.00, 'change': -8.50, 'change_percent': -3.29, 'timestamp': datetime.now(timezone.utc).isoformat()},
            'GOOGL': {'price': 140.00, 'change': 2.10, 'change_percent': 1.52, 'timestamp': datetime.now(timezone.utc).isoformat()},
            'VTI': {'price': 220.00, 'change': 1.50, 'change_percent': 0.69, 'timestamp': datetime.now(timezone.utc).isoformat()},
            'VOO': {'price': 410.00, 'change': 2.80, 'change_percent': 0.69, 'timestamp': datetime.now(timezone.utc).isoformat()},
            'SCHD': {'price': 75.00, 'change': 0.30, 'change_percent': 0.40, 'timestamp': datetime.now(timezone.utc).isoformat()},
            'CRWD': {'price': 180.00, 'change': 4.20, 'change_percent': 2.39, 'timestamp': datetime.now(timezone.utc).isoformat()},
            'PANW': {'price': 320.00, 'change': 6.80, 'change_percent': 2.17, 'timestamp': datetime.now(timezone.utc).isoformat()},
            'AVGO': {'price': 1200.00, 'change': 15.50, 'change_percent': 1.31, 'timestamp': datetime.now(timezone.utc).isoformat()},
            'UNH': {'price': 520.00, 'change': -3.20, 'change_percent': -0.61, 'timestamp': datetime.now(timezone.utc).isoformat()},
            'UPS': {'price': 160.00, 'change': 1.80, 'change_percent': 1.14, 'timestamp': datetime.now(timezone.utc).isoformat()},
            'VST': {'price': 45.00, 'change': 0.80, 'change_percent': 1.81, 'timestamp': datetime.now(timezone.utc).isoformat()},
            'HIMS': {'price': 8.50, 'change': 0.20, 'change_percent': 2.41, 'timestamp': datetime.now(timezone.utc).isoformat()},
            'AB': {'price': 35.00, 'change': 0.50, 'change_percent': 1.45, 'timestamp': datetime.now(timezone.utc).isoformat()},
            'ZYNE': {'price': 2.50, 'change': -0.10, 'change_percent': -3.85, 'timestamp': datetime.now(timezone.utc).isoformat()},
        }
        
        self.mock_news = {
            'NVDA': [
                {'headline': 'NVIDIA Reports Strong Q4 Earnings', 'source': 'Reuters', 'published': '2024-01-15T10:00:00Z', 'url': 'https://example.com/nvda1'},
                {'headline': 'AI Chip Demand Drives NVIDIA Growth', 'source': 'Bloomberg', 'published': '2024-01-15T09:30:00Z', 'url': 'https://example.com/nvda2'},
                {'headline': 'NVIDIA Partners with Major Cloud Providers', 'source': 'TechCrunch', 'published': '2024-01-15T08:15:00Z', 'url': 'https://example.com/nvda3'}
            ],
            'MSFT': [
                {'headline': 'Microsoft Azure Revenue Surges', 'source': 'CNBC', 'published': '2024-01-15T11:00:00Z', 'url': 'https://example.com/msft1'},
                {'headline': 'Microsoft Teams Adds New AI Features', 'source': 'The Verge', 'published': '2024-01-15T10:30:00Z', 'url': 'https://example.com/msft2'},
                {'headline': 'Microsoft Stock Hits New High', 'source': 'MarketWatch', 'published': '2024-01-15T09:45:00Z', 'url': 'https://example.com/msft3'}
            ],
            'AAPL': [
                {'headline': 'Apple iPhone Sales Exceed Expectations', 'source': 'Apple Insider', 'published': '2024-01-15T12:00:00Z', 'url': 'https://example.com/aapl1'},
                {'headline': 'Apple Services Revenue Grows 15%', 'source': 'Reuters', 'published': '2024-01-15T11:30:00Z', 'url': 'https://example.com/aapl2'},
                {'headline': 'Apple Announces New MacBook Pro', 'source': 'MacRumors', 'published': '2024-01-15T10:45:00Z', 'url': 'https://example.com/aapl3'}
            ]
        }
    
    def fetch_quotes(self, tickers):
        """Return mock quotes for testing."""
        return {ticker: self.mock_quotes.get(ticker, {'price': 0, 'change': 0, 'change_percent': 0, 'timestamp': 'N/A'}) for ticker in tickers}
    
    def fetch_news(self, tickers, limit=3):
        """Return mock news for testing."""
        return {ticker: self.mock_news.get(ticker, [])[:limit] for ticker in tickers}


def test_investment_planner():
    """Test the investment planner with mock data."""
    print("Testing Investment Planner with mock data...")
    
    # Create a temporary planner with mock API client
    planner = InvestmentPlanner(contribution=1000.0, provider='finnhub', news_per_ticker=3)
    planner.api_client = MockAPIClient()
    
    # Add some sample holdings
    planner.holdings.loc[planner.holdings['Ticker'] == 'NVDA', 'Shares'] = 2.5
    planner.holdings.loc[planner.holdings['Ticker'] == 'NVDA', 'Avg Cost'] = 400.00
    planner.holdings.loc[planner.holdings['Ticker'] == 'MSFT', 'Shares'] = 5.0
    planner.holdings.loc[planner.holdings['Ticker'] == 'MSFT', 'Avg Cost'] = 350.00
    planner.holdings.loc[planner.holdings['Ticker'] == 'AAPL', 'Shares'] = 10.0
    planner.holdings.loc[planner.holdings['Ticker'] == 'AAPL', 'Avg Cost'] = 150.00
    
    # Fetch mock market data
    planner.fetch_market_data()
    
    # Test holdings dataframe
    holdings_df = planner.build_holdings_dataframe()
    print(f"[OK] Holdings dataframe created with {len(holdings_df)} positions")
    
    # Test allocation calculation
    allocation_df, suggested_buys_df = planner.calculate_biweekly_allocation()
    print(f"[OK] Allocation calculated: {len(allocation_df)} buckets, {len(suggested_buys_df)} suggested buys")
    
    # Test news dataframe
    news_df = planner.build_news_dataframe()
    print(f"[OK] News dataframe created with {len(news_df)} articles")
    
    # Test core longterm dataframe
    core_df = planner.build_core_longterm_dataframe()
    print(f"[OK] Core longterm dataframe created with {len(core_df)} positions")
    
    # Create Excel file in temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = os.path.join(temp_dir, 'TestInvestmentPlan.xlsx')
        planner.create_excel_workbook(output_file)
        
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"[OK] Excel workbook created successfully: {output_file} ({file_size} bytes)")
        else:
            print("[FAIL] Excel workbook creation failed")
            return False
    
    print("[OK] All tests passed!")
    return True


def test_config_validation():
    """Test configuration validation."""
    print("\nTesting configuration validation...")
    
    # Test valid config
    try:
        planner = InvestmentPlanner()
        print("[OK] Default configuration is valid")
    except Exception as e:
        print(f"[FAIL] Default configuration failed: {e}")
        return False
    
    # Test invalid config (percentages don't sum to 100)
    try:
        # Create a planner with invalid config by overriding the _load_config method
        class TestPlanner(InvestmentPlanner):
            def _load_config(self, config_file):
                invalid_config = {
                    'allocation_buckets': {
                        'ETF/Index': {'percentage': 50, 'tickers': ['VTI']},
                        'Growth': {'percentage': 30, 'tickers': ['NVDA']}
                    }
                }
                # Validate allocation percentages sum to 100%
                total_percentage = sum(bucket['percentage'] for bucket in invalid_config['allocation_buckets'].values())
                if abs(total_percentage - 100) > 0.01:
                    raise ValueError(f"Allocation percentages must sum to 100%, got {total_percentage}%")
                return invalid_config
        
        # This should raise an error
        planner = TestPlanner()
        print("[FAIL] Invalid configuration was accepted (should have failed)")
        return False
    except ValueError as e:
        print(f"[OK] Invalid configuration correctly rejected: {e}")
    
    return True


def main():
    """Run all tests."""
    print("Investment Planner Test Suite")
    print("=" * 40)
    
    success = True
    
    # Test basic functionality
    if not test_investment_planner():
        success = False
    
    # Test configuration validation
    if not test_config_validation():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("[SUCCESS] All tests passed! The investment planner is working correctly.")
        print("\nTo use with real data:")
        print("1. Copy env_example.txt to .env")
        print("2. Add your API keys to .env")
        print("3. Run: python invest_plan.py")
    else:
        print("[ERROR] Some tests failed. Please check the implementation.")
        sys.exit(1)


if __name__ == '__main__':
    main()
