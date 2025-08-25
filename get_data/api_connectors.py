from pydantic_core import Url
import requests
from dotenv import load_dotenv
import os

load_dotenv()

url=os.getenv("HOUDUAN_URL")
production_url=url+"/api/ads-ai-production"
procurement_url=url+"/api/ads-ai-procurement"
sales_url=url+"/api/ads-ai-sales"
def get_ads_ai_production():
    production = requests.get(production_url)
    return production.json()

def get_ads_ai_procurement():
    procurement = requests.get(procurement_url)
    return procurement.json()

def get_ads_ai_sales():
    sales = requests.get(sales_url)
    return sales.json()

if __name__ == '__main__':
    production = get_ads_ai_production()
    procurement = get_ads_ai_procurement()
    sales = get_ads_ai_sales()
    print(sales)