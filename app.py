# app.py
from flask import Flask, render_template, request, jsonify
import pandas as pd
from datetime import datetime
import os
import json
import numpy as np
import colorsys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

# Import our custom modules
from scrapers.scraper import BusinessScraper
from analysis.analyzer import BusinessAnalyzer

app = Flask(__name__)

# Initialize our classes
scraper = BusinessScraper()
analyzer = BusinessAnalyzer()

@app.route('/')
def home():
    """Render the main page"""
    return render_template('index.html', 
                          last_updated=datetime.now().strftime("%Y-%m-%d %H:%M"))

@app.route('/api/refresh-data', methods=['POST'])
def refresh_data():
    """API endpoint to refresh the data"""
    try:
        # In a real app, you'd implement proper scraping here
        # For demo purposes, we'll just use sample data
        df = scraper.load_sample_data()
        
        # Analyze the data
        analyzed_df = analyzer.analyze_turnaround_potential(df)
        
        return jsonify({
            'success': True,
            'message': f'Successfully refreshed data with {len(analyzed_df)} listings',
            'count': len(analyzed_df)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error refreshing data: {str(e)}'
        })

@app.route('/api/opportunities')
def get_opportunities():
    """API endpoint to get filtered opportunities"""
    # Get query parameters
    min_score = request.args.get('min_score', 50, type=int)
    max_difficulty = request.args.get('max_difficulty', 5, type=int)
    
    try:
        # Load the analyzed data
        try:
            df = pd.read_csv('data/analyzed_listings.csv')
        except FileNotFoundError:
            # If no analyzed data exists, process it first
            raw_df = scraper.load_sample_data()
            df = analyzer.analyze_turnaround_potential(raw_df)
        
        # Filter businesses
        filtered_df = df[
            (df['turnaround_score'] >= min_score) & 
            (df['turnaround_difficulty'] <= max_difficulty)
        ]
        
        # Sort by score (descending)
        filtered_df = filtered_df.sort_values('turnaround_score', ascending=False)
        
        # Convert to list of dictionaries
        opportunities = filtered_df.to_dict('records')
        
        return jsonify({
            'success': True,
            'count': len(opportunities),
            'opportunities': opportunities
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting opportunities: {str(e)}',
            'opportunities': []
        })



@app.route('/api/chart-data')
def chart_data():
    """Provide data for dashboard charts"""
    try:
        # Load data (or use sample data if file doesn't exist)
        try:
            df = pd.read_csv('data/analyzed_listings.csv')
        except FileNotFoundError:
            # Create sample data with more variety for better charts
            sample_data = [
                {
                    'title': 'Struggling Restaurant in Downtown',
                    'price': 120000,
                    'revenue': 300000,
                    'description': 'Recently reduced price! Restaurant showing declining revenue but in prime location. Owner must sell quickly due to health issues.',
                    'location': 'Seattle, WA',
                    'url': 'https://example.com/business1',
                    'turnaround_score': 85,
                    'turnaround_difficulty': 3,
                    'price_to_revenue_ratio': 0.4
                },
                {
                    'title': 'Manufacturing Business - Priced to Sell',
                    'price': 450000,
                    'revenue': 750000,
                    'description': 'Motivated seller! Manufacturing business with solid customer base but declining profits due to management issues.',
                    'location': 'Portland, OR',
                    'url': 'https://example.com/business2',
                    'turnaround_score': 72,
                    'turnaround_difficulty': 4,
                    'price_to_revenue_ratio': 0.6
                },
                {
                    'title': 'Retail Store in Mall Location',
                    'price': 95000,
                    'revenue': 180000,
                    'description': 'Retail store in busy mall. Current owner not focusing on marketing.',
                    'location': 'Chicago, IL',
                    'url': 'https://example.com/business3',
                    'turnaround_score': 65,
                    'turnaround_difficulty': 2,
                    'price_to_revenue_ratio': 0.53
                },
                {
                    'title': 'Auto Repair Shop with Real Estate',
                    'price': 550000,
                    'revenue': 320000,
                    'description': 'Auto repair shop with property included. Established 15 years but poorly managed.',
                    'location': 'Dallas, TX',
                    'url': 'https://example.com/business4',
                    'turnaround_score': 78,
                    'turnaround_difficulty': 3,
                    'price_to_revenue_ratio': 1.72
                },
                {
                    'title': 'E-commerce Store - Health Products',
                    'price': 75000,
                    'revenue': 210000,
                    'description': 'Online store selling health supplements. Needs better inventory management.',
                    'location': 'Online Business',
                    'url': 'https://example.com/business5',
                    'turnaround_score': 90,
                    'turnaround_difficulty': 1,
                    'price_to_revenue_ratio': 0.36
                },
                {
                    'title': 'Laundromat With Delivery Service',
                    'price': 280000,
                    'revenue': 220000,
                    'description': 'Established laundromat with delivery service in college area. Owner retiring.',
                    'location': 'Boston, MA',
                    'url': 'https://example.com/business6',
                    'turnaround_score': 62,
                    'turnaround_difficulty': 2,
                    'price_to_revenue_ratio': 1.27
                },
                {
                    'title': 'Software Development Agency',
                    'price': 800000,
                    'revenue': 1200000,
                    'description': 'Software dev shop with recurring clients but management issues causing talent loss.',
                    'location': 'Austin, TX',
                    'url': 'https://example.com/business7',
                    'turnaround_score': 81,
                    'turnaround_difficulty': 4,
                    'price_to_revenue_ratio': 0.67
                }
            ]
            df = pd.DataFrame(sample_data)
            
        # Prepare score distribution data
        score_bins = [0, 20, 40, 60, 80, 100]
        score_labels = ['0-20', '21-40', '41-60', '61-80', '81-100']
        score_counts = np.histogram(df['turnaround_score'], bins=score_bins)[0].tolist()
        
        # Prepare price vs revenue data
        price_revenue_data = []
        colors = []
        
        for _, row in df.iterrows():
            # Generate colors based on turnaround score (higher score = more green)
            h = (120 * min(row['turnaround_score'] / 100, 1)) / 360  # 0 = red, 120 = green in HSL
            r, g, b = colorsys.hsv_to_rgb(h, 0.8, 0.8)
            color = f'rgba({int(r*255)}, {int(g*255)}, {int(b*255)}, 0.7)'
            
            price_revenue_data.append({
                'x': row['price'],
                'y': row['revenue'],
                'title': row['title'],
                'score': row['turnaround_score'],
                'difficulty': row['turnaround_difficulty']
            })
            colors.append(color)
        
        return jsonify({
            'score_labels': score_labels,
            'score_data': score_counts,
            'price_revenue_data': price_revenue_data,
            'colors': colors
        })
    
    except Exception as e:
        print(f"Error generating chart data: {e}")
        return jsonify({'error': str(e)})

