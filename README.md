# 🕐 HOROLOGY.IA

AI-powered Rolex valuation terminal using machine learning to predict fair market value based on historical sales data.

![Terminal Preview](docs/screenshot.png)

## 🎯 Features

- **ML-based pricing**: RandomForest model trained on 81,725 real Rolex listings
- **Financial terminal UI**: Dark professional interface inspired by Bloomberg terminals
- **Real-time valuation**: Instant pricing with confidence intervals
- **Market analysis**: Compare prices by year, condition, and accessories
- **Scenario modeling**: Quick "what-if" analysis for different configurations
- **Presentation mode**: Clean view for client presentations
- **Model insights**: Technical specs and historical context for iconic models

## 🛠 Tech Stack

**Backend:**
- Python 3.9+
- Flask (REST API)
- scikit-learn (RandomForest)
- pandas (data processing)

**Frontend:**
- Vanilla JavaScript
- Chart.js (data visualization)
- CSS3 (terminal-inspired design)

**Data:**
- 81,725 Rolex listings scraped from Chrono24
- 6 features: model, year, condition, material, box, papers

## 📊 Model Performance

- **R² Score**: 0.506 (50.6% variance explained)
- **Training samples**: 65,380
- **Test samples**: 16,345
- **Features**: 6 (model, year, condition, material, box, papers)
- **Estimators**: 300 trees

### Feature Importance
- Material: 36.9%
- Model: 31.8%
- Year: 16.7%
- Papers: 6.9%
- Condition: 6.1%
- Box: 1.5%

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/horology-alex/horology-ai.git
cd horology-ai
