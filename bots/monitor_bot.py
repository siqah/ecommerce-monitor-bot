from bots.scraper_bot import ProductScraperBot
import json
from datetime import date, datetime, time, timedelta 
from typing import List, Dict 
import smtplib 
from email.mime.text import MIMEText 
from email.mime.multipart import MIMEMultipart 
import os
from dotenv import load_dotenv

load_dotenv()

class PriceMonitorBot(ProductScraperBot):
    def __init__(self, config=None):
        super().__init__(config)
        self.price_history = {}
        self.alerts = []

    def load_tracking_list(self, filename: str = "tracking_list.json") -> List[Dict]:
        tracking_file = self.data_dir / filename 

        if tracking_file.exists():
            with open(tracking_file, 'r') as f:
                return json.load(f)
            

        #Default tracking list
        default_list = [
            {
                "name": "Sample Product",
                "url": "https://example.com/product",
                "selectors": {
                    "name": "h1",
                    "price": ".price",
                    "availability": ".stock"
                },
                "target_price": 100.0,
                "alert_email": "user@example.com"
            }
        ]
        with open(tracking_file, 'w') as f:
            json.dump(default_list, f, indent=4)

        return default_list

    def monitor_prices(self, interval_minutes: int = 60, max_cycles: int = 24):
        print(f"Starting price monitoring... {interval_minutes}-minute intervals for {max_cycles} cycles.")

        product_to_track = self.load_tracking_list()

        for cycle in range(max_cycles):
            print(f"Cycle {cycle + 1}/{max_cycles} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            for product_info in product_to_track:
                #scrape current price
                try:
                    product_data = self.scrape_product_page(
                        product_info["url"],
                        product_info["selector"]
                    )

                    if product_data and product_data.get("pice"):
                        self._update_price_history(
                            product_info,
                            product_data
                        )
                        self._check_price_alert(
                            product_info,
                            product_data
                        )
                except Exception as e:
                    print(f"Error monitoring {product_info.get('name', 'unknown')}: {e}")

            print(f"Waiting {interval_minutes} minutes before next cycle...")
           
            time.sleep(interval_minutes * 60)

        print("Monitoring completed.")    

    def _update_price_history(self, product_info: Dict, product_data: Dict):
        product_id = product_info["url"]

        if product_id not in self.price_history:
            self.price_history[product_id] = []

        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "price": product_data["price"],
            "name": product_data.get("name", product_info.get("name", "unknown"))
        }

        self.price_history[product_id].append(history_entry)

        #keep only last 100 entries
        if len(self.price_history[product_id]) > 100:
            self.price_history[product_id] = self.price_history[product_id][-100:]
        
        #save history
        self.save_data(self.price_history, "price_history.json")


    def _check_price_alerts(self, product_info: Dict, product_data: Dict):
        target_price = product_info.get("target_price")
        current_price = product_data.get("price")

        if current_price and target_price and current_price <= target_price:
            alert = {
                "product": product_info.get("name", "unknown"),
                "Current Price": current_price,
                "target_price": target_price,
                "url": product_info["url"],
                "timestamp": datetime.now().isoformat(),
                "sceenshot": f"product_{product_data.get('name', 'product').replace(' ', '_')[:50]}_{int(time.time())}.png"
            }
            self.alerts.append(alert)
            print(f"Price alert triggered for {alert['product']} at ${current_price}")

            #send email alert
            if product_info.get("alert_email"):
                self._send_alert_email(product_info["alert_email"], alert) 


    def _send_alert_email(self, to_email: str, alert: Dict):
        #send price alert email
        try:
            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", 587))
            smtp_user = os.getenv("SMTP_USER")
            smtp_password = os.getenv("SMTP_PASSWORD")

            if not all([smtp_server, smtp_user, smtp_password]):
                print("EMAIL  configuration missing. set SMTP_* environment variables.")
                return
            
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = to_email
            msg['Subject'] = f"Price Alert for {alert['product']}"

            body = f""" 
            PRICE DROP ALERT!

            product: {alert['product']}
            Current Price: ${alert['current_price']}
            Your Target : ${alert['target_price']}

            Buy now: {alert['url']}
            
            Alert Time: {alert['timestamp']}

            """
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            print(f"Alert email sent to {to_email} for {alert['product']}")
        except Exception as e:
            print(f"Failed to send alert email to {to_email}: {e}")



            print(f"Alert email sent to {to_email} for {alert['product']}")
        except Exception as e:
            print(f"Failed to send alert email to {to_email}: {e}")