#!/usr/bin/env python3
"""
Investment Planner Web Application

A Flask web interface for the bi-weekly investment planner.
Provides portfolio management, allocation controls, and stock research capabilities.
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from werkzeug.utils import secure_filename
import tempfile
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from invest_plan import InvestmentPlanner

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# Global planner instance
planner = None

def get_planner():
    """Get or create the investment planner instance."""
    global planner
    if planner is None:
        try:
            planner = InvestmentPlanner()
            planner.fetch_market_data()
        except Exception as e:
            logger.error(f"Failed to initialize planner: {e}")
            flash(f"Error initializing planner: {e}", "error")
            return None
    return planner

@app.route('/')
def dashboard():
    """Main dashboard page."""
    planner_instance = get_planner()
    if not planner_instance:
        return render_template('error.html', error="Failed to initialize investment planner")
    
    try:
        # Get portfolio data
        holdings_df = planner_instance.build_holdings_dataframe()
        allocation_df, suggested_buys_df = planner_instance.calculate_biweekly_allocation()
        
        # Calculate portfolio summary
        total_market_value = holdings_df['Market Value'].sum()
        total_cost_basis = holdings_df['Cost Basis'].sum()
        total_gain_loss = total_market_value - total_cost_basis
        total_gain_loss_pct = (total_gain_loss / total_cost_basis * 100) if total_cost_basis > 0 else 0
        
        # Get top performers
        top_performers = holdings_df.nlargest(3, 'Gain/Loss %')
        
        return render_template('dashboard.html',
                             holdings=holdings_df.to_dict('records'),
                             allocation=allocation_df.to_dict('records'),
                             suggested_buys=suggested_buys_df.to_dict('records'),
                             portfolio_summary={
                                 'total_market_value': total_market_value,
                                 'total_cost_basis': total_cost_basis,
                                 'total_gain_loss': total_gain_loss,
                                 'total_gain_loss_pct': total_gain_loss_pct,
                                 'contribution': planner_instance.contribution
                             },
                             top_performers=top_performers.to_dict('records'),
                             provider=planner_instance.provider)
    
    except Exception as e:
        logger.error(f"Error in dashboard: {e}")
        return render_template('error.html', error=str(e))

@app.route('/portfolio')
def portfolio():
    """Portfolio management page."""
    planner_instance = get_planner()
    if not planner_instance:
        return render_template('error.html', error="Failed to initialize investment planner")
    
    try:
        holdings_df = planner_instance.build_holdings_dataframe()
        return render_template('portfolio.html', holdings=holdings_df.to_dict('records'))
    except Exception as e:
        logger.error(f"Error in portfolio: {e}")
        return render_template('error.html', error=str(e))

@app.route('/allocation')
def allocation():
    """Allocation management page."""
    planner_instance = get_planner()
    if not planner_instance:
        return render_template('error.html', error="Failed to initialize investment planner")
    
    try:
        allocation_df, suggested_buys_df = planner_instance.calculate_biweekly_allocation()
        return render_template('allocation.html',
                             allocation=allocation_df.to_dict('records'),
                             suggested_buys=suggested_buys_df.to_dict('records'),
                             contribution=planner_instance.contribution,
                             buckets=planner_instance.config['allocation_buckets'])
    except Exception as e:
        logger.error(f"Error in allocation: {e}")
        return render_template('error.html', error=str(e))

@app.route('/research')
def research():
    """Stock research page."""
    planner_instance = get_planner()
    if not planner_instance:
        return render_template('error.html', error="Failed to initialize investment planner")
    
    try:
        # Get news data for portfolio holdings
        news_df = planner_instance.build_news_dataframe()
        quotes = planner_instance.quotes
        
        return render_template('research.html',
                             news=news_df.to_dict('records'),
                             quotes=quotes,
                             holdings=planner_instance.holdings['Ticker'].tolist())
    except Exception as e:
        logger.error(f"Error in research: {e}")
        return render_template('error.html', error=str(e))


@app.route('/api/stock_info/<ticker>')
def get_stock_info(ticker):
    """API endpoint to get detailed stock information."""
    planner_instance = get_planner()
    if not planner_instance:
        return jsonify({'error': 'Planner not initialized'}), 500
    
    try:
        # Fetch fresh data for the specific ticker
        quotes = planner_instance.api_client.fetch_quotes([ticker.upper()])
        news = planner_instance.api_client.fetch_news([ticker.upper()], 5)
        
        return jsonify({
            'ticker': ticker.upper(),
            'quote': quotes.get(ticker.upper(), {}),
            'news': news.get(ticker.upper(), [])
        })
    except Exception as e:
        logger.error(f"Error fetching stock info for {ticker}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/update_contribution', methods=['POST'])
def update_contribution():
    """Update the bi-weekly contribution amount."""
    planner_instance = get_planner()
    if not planner_instance:
        return jsonify({'error': 'Planner not initialized'}), 500
    
    try:
        data = request.get_json()
        new_contribution = float(data.get('contribution', 1000))
        
        if new_contribution <= 0:
            return jsonify({'error': 'Contribution must be positive'}), 400
        
        planner_instance.contribution = new_contribution
        flash(f'Contribution updated to ${new_contribution:,.2f}', 'success')
        
        return jsonify({'success': True, 'contribution': new_contribution})
    except Exception as e:
        logger.error(f"Error updating contribution: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/update_holding', methods=['POST'])
def update_holding():
    """Update a holding's shares or average cost."""
    planner_instance = get_planner()
    if not planner_instance:
        return jsonify({'error': 'Planner not initialized'}), 500
    
    try:
        data = request.get_json()
        ticker = data.get('ticker', '').upper()
        shares = float(data.get('shares', 0))
        avg_cost = float(data.get('avg_cost', 0))
        
        # Update the holding
        mask = planner_instance.holdings['Ticker'] == ticker
        if mask.any():
            planner_instance.holdings.loc[mask, 'Shares'] = shares
            planner_instance.holdings.loc[mask, 'Avg Cost'] = avg_cost
            flash(f'Updated {ticker}: {shares} shares at ${avg_cost:.2f} average cost', 'success')
            return jsonify({'success': True})
        else:
            return jsonify({'error': f'Ticker {ticker} not found'}), 404
    
    except Exception as e:
        logger.error(f"Error updating holding: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_holding', methods=['POST'])
def add_holding():
    """Add a new holding to the portfolio."""
    planner_instance = get_planner()
    if not planner_instance:
        return jsonify({'error': 'Planner not initialized'}), 500
    
    try:
        data = request.get_json()
        ticker = data.get('ticker', '').upper()
        company_name = data.get('company_name', '')
        shares = float(data.get('shares', 0))
        avg_cost = float(data.get('avg_cost', 0))
        category = data.get('category', 'Growth')
        
        # Check if ticker already exists
        if ticker in planner_instance.holdings['Ticker'].values:
            return jsonify({'error': f'Ticker {ticker} already exists'}), 400
        
        # Add new holding
        new_holding = {
            'Ticker': ticker,
            'Company Name': company_name,
            'Shares': shares,
            'Avg Cost': avg_cost,
            'Category': category
        }
        
        planner_instance.holdings = planner_instance.holdings.append(new_holding, ignore_index=True)
        
        # Fetch quote for the new ticker
        try:
            quotes = planner_instance.api_client.fetch_quotes([ticker])
            planner_instance.quotes.update(quotes)
        except Exception as e:
            logger.warning(f"Failed to fetch quote for {ticker}: {e}")
        
        flash(f'Added {ticker} to portfolio', 'success')
        return jsonify({'success': True})
    
    except Exception as e:
        logger.error(f"Error adding holding: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export_excel')
def export_excel():
    """Export the current portfolio to Excel."""
    planner_instance = get_planner()
    if not planner_instance:
        return jsonify({'error': 'Planner not initialized'}), 500
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            filename = tmp_file.name
        
        # Generate Excel file
        planner_instance.create_excel_workbook(filename)
        
        return send_file(filename, as_attachment=True, 
                        download_name=f'InvestmentPlan_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
    
    except Exception as e:
        logger.error(f"Error exporting Excel: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh_data')
def refresh_data():
    """Refresh market data."""
    planner_instance = get_planner()
    if not planner_instance:
        return jsonify({'error': 'Planner not initialized'}), 500
    
    try:
        planner_instance.fetch_market_data()
        flash('Market data refreshed successfully', 'success')
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error refreshing data: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
