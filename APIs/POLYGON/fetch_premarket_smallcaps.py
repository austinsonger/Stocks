import requests
import pandas as pd
import os

# Constants
API_URL = "https://api.polygon.io/v3/reference/tickers?market=stocks&type=CS&active=true&sort=market_cap&order=asc&limit=1000"
PREMARKET_ENDPOINT = "https://api.polygon.io/v2/aggs/ticker/{ticker}/prev"
SMALLCAP_THRESHOLD = 2_000_000_000  # Market cap in USD (2 billion)
OUTPUT_FILE = "premarket_smallcaps.csv"

def get_smallcap_tickers(api_key):
    response = requests.get(f"{API_URL}&apiKey={api_key}")
    tickers = []
    if response.status_code == 200:
        data = response.json()
        for result in data['results']:
            if result['market_cap'] < SMALLCAP_THRESHOLD:
                tickers.append(result['ticker'])
    return tickers

def fetch_premarket_data(tickers, api_key):
    premarket_data = []
    for ticker in tickers:
        url = f"{PREMARKET_ENDPOINT.format(ticker=ticker)}?apiKey={api_key}"
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

def save_premarket_data(df, file_path):
    df.to_csv(file_path, index=False)

def main():
    api_key = os.getenv('POLYGON_TOKEN')
    if not api_key:
        raise ValueError("Please set the POLYGON_TOKEN environment variable")
    
    tickers = get_smallcap_tickers(api_key)
    premarket_data = fetch_premarket_data(tickers, api_key)
    top_smallcaps = filter_top_smallcaps(premarket_data)
    
    # Convert to DataFrame
    df = pd.DataFrame(top_smallcaps)
    save_premarket_data(df, OUTPUT_FILE)

if __name__ == "__main__":
    main()
