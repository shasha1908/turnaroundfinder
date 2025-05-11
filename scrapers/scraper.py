# scrapers/scraper.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import json
import os

class BusinessScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
    
    def scrape_bizbuysell_sample(self):
        """
        This is a simplified demonstration scraper.
        In a real application, you would implement proper pagination and error handling.
        
        Note: Always check terms of service before scraping any website.
        """
        businesses = []
        
        # For demo purposes, we'll use a sample page
        # (In a real app, you'd loop through multiple pages)
        url = 'https://www.bizbuysell.com/businesses-for-sale/'
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find business listings
            listings = soup.select('div.card.card--result')
            
            for listing in listings[:10]:  # Limit to first 10 for demo
                try:
                    # Extract basic info (adjust selectors based on actual structure)
                    title_elem = listing.select_one('h2.card-title')
                    title = title_elem.text.strip() if title_elem else "Unknown"
                    
                    link_elem = title_elem.find('a') if title_elem else None
                    link = f"https://www.bizbuysell.com{link_elem['href']}" if link_elem and 'href' in link_elem.attrs else ""
                    
                    desc_elem = listing.select_one('div.card-description')
                    description = desc_elem.text.strip() if desc_elem else ""
                    
                    # Extract price and financials
                    price_elem = listing.select_one('div.price')
                    price_text = price_elem.text.strip() if price_elem else "0"
                    price = self._extract_price(price_text)
                    
                    # Extract location
                    location_elem = listing.select_one('p.card-location')
                    location = location_elem.text.strip() if location_elem else "Unknown"
                    
                    # Extract other financial data if available
                    revenue = self._extract_value(listing, 'Cash Flow:', '0')
                    
                    business = {
                        'title': title,
                        'price': price,
                        'revenue': revenue,
                        'description': description,
                        'location': location,
                        'url': link
                    }
                    businesses.append(business)
                    
                except Exception as e:
                    print(f"Error parsing listing: {e}")
            
            # Save data to file
            df = pd.DataFrame(businesses)
            df.to_csv('data/raw_listings.csv', index=False)
            return df
            
        except Exception as e:
            print(f"Error scraping data: {e}")
            return pd.DataFrame()
    
    def _extract_price(self, text):
        """Extract numeric price from text like '$100,000'"""
        if not text:
            return 0
        numbers = re.findall(r'[\d,]+', text)
        if numbers:
            return int(numbers[0].replace(',', ''))
        return 0
    
    def _extract_value(self, listing, label, default="0"):
        """Extract a value from a label in the listing"""
        elements = listing.find_all('div', class_='fact')
        for element in elements:
            if label in element.text:
                value_text = element.text.replace(label, '')
                numbers = re.findall(r'[\d,]+', value_text)
                if numbers:
                    return int(numbers[0].replace(',', ''))
        return int(default)

    def load_sample_data(self):
        """For testing: load sample data or generate it if not available"""
        try:
            return pd.read_csv('data/raw_listings.csv')
        except FileNotFoundError:
            # For demo/development - create sample data if no real data
            sample_data = [
                {
                    'title': 'Struggling Restaurant in Downtown',
                    'price': 120000,
                    'revenue': 300000,
                    'description': 'Recently reduced price! Restaurant showing declining revenue but in prime location. Owner must sell quickly due to health issues.',
                    'location': 'Seattle, WA',
                    'url': 'https://example.com/business1'
                },
                {
                    'title': 'Manufacturing Business - Priced to Sell',
                    'price': 450000,
                    'revenue': 750000,
                    'description': 'Motivated seller! Manufacturing business with solid customer base but declining profits due to management issues. Great opportunity for experienced operator.',
                    'location': 'Portland, OR',
                    'url': 'https://example.com/business2'
                },
                # Add more sample entries here
            ]
            df = pd.DataFrame(sample_data)
            df.to_csv('data/raw_listings.csv', index=False)
            return df