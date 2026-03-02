import os
import requests
import pandas as pd
from io import StringIO
from datetime import datetime

class FxSwapDataCrawler:
    def __init__(self, token=None):
        self.token = token if token else self._extract_xsrf_token()
        self.current_date = datetime.now().strftime('%d-%m-%Y')
        self.base_url = 'https://vbma.org.vn/csv/markets/tables/vi/fxswapcurve/'
        self.headers = self._prepare_headers()

    def _prepare_headers(self):
        """Prepare request headers with XSRF-TOKEN and other necessary fields."""
        return {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7,fr-FR;q=0.6,fr;q=0.5',
            'Connection': 'keep-alive',
            'Referer': 'https://vbma.org.vn/vi/market-data/fx-swap-curve',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'X-XSRF-TOKEN': self.token,
            'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }

    def _extract_xsrf_token(self):
        """Extract XSRF-TOKEN from the website by sending a GET request to https://vbma.org.vn/vi."""
        url = "https://vbma.org.vn/vi"
        response = requests.get(url, verify=False)

        if response.status_code == 200:
            xsrf_token = response.cookies.get('XSRF-TOKEN')
            if xsrf_token:
                print(f"XSRF-TOKEN: {xsrf_token}")
                return xsrf_token
            else:
                print("XSRF-TOKEN not found in cookies.")
        else:
            print(f"Request failed with status code: {response.status_code}")
        return None

    def _create_folder_if_not_exists(self, file_path):
        """Create the folder if it doesn't already exist."""
        folder_name = os.path.dirname(file_path)
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

    def _make_api_request(self, endpoint):
        """Send a GET request to the specified API endpoint."""
        url = self.base_url + endpoint
        response = requests.get(url, headers=self.headers, verify=False)
        return response

    def _get_data(self, endpoint):
        """Fetch data from the API and return it as a DataFrame."""
        response = self._make_api_request(endpoint)
        if response.status_code == 200:
            csv_data = StringIO(response.text)
            return pd.read_csv(csv_data)
        else:
            print(f"Request failed. Error code: {response.status_code}")
        return None

    def get_fx_swap_data(self, date: str):
        """Fetch FX swap data for a specific date."""
        return self._get_data(f'{date}.csv')

    def get_fx_swap_data_with_details(self):
        """Fetch detailed FX swap data (table-bottom)."""
        return self._get_data('table-bottom.csv')

    def export_data(self, data, file_name):
        """Export the DataFrame to a CSV file after ensuring the folder exists."""
        if data is not None:
            self._create_folder_if_not_exists(file_name)
            data.to_csv(file_name, index=False)
            print(f"Data has been exported to {file_name}")
        else:
            print("No data available to export.")

    def export_fx_swap_data(self, date=None):
        """Export FX swap data for a given date or the current date."""
        if not date:
            date = self.current_date
        data = self.get_fx_swap_data(date)
        file_name = f'data/fxswapcurve_{date}.csv'
        self.export_data(data, file_name)

    def export_fx_swap_data_with_details(self):
        """Export detailed FX swap data for all banks."""
        data = self.get_fx_swap_data_with_details()
        file_name = f'data/fxswapcurve_detail_{self.current_date}.csv'
        self.export_data(data, file_name)

    def run(self, date=None):
        """Run the entire process of fetching and exporting both types of data."""
        self.export_fx_swap_data(date)
        self.export_fx_swap_data_with_details()

if __name__ == "__main__":
    # Token is either passed in or extracted from the website
    token_input = None
    bot = FxSwapDataCrawler(token_input)
    bot.run()