# Business Turnaround Opportunity Finder

A weekend project to identify and analyze business acquisition opportunities with high turnaround potential.

Screenshots:

<img width="1111" alt="Screenshot 2025-05-10 at 19 27 41" src="https://github.com/user-attachments/assets/402922ae-7b65-49ca-9bc4-9b37f73155f8" />
<img width="1440" alt="Screenshot 2025-05-10 at 19 19 04" src="https://github.com/user-attachments/assets/d31bf154-d42d-4cd6-bb85-23a8b49463f3" />
<img width="1440" alt="Screenshot 2025-05-10 at 19 18 58" src="https://github.com/user-attachments/assets/131cc664-3d02-4b90-92e6-979c73cc21f2" />
<img width="1440" alt="Screenshot 2025-05-10 at 19 18 53" src="https://github.com/user-attachments/assets/60918d99-fea5-4224-9fd1-38828cee2e4a" />


## Features

- **Smart Opportunity Scoring**: Filter businesses by turnaround score and difficulty level
- **Multi-factor Analysis**: Evaluate businesses based on price, revenue, location, management issues, and more
- **Interactive Dashboard**: Visualize data with responsive charts and metrics
- **Detailed Business Profiles**: View comprehensive analysis of each acquisition opportunity
- **Email Reports**: Share results directly from the application

## Technologies Used

- **Python 3.8+**: Core programming language
- **Flask**: Fast, lightweight web framework
- **Pandas**: Data manipulation and analysis
- **scikit-learn**: Machine learning for scoring algorithm
- **Chart.js**: Interactive data visualization
- **Bootstrap 5**: Responsive UI components

## Local Development

1. Clone the repository
   ```
   git clone https://github.com/shasha1908/turnaroundfinder.git
   cd turnaroundfinder
   ```

2. Create a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install flask pandas scikit-learn
   ```

4. Run the application
   ```
   python app.py
   ```

5. Open http://127.0.0.1:5000/ in your browser

## Project Structure

```
turnaround-finder/
├── app.py                # Main Flask application
├── scrapers/             # Data collection modules
│   └── scraper.py        # Sample data generator
├── analysis/             # Business analysis modules
│   └── analyzer.py       # Analysis algorithms
├── static/               # Static files (CSS, JS)
│   └── style.css         # Custom styles
├── templates/            # HTML templates
│   ├── index.html        # Main dashboard
│   ├── business_detail.html # Detailed business view
│   └── error.html        # Error page
└── data/                 # Sample data directory
```

## Future Enhancements

- User accounts and saved searches
- Advanced filtering options
- Real-time data integration (with proper API access)
- Machine learning for more accurate turnaround predictions

## Screenshots

The screenshots folder contains example views of the application:
- ss1.png: Main dashboard view
- ss2.png: Detailed business analysis page
- ss3.png: Data visualization charts
- ss4.png: Mobile-responsive design

## License

MIT License
