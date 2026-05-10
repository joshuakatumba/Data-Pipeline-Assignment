# ⬡ Patent Intelligence Dashboard

A high-performance, interactive data pipeline and analytics dashboard for global patent intelligence.

## 🚀 Overview

This project provides a comprehensive end-to-end data pipeline that extracts, cleans, and analyzes synthetic patent data. The results are presented through a premium, dark-themed Streamlit dashboard.

## 📊 Dashboard Preview

![Dashboard Screenshot](./dashboard_screenshot.png)

## ✨ Key Features

- **Interactive Sidebar Explorer**: Filter by year range, classifications, countries, and top results.
- **Advanced Trend Analysis**: Real-time filing trends with linear projection modeling.
- **Geographic & Temporal Analysis**: Visualizing patent distribution across countries and years via heatmaps and donut charts.
- **Full-Text Search**: Instant search across patent titles and abstracts.
- **Premium Aesthetics**: Dark glassmorphic design with custom SVG iconography and animated KPI cards.

## 🛠️ Technology Stack

- **Frontend**: Streamlit, Plotly
- **Data Backend**: SQLite3, Pandas, NumPy
- **Pipeline**: Python (Scripts for Extract, Clean, Load, Analyze)

## 🏗️ Getting Started

1. **Setup Environment**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Data Pipeline**:
   ```bash
   python scripts/1_extract_data.py
   python scripts/2_clean_data.py
   python scripts/3_load_to_sql.py
   python scripts/4_analyze_and_report.py
   ```

3. **Launch Dashboard**:
   ```bash
   streamlit run app.py
   ```

## 📸 How to Add Screenshots

To add your own screenshots to this README:
1. Open your dashboard in the browser.
2. Take a screenshot and save it as `dashboard_screenshot.png` in the project root folder.
3. Commit and push the image to your repository.

---
github: https://github.com/joshuakatumba/Data-Pipeline-Assignment  
Deployment link: https://share.streamlit.io/j46068742/data-pipeline/main/app.py