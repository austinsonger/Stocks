import os
import requests
import pandas as pd
from datetime import datetime

# Constants
API_KEY = os.getenv('ALPHA_TOKEN')
PREMARKET_ENDPOINT = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval=1min&apikey=' + API_KEY
MICROCAP_THRESHOLD = 300_000_000  # Market cap in USD

def get_microcap_tickers():
    # Alpha Vantage doesn't provide direct market cap data, so use another reliable source or predefined list
    # For simplicity, using a predefined list
    return ['AAPL', 'MSFT', 'GOOGL']  # Replace with actual microcap tickers

def fetch_premarket_data(tickers):
    premarket_data = []
    for ticker in tickers:
        url = PREMARKET_ENDPOINT.format(ticker=ticker)
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'Time Series (1min)' in data:
                latest_time = sorted(data['Time Series (1min)'].keys())[-1]
                latest_data = data['Time Series (1min)'][latest_time]
                premarket_data.append({
                    'ticker': ticker,
                    'volume': int(latest_data['5. volume']),
                    'close': float(latest_data['4. close']),
                    'market_cap': 0  # Placeholder, update with actual data if available
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
