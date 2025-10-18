# Investment Planner Web Application

A modern, user-friendly web interface for your bi-weekly investment planner. This web application provides an intuitive way to manage your portfolio, adjust allocations, and research stocks with real-time data.

## 🌟 Features

### 📊 Dashboard
- **Portfolio Overview**: Total market value, cost basis, and performance metrics
- **Bi-Weekly Plan Summary**: Quick view of your investment allocation
- **Top Performers**: Best performing stocks in your portfolio
- **Real-time Data**: Live market data with automatic refresh

### 💼 Portfolio Management
- **Add Holdings**: Easily add new stocks to your portfolio
- **Edit Holdings**: Update shares and average cost for existing positions
- **Performance Tracking**: Real-time gain/loss calculations
- **Category Management**: Organize holdings by investment type

### 📈 Allocation Controls
- **Contribution Adjustment**: Change your bi-weekly contribution amount
- **Bucket Visualization**: See how your money is allocated across investment categories
- **Suggested Buys**: Detailed purchase recommendations with fractional shares
- **Allocation Validation**: Ensures percentages always sum to 100%

### 🔍 Stock Research
- **Stock Search**: Look up any ticker symbol for real-time data
- **News Integration**: Latest headlines and news articles
- **Portfolio News**: News specific to your holdings
- **Price Tracking**: Current prices with daily changes

### 📥 Export & Data
- **Excel Export**: Download comprehensive Excel reports
- **Data Refresh**: Manual and automatic data updates
- **API Integration**: Multiple data providers (Finnhub, Polygon, Alpha Vantage)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys
Copy `env_example.txt` to `.env` and add your API keys:
```bash
cp env_example.txt .env
```

Edit `.env` and add your API keys:
```
FINNHUB_API_KEY=your_finnhub_api_key_here
POLYGON_API_KEY=your_polygon_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here
```

### 3. Start the Web Application
```bash
python start_web_app.py
```

The application will automatically open in your browser at `http://localhost:5000`

## 🖥️ Web Interface Guide

### Navigation
- **Dashboard**: Main overview with key metrics and quick actions
- **Portfolio**: Manage your holdings (add, edit, view performance)
- **Allocation**: Adjust contribution amounts and view suggested buys
- **Research**: Search stocks and view news

### Key Actions

#### Adding a New Holding
1. Go to **Portfolio** page
2. Click **"Add Holding"** button
3. Fill in ticker, company name, shares, and average cost
4. Select appropriate category
5. Click **"Add Holding"**

#### Adjusting Contribution Amount
1. Go to **Dashboard** or **Allocation** page
2. Click **"Edit Contribution Amount"**
3. Enter new bi-weekly contribution
4. Click **"Update"**

#### Researching a Stock
1. Go to **Research** page
2. Enter ticker symbol in search box
3. Click **"Search"** or press Enter
4. View real-time quote and recent news

#### Exporting to Excel
1. Click **"Export Excel"** button (available on all pages)
2. File will download automatically
3. Contains all 5 sheets: Dashboard, Portfolio, Allocation, Research, Strategy

## 🔧 Configuration

### Customizing Allocations
Edit `config.json` to modify:
- Allocation percentages
- Ticker assignments to buckets
- Long-term strategy targets

Example:
```json
{
  "allocation_buckets": {
    "ETF/Index": {
      "percentage": 40,
      "tickers": ["VTI", "VOO", "SCHD", "QQQ"]
    },
    "Growth": {
      "percentage": 35,
      "tickers": ["NVDA", "CRWD", "PANW", "GOOGL", "AMZN", "TSLA"]
    }
  }
}
```

### API Provider Selection
The web app uses the same API provider as configured in your environment. To change:
1. Update your `.env` file with different API keys
2. Restart the web application

## 📱 Responsive Design

The web application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- All modern web browsers

## 🔒 Security Features

- Input validation on all forms
- SQL injection protection
- XSS prevention
- Secure API key handling
- Error handling and logging

## 🛠️ Technical Details

### Built With
- **Backend**: Flask (Python)
- **Frontend**: Bootstrap 5, jQuery, DataTables
- **APIs**: Finnhub, Polygon.io, Alpha Vantage
- **Data**: Pandas, xlsxwriter

### Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Performance
- Automatic data refresh every 5 minutes
- Efficient API calls with caching
- Responsive loading states
- Error handling and recovery

## 🐛 Troubleshooting

### Common Issues

#### "Failed to initialize planner"
- Check your `.env` file has valid API keys
- Ensure at least one API provider is configured
- Verify internet connection

#### "No data available"
- Click "Refresh Data" button
- Check API key limits (free tiers have restrictions)
- Verify ticker symbols are correct

#### "Port not available"
- Make sure port 5000 is not in use
- Try running: `python app.py --port 5001`
- Check firewall settings

### Getting Help

1. Check the console logs for error messages
2. Verify your API keys are working
3. Ensure all dependencies are installed
4. Check the command line interface still works: `python invest_plan.py`

## 🔄 Updates and Maintenance

### Regular Tasks
- Update API keys when they expire
- Refresh market data regularly
- Review and adjust allocations quarterly
- Export Excel reports for record keeping

### Data Backup
- Excel exports serve as data backups
- Portfolio data is stored in memory (restart to reset)
- Consider saving Excel files regularly

## 🚀 Advanced Usage

### Command Line + Web Interface
You can use both interfaces:
- **Command Line**: For batch processing and automation
- **Web Interface**: For interactive management and research

### API Endpoints
The web app exposes several API endpoints:
- `/api/stock_info/<ticker>` - Get stock information
- `/api/update_contribution` - Update contribution amount
- `/api/add_holding` - Add new holding
- `/api/update_holding` - Update existing holding
- `/api/export_excel` - Export Excel file
- `/api/refresh_data` - Refresh market data

### Customization
- Modify templates in `templates/` directory
- Update styles in `static/style.css`
- Add JavaScript functionality in `static/script.js`
- Extend Flask routes in `app.py`

## 📈 Future Enhancements

Planned features:
- User authentication and multiple portfolios
- Historical performance tracking
- Advanced charting and analytics
- Mobile app version
- Email notifications
- Social features and sharing

## 📄 License

This project is open source and available under the MIT License.

---

**Happy Investing! 📈💰**
