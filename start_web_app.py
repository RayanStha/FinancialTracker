#!/usr/bin/env python3
"""
Startup script for the Investment Planner Web Application
"""

import os
import sys
import webbrowser
import time
import threading
from app import app

def open_browser():
    """Open the web browser after a short delay."""
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')

def main():
    """Main function to start the web application."""
    print("=" * 60)
    print("Investment Planner Web Application")
    print("=" * 60)
    print()
    print("Starting web server...")
    print("The application will be available at: http://localhost:5000")
    print()
    print("Features:")
    print("• Dashboard with portfolio overview")
    print("• Portfolio management (add/edit holdings)")
    print("• Allocation controls (adjust contributions)")
    print("• Stock research with real-time data")
    print("• Excel export functionality")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    # Open browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        # Start the Flask app
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\nShutting down web server...")
        print("Thank you for using Investment Planner!")
        sys.exit(0)

if __name__ == '__main__':
    main()