@app.route('/email-results', methods=['POST'])
def email_results():
    """Email the current search results to the user"""
    try:
        # Get email address from the form
        recipient_email = request.form.get('email')
        min_score = request.args.get('min_score', 50, type=int)
        max_difficulty = request.args.get('max_difficulty', 5, type=int)
        
        if not recipient_email:
            return jsonify({
                'success': False,
                'message': 'Email address is required'
            })
        
        # Get the current filtered opportunities
        try:
            df = pd.read_csv('data/analyzed_listings.csv')
        except FileNotFoundError:
            # Use sample data if file doesn't exist
            raw_df = scraper.load_sample_data()
            df = analyzer.analyze_turnaround_potential(raw_df)
        
        # Filter businesses
        filtered_df = df[
            (df['turnaround_score'] >= min_score) & 
            (df['turnaround_difficulty'] <= max_difficulty)
        ]
        
        # Sort by score (descending)
        filtered_df = filtered_df.sort_values('turnaround_score', ascending=False)
        
        # If no matches, return error
        if len(filtered_df) == 0:
            return jsonify({
                'success': False,
                'message': 'No opportunities match your criteria'
            })
        
        # Create email content
        subject = "Your Business Turnaround Opportunities"
        
        # Create plain text version as fallback
        plain_text = f"""
Business Turnaround Opportunities

Here are the {len(filtered_df)} opportunities that match your criteria:

"""
        
        # Add each business to the plain text version
        for _, business in filtered_df.iterrows():
            plain_text += f"""
{business['title']}
Location: {business['location']}
Price: ${int(business['price']):,}
Revenue: ${int(business['revenue']):,}
Score: {int(business['turnaround_score'])}
URL: {business['url']}

"""
        
        # Build the HTML version
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; }
                .card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 20px; }
                .score { font-size: 20px; font-weight: bold; color: white; background-color: #28a745; 
                         padding: 5px 10px; border-radius: 20px; }
                .difficulty { color: #6c757d; }
                .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
                .title { font-size: 18px; font-weight: bold; margin: 0; }
                .location { color: #6c757d; margin-top: 5px; }
                .details { display: flex; margin: 10px 0; }
                .details div { margin-right: 20px; }
                .label { font-weight: bold; }
            </style>
        </head>
        <body>
            <h2>Business Turnaround Opportunities</h2>
            <p>Here are the """ + str(len(filtered_df)) + """ opportunities that match your criteria:</p>
        """
        
        # Add each business to the email
        for _, business in filtered_df.iterrows():
            # Create difficulty stars with ASCII characters
            difficulty_stars = "*" * int(business['turnaround_difficulty']) + "-" * (5 - int(business['turnaround_difficulty']))
            
            # Get business data with safe fallbacks
            title = str(business.get('title', 'Unnamed Business'))
            location = str(business.get('location', 'Unknown Location'))
            price = int(business.get('price', 0))
            revenue = int(business.get('revenue', 0))
            score = int(business.get('turnaround_score', 0))
            url = str(business.get('url', '#'))
            
            # Make sure description is safe
            description = str(business.get('description', 'No description available'))
            if description:
                # Limit length and ensure it's clean
                description = description[:150]
            else:
                description = "No description available"
            
            # Build the business card HTML
            card_html = """
            <div class="card">
                <div class="header">
                    <h3 class="title">{title}</h3>
                    <span class="score">{score}</span>
                </div>
                <div class="location">{location}</div>
                <p>{description}...</p>
                <div class="details">
                    <div>
                        <div class="label">Price:</div>
                        <div>${price:,}</div>
                    </div>
                    <div>
                        <div class="label">Revenue:</div>
                        <div>${revenue:,}</div>
                    </div>
                    <div>
                        <div class="label">Difficulty:</div>
                        <div class="difficulty">{difficulty_stars}</div>
                    </div>
                </div>
                <a href="{url}" style="color: #007bff;">View Details</a>
            </div>
            """.format(
                title=title,
                score=score,
                location=location,
                description=description,
                price=price,
                revenue=revenue,
                difficulty_stars=difficulty_stars,
                url=url
            )
            
            html += card_html
        
        html += """
            <p>This is an automated email from Business Turnaround Finder.</p>
        </body>
        </html>
        """
        
        # For a weekend project with no budget, let's use a simple approach
        # In a real project, you'd use environment variables for these
        sender_email = ""  # Your email
        app_password = ""     # Your app password
        
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['From'] = sender_email
            message['To'] = recipient_email
            message['Subject'] = subject
            
            # Attach plain text version
            part1 = MIMEText(plain_text, 'plain')
            message.attach(part1)
            
            # Attach HTML version
            part2 = MIMEText(html, 'html')
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, app_password)
                server.send_message(message)
            
            return jsonify({
                'success': True,
                'message': f'Results successfully sent to {recipient_email}'
            })
            
        except Exception as e:
            print(f"Error sending email: {e}")
            # Try printing the html to find where the problem is
            problematic_chars = []
            for i, char in enumerate(html):
                if ord(char) > 127:
                    problematic_chars.append((i, char, ord(char)))
            
            if problematic_chars:
                print(f"Found problematic characters at: {problematic_chars[:5]}")
            
            return jsonify({
                'success': False,
                'message': f'Error sending email: {str(e)}'
            })
    
    except Exception as e:
        print(f"Error in email-results: {e}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        })

@app.route('/business/<int:business_id>')
def business_detail(business_id):
    """Show detailed view of a business"""
    try:
        # Load data
        try:
            df = pd.read_csv('data/analyzed_listings.csv')
        except FileNotFoundError:
            raw_df = scraper.load_sample_data()
            df = analyzer.analyze_turnaround_potential(raw_df)
        
        # Find the business by ID (index in this case)
        if business_id < 0 or business_id >= len(df):
            return render_template('error.html', message="Business not found")
        
        business = df.iloc[business_id].to_dict()
        
        # Add additional analysis
        business['roi_estimate'] = f"{(business['revenue'] / business['price'] * 100):.1f}%"
        
        # Calculate potential improvement areas
        improvement_areas = []
        if business.get('declining_revenue', 0) == 1:
            improvement_areas.append({
                'area': 'Revenue Growth',
                'description': 'This business shows signs of declining revenue, which presents an opportunity for new marketing initiatives and sales strategies.',
                'impact': 'High'
            })
        
        if business.get('management_issues', 0) == 1:
            improvement_areas.append({
                'area': 'Management Efficiency',
                'description': 'There appear to be management issues that could be addressed with better operational processes and leadership.',
                'impact': 'High'
            })
            
        if business.get('price_drop', 0) == 1:
            improvement_areas.append({
                'area': 'Valuation',
                'description': 'The price has been reduced, suggesting potential for negotiation or value-based improvements.',
                'impact': 'Medium'
            })
            
        if business.get('prime_location', 0) == 1:
            improvement_areas.append({
                'area': 'Location Leverage',
                'description': 'The business is in a prime location that may not be fully utilized in the current operation.',
                'impact': 'Medium'
            })
            
        # If no improvement areas identified, add a default one
        if not improvement_areas:
            improvement_areas.append({
                'area': 'General Operations',
                'description': 'Potential for operational improvements and efficiency gains under new management.',
                'impact': 'Medium'
            })
            
        return render_template('business_detail.html', business=business, improvement_areas=improvement_areas)
    
    except Exception as e:
        print(f"Error in business detail: {e}")
        return render_template('error.html', message=f"Error: {str(e)}")

# Add to app.py
@app.template_filter('format_number')
def format_number(value):
    """Format a number with commas"""
    return f"{value:,}"

if __name__ == '__main__':
    # Ensure we have some data to work with
    if not os.path.exists('data/analyzed_listings.csv'):
        print("Initializing sample data...")
        raw_df = scraper.load_sample_data()
        analyzer.analyze_turnaround_potential(raw_df)
    
    app.run(debug=True)