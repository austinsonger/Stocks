import os
import requests
import pandas as pd
from datetime import datetime

# Constants
API_KEY = os.getenv('INTRINIO_TOKEN')
PREMARKET_ENDPOINT = 'https://api-v2.intrinio.com/securities/{ticker}/prices/pre_market?api_key=' + API_KEY
MICROCAP_THRESHOLD = 300_000_000  # Market cap in USD

def get_microcap_tickers():
    url = f'https://api-v2.intrinio.com/companies?market_cap_lt={MICROCAP_THRESHOLD}&api_key={API_KEY}'
    response = requests.get(url)
    tickers = []
    if response.status_code == 200:
        data = response.json()
        for result in data['companies']:
            tickers.append(result['ticker'])
    return tickers

def fetch_premarket_data(tickers):
    premarket_data = []
    for ticker in tickers:
        url = PREMARKET_ENDPOINT.format(ticker=ticker)
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['prices']:
                latest_data = data['prices'][0]
                premarket_data.append({
                    'ticker': ticker,
                    'volume': latest_data['volume'],
                    'close': latest_data['close'],
                    'market_cap': latest_data['market_cap']  # Assumes market_cap is included
                })
    return premarket_data

def filter_top_microcaps(data):
    microcaps = [d for d in data if d['market_cap'] < MICROCAP_THRESHOLD]
    sorted_microcaps = sorted(microcaps, key=lambda x: x['volume'], reverse=True)
    return sorted_microcaps[:10]

def save_to_markdown(companies):
    date_path = datetime.now().strftime('%Y/%m/%d')
    os.makedirs(date_path, exist_ok=True)

    with open('premarket_microcaps.md', 'w') as f:
        f.write('# Top 10 Premarket Microcap Companies\n')
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
    tickers = get_microcap_tickers()
    premarket_data = fetch_premarket_data(tickers)
    top_microcaps = filter_top_microcaps(premarket_data)
    save_to_markdown(top_microcaps)

if __name__ == '__main__':
    main()
