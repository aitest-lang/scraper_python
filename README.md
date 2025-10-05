# Recon Tool

A Python Streamlit web application for reconnaissance and contact information extraction from professional sites, mimicking SignalHire functionality. **Streamlit Cloud compatible** - deployable online without local browser dependencies.

## Features

- **Streamlit Web UI**: Interactive web interface for easy reconnaissance
- **Cloud Compatible**: Works on Streamlit Cloud and other hosting platforms
- **Multi-Site Support**: LinkedIn and other professional platforms
- **Contact Extraction**: Emails and phone numbers with validation
- **OSINT Integration**: theHarvester for comprehensive email harvesting
- **Data Export**: JSON and CSV export capabilities
- **Verification**: Email and phone number validation
- **Progress Tracking**: Real-time scraping progress with visual indicators

## Installation

1. Clone or download the project
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install theHarvester (optional, for enhanced OSINT):
```bash
# Install from GitHub or package manager
pip install theHarvester
# or
git clone https://github.com/laramies/theHarvester
cd theHarvester
pip install -r requirements.txt
python setup.py install
```

## Usage

### Local Development

```bash
# Launch via main.py launcher
python main.py

# Or run Streamlit directly
streamlit run app.py
```

2. Open your browser to the displayed URL (usually http://localhost:8501)

3. Enter a profile URL or person name in the web interface

4. Click "🔍 Start Reconnaissance"

5. View extracted contacts with validation status

### Streamlit Cloud Deployment

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set the main file path to `app.py`
5. The `packages.txt` file is included for any required system packages
6. Deploy!

**Note**: The tool uses requests-based scraping (no Selenium) for full Streamlit Cloud compatibility.

## Project Structure

```
recon_tool/
├── main.py                 # Streamlit launcher
├── app.py                  # Streamlit web application
├── requirements.txt        # Python dependencies
├── scrapers/
│   ├── linkedin_scraper.py # LinkedIn-specific scraper
│   └── general_scraper.py  # General website scraper
├── utils/
│   ├── extractors.py       # Contact extraction and validation
│   ├── storage.py          # JSON/CSV storage utilities
│   └── theharvester_integration.py # OSINT tool integration
└── data/                   # Output directory for results
```

## Dependencies

- **streamlit**: Web interface framework
- **requests/beautifulsoup4**: HTTP requests and HTML parsing (cloud-compatible)
- **linkedin-scraper**: LinkedIn-specific scraping
- **theHarvester**: Email/subdomain reconnaissance
- **email-validator**: Email validation
- **phonenumbers**: Phone number validation and formatting
- **scrapy**: Advanced web scraping framework
- **undetected-chromedriver**: Anti-detection browser automation
- **shodan**: IP/domain reconnaissance

## Output Format

Results are saved as JSON with the following structure:

```json
{
  "emails": ["user@example.com", "contact@company.com"],
  "phones": ["+1 123-456-7890", "+44 20 7123 4567"],
  "metadata": {
    "source_url": "https://www.linkedin.com/in/username",
    "name": "John Doe",
    "title": "Software Engineer",
    "company": "Tech Corp",
    "location": "San Francisco, CA",
    "extraction_timestamp": "2025-10-05T21:30:00",
    "total_emails_found": 2,
    "total_phones_found": 1,
    "validated_emails": 2,
    "validated_phones": 1
  }
}
```

## Legal and Ethical Considerations

- This tool is for educational and research purposes only
- Respect website terms of service and robots.txt
- LinkedIn and other sites have strict scraping policies
- Use responsibly and obtain permission when necessary
- Rate limiting and delays are implemented to minimize impact

## Troubleshooting

### Streamlit Cloud Issues
- The tool uses requests-based scraping (no browser automation) for full cloud compatibility
- LinkedIn may return limited data without authentication
- For better results, consider using the linkedin-scraper library locally

### LinkedIn Scraping Issues
- LinkedIn requires authentication for full profiles
- Static scraping may return login pages or limited content
- Consider manual data entry for critical reconnaissance

### theHarvester Not Found
- Ensure theHarvester is installed and in PATH
- Check Python path if installed via pip
- Some systems may require sudo for installation

### Import Errors
- Install all dependencies: `pip install -r requirements.txt`
- Some packages may require specific Python versions
- Check for conflicting package versions

## Development

### Adding New Scrapers

1. Create a new scraper in `scrapers/` directory
2. Implement a scrape function that returns structured data
3. Update `app.py` to use the new scraper
4. Add any required dependencies to `requirements.txt`

### Extending Contact Extraction

1. Add new regex patterns in `utils/extractors.py`
2. Implement validation functions for new contact types
3. Update the extraction pipeline in `extract_contacts()`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes. Use at your own risk and responsibility.
