import json
from pydoc import text
from typing import Any
from pathlib import Path


def load_json_file(filepath: Path) -> Any:
    path = Path(filepath)
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_json_file(data: Any, filepath: str):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def format_price(price: float) -> str:
    """Format price as currency"""
    return f"${price:.2f}"

def clean_text(text: str) -> str:
    if not text:
        return ""
    return ''.join(text.split())


def generate_report(products: list) -> str:
    """Generate a text report from product data"""
    report = []
    report.append("=" * 50)
    report.append("E-COMMERCE MONITORING REPORT")
    report.append("=" * 50)
    
    for i, product in enumerate(products, 1):
        report.append(f"\n{i}. {product.get('name', 'Unknown Product')}")
        report.append(f"   Price: ${product.get('price', 'N/A')}")
        report.append(f"   Available: {'Yes' if product.get('availability') else 'No'}")
        report.append(f"   URL: {product.get('url', 'N/A')}")
    
    report.append(f"\n{'=' * 50}")
    report.append(f"Total Products: {len(products)}")
    report.append(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return '\n'.join(report)
