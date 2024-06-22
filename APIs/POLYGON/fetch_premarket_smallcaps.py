import os
import requests
import pandas as pd
from datetime import datetime

# Constants
API_KEY = os.getenv('POLYGON_TOKEN')
if API_KEY is None:
    raise ValueError("No API key provided. Please set the POLYGON_API_KEY environment variable.")

PREMARKET_ENDPOINT = 'https://api.polygon.io/v2/aggs/ticker/{ticker}/prev?adjusted=true&apiKey=' + API_KEY
SMALLCAP_THRESHOLD = 2_000_000_000  # Market cap in USD (2 billion)

def get_smallcap_tickers():
    url = 'https://api.polygon.io/v3/reference/tickers?market=stocks&type=CS&active=true&sort=market_cap&order=asc&limit=1000&apiKey=' + API_KEY
    response = requests.get(url)
    tickers = []
    if response.status_code == 200:
        data = response.json()
        for result in data['results']:
            if result['market_cap'] < SMALLCAP_THRESHOLD:
                tickers.append(result['ticker'])
    return tickers

def fetch_premarket_data(tickers):
    premarket_data = []
    for ticker in tickers:
        url = PREMARKET_ENDPOINT.format(ticker=ticker)
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                latest_data = data['results'][0]
                premarket_data.append({
                    'ticker': ticker,
                    'volume': latest_data['v'],
                    'close': latest_data['c'],
                    'market_cap': latest_data['c'] * latest_data['v']  # Simplified calculation
                })
    return premarket_data

def filter_top_smallcaps(data):
    smallcaps = [d for d in data if d['market_cap'] < SMALLCAP_THRESHOLD]
    sorted_smallcaps = sorted(smallcaps, key=lambda x: x['volume'], reverse=True)
    return sorted_smallcaps[:10]

def save_to_markdown(companies):
    date_path = datetime.now().strftime('%Y/%m/%d')
    os.makedirs(date_path, exist_ok=True)

    with open('premarket_smallcaps.md', 'w') as f:
        f.write('# Top 10 Premarket Small Cap Companies\n')
        f.write(f'Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
        f.write('| Ticker | Volume | Close Price | Market Cap |\n')
        f.write('| ------ | ------ | ----------- | ---------- |\n')
        for company in companies:
            f.write(f"| {company['ticker']} | {company['volume']} | {company['close']} | {company['market_cap']:,} |\n")
            save_company_details(company, date_path)

def save_company_details(company, date_path):
    file_path = f"{date_path}/{company['ticker']}.md"
    with open(file_path, 'w') as f:
        f.write(f"# {company['ticker']}\n")
        f.write(f"**Volume:** {company['volume']}\n")
        f.write(f"**Close Price:** {company['close']}\n")
        f.write(f"**Market Cap:** {company['market_cap']:,}\n")
        # Add any additional relevant information here

def main():
    tickers = get_smallcap_tickers()
    premarket_data = fetch_premarket_data(tickers)
    top_smallcaps = filter_top_smallcaps(premarket_data)
    save_to_markdown(top_smallcaps)

if __name__ == '__main__':
    main()
