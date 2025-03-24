# SEO Monitor Agent for OWL AI Agency

This tool monitors the SEO performance of the OWL AI Agency website, tracking keyword rankings, indexing status, backlinks, and competitor analysis.

## Features

- **Keyword Ranking Tracking**: Monitors rankings for target keywords like "legal research automation" and "batch processing legal research"
- **Indexing Status Checks**: Verifies that important pages are properly indexed by search engines
- **Backlink Analysis**: Tracks backlink growth and referring domains
- **Competitor Analysis**: Monitors competitor websites for keyword usage and content structure
- **Automated Reporting**: Generates comprehensive SEO reports with actionable recommendations
- **Scheduled Monitoring**: Runs daily and weekly tasks automatically
- **AI-Powered Content Generation**: Creates SEO-optimized content briefs and keyword clusters
- **Competitive Intelligence Automation**: Tracks competitor rankings and content strategies in real-time

## Setup Instructions

1. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   - Create a `.env` file in the same directory with the following variables:
     ```
     SEARCH_ENGINE_ID=your_google_custom_search_engine_id
     ```

3. Set up Google API credentials:
   - Create a Google Cloud project and enable the Custom Search API
   - Create service account credentials and download as `google_credentials.json`
   - Place the credentials file in the same directory as the script

## Usage

### Generate a one-time SEO report:

```python
from seo_monitor_agent import SEOMonitorAgent

agent = SEOMonitorAgent()
agent.generate_seo_report()
```

### Schedule regular monitoring:

```python
from seo_monitor_agent import SEOMonitorAgent

agent = SEOMonitorAgent()
agent.schedule_tasks()
```

### Run specific tasks:

```python
from seo_monitor_agent import SEOMonitorAgent

agent = SEOMonitorAgent()

# Check if pages are indexed
agent.check_indexing_status()

# Check keyword rankings
agent.check_keyword_rankings()

# Analyze backlinks
agent.check_backlinks()

# Analyze competitors
agent.analyze_competitors()
```

### Generate SEO-optimized content:

```python
from content_generator import ContentGenerator

generator = ContentGenerator()

# Generate content brief for a topic
brief = generator.generate_content_brief("legal research automation trends")

# Generate keyword clusters
clusters = generator.generate_keyword_clusters("legal research automation")

# Create title variations for A/B testing
titles = generator.generate_title_variations("How to Implement Legal Research Automation")
```

### Monitor competitor rankings and content:

```python
from competitor_monitor import CompetitorMonitor

monitor = CompetitorMonitor()

# Run a full analysis
report = monitor.run_full_analysis()

# Schedule regular monitoring
monitor.schedule_monitoring()

# Analyze specific competitor content
content_analysis = monitor.analyze_competitor_content("https://example-competitor.com/legal-research")
```

## Target Keywords

The agent monitors the following keywords:
- legal research automation
- batch processing legal research
- AI legal research
- legal document automation
- citation formatting legal documents
- document merging legal research
- interactive legal reports
- template customization legal documents
- legal research efficiency
- XRP payments legal services

## Competitors

The agent monitors the following competitors:
- lexisnexis.com
- westlaw.com
- casetext.com
- ross.com
- fastcase.com

## Reports

Reports are saved in the `reports` directory with timestamps in the following formats:
- `indexing_status_YYYYMMDD_HHMMSS.csv`
- `keyword_rankings_YYYYMMDD_HHMMSS.csv`
- `backlinks_YYYYMMDD_HHMMSS.json`
- `competitor_analysis_YYYYMMDD_HHMMSS.json`
- `seo_report_YYYYMMDD_HHMMSS.json`

## Recommendations

The agent generates actionable recommendations based on the collected data, prioritized as High, Medium, or Low, in the following categories:
- Indexing
- Keywords
- Backlinks
- Competitive Analysis
