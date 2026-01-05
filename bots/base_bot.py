from playwright.sync_api import sync_playwright
import time 
import json
import os
from pathlib import Path 
from dataclasses import dataclass 
from typing import Optional, Dict, List,Any
import random 

@dataclass
class BotConfig:
    headless: bool = False
    slow_mo: int = 100 
    viewport: Dict[str, int] = None 
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    timeout: int = 30000 

    def __post_init__(self):
        if self.viewport is None:
            self.viewport = {"width": 1280, "height": 720}

class BaseBot:
    def __init__(self, config: BotConfig):
        self.config = config or BotConfig()
        self.playwright = None
        self.browser = None
        self.context = None 
        self.page = None 
        self.screenshots_dir = Path("screenshots")
        self.data_dir = Path("data")
        self._setup_directories()

    def _setup_directories(self):
        self.screenshots_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)


    def start(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwrright.chromium.launch(
            headless=self.config.headless,
            slow_mo=self.config.slow_mo
        )
        self.page = self.context.new_page()
        self.page.set_default_timeout(self.config.timeout)
        print("Bot initialized successfully")
        return self
    
    def navigate(self, url: str):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.page.goto(url, wait_until="networkidle")
                if response and response.ok:
                    print(f"Navigated to {url}")
                    return True
            except Exception as e:
                print(f"navigation to {url} failed on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
        print(f"Failed to navigate to {url}")
        return False    
    
    def take_screenshot(self, name: str = "screenshot", full_page: bool = True ):
        #take screenshot
        filename = self.screenshots_dir / f"{name}_{int(time.time())}.png"
        self.page.screenshot(path=str(filename), full_page=full_page)
        print(f"Screenshot saved to {filename}")
        return filename
    
    def wait_random(self, min_seconds: float = 1, max_seconds: float = 3):
        time.sleep(random.uniform(min_seconds, max_seconds))
       
    def scroll_page(self, scroll_pixels: int = 500):
        self.page.evaluate(f"windows.scrollBy(0, {scroll_pixels})")
        self.wait_random(0.5, 1.5)

    def save_data(self, data:any, filename:str):
        # Save data as JSON
        filepath = self.data_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Data saved to {filepath}")

    def load_data(self, filename:str) -> Any:
        filepath = self.data_dir / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("Bot closed successfully")

    def __enter__(self):
        return self.start()
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()