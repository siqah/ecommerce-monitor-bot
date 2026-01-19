#!/usr/bin/env python3
"""
E-commerce Price Monitoring Bot
Usage: python main.py [command] [options]
"""

import sys
import argparse
from bots.monitor_bot import PriceMonitorBot
from bots.base_bot import BotConfig
from config.settings import Settings

def demo_scraping():
    """Demo: Scrape sample product data"""
    print("🛒 Demo: Scraping Amazon product page (example)")
    
    config = BotConfig(
        headless=False,  # Set to True for production
        slow_mo=150
    )
    
    with PriceMonitorBot(config) as bot:
        # Example selectors for Amazon
        selectors = {
            "name": "#productTitle",
            "price": ".a-price-whole",
            "availability": "#availability span",
            "rating": ".a-icon-alt"
        }
        
        # Demo URL (replace with actual product URL)
        url = "https://www.amazon.com/dp/B08N5WRWNW"
        
        try:
            product = bot.scrape_product_page(url, selectors)
            if product:
                print("\n📊 Product Details:")
                for key, value in product.items():
                    if value:
                        print(f"   {key}: {value}")
                
                # Save data
                bot.save_data([product], "demo_product.json")
                print(f"\n💾 Data saved to data/demo_product.json")
        
        except Exception as e:
            print(f"❌ Error: {e}")

def start_monitoring():
    """Start price monitoring"""
    print("🔍 Starting Price Monitor...")
    
    config = BotConfig(
        headless=True,  # Headless for monitoring
        slow_mo=50
    )
    
    monitor = PriceMonitorBot(config)
    
    try:
        monitor.start()
        monitor.monitor_prices(
            interval_minutes=Settings.CHECK_INTERVAL_MINUTES,
            max_cycles=Settings.MAX_MONITOR_CYCLES
        )
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped by user")
    finally:
        monitor.close()

def create_tracking_list():
    """Create a sample tracking list"""
    from utils.helpers import save_json_file
    
    sample_list = [
        {
            "name": "Wireless Earbuds",
            "url": "https://www.amazon.com/dp/B08N5WRWNW",
            "selectors": {
                "name": "#productTitle",
                "price": ".a-price-whole",
                "availability": "#availability span"
            },
            "target_price": 100.0,
            "alert_email": "your-email@example.com"
        },
        {
            "name": "Gaming Mouse",
            "url": "https://www.amazon.com/dp/B07S5QWM6L",
            "selectors": {
                "name": "#productTitle",
                "price": ".a-price-whole",
                "availability": "#availability span"
            },
            "target_price": 50.0,
            "alert_email": "your-email@example.com"
        }
    ]
    
    save_json_file(sample_list, "data/tracking_list.json")
    print("✅ Sample tracking list created: data/tracking_list.json")
    print("⚠️ Remember to update URLs and selectors for actual products!")

def main():
    parser = argparse.ArgumentParser(description="E-commerce Price Monitoring Bot")
    parser.add_argument("command", choices=["demo", "monitor", "setup"], 
                       help="Command to run")
    parser.add_argument("--headless", action="store_true", 
                       help="Run browser in headless mode")
    
    args = parser.parse_args()
    
    # Setup directories
    Settings.setup_directories()
    
    if args.command == "demo":
        demo_scraping()
    elif args.command == "monitor":
        start_monitoring()
    elif args.command == "setup":
        create_tracking_list()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()