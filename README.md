# 🎯 Pioneers Founder Scout

AI-powered sourcing agent for finding technical founders and co-founders using LinkedIn data via HarvestAPI.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- HarvestAPI account and API key

### Setup

1. **Clone and navigate to the project**
   ```bash
   git clone https://github.com/Alroma79/pioneers-founder-scout.git
   cd pioneers-founder-scout
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your HARVEST_API_KEY
   ```

5. **Run the application**
   ```bash
   # Terminal 1: Backend
   uvicorn backend.app.main:app --reload

   # Terminal 2: Frontend
   streamlit run frontend/streamlit_app.py
   ```

## 📋 Usage

### API Endpoint

**POST** `/search` - Search for founder candidates

Example request:
```json
{
  "sector": "Portugal",
  "founder_signal": true,
  "technical_signal": true,
  "min_years_experience": 5,
  "startup_experience_required": true
}
```

Example using curl:
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "sector": "Portugal",
    "founder_signal": true,
    "technical_signal": true
  }'
```

### Streamlit Interface

1. Open http://localhost:8501 in your browser
2. Use filters to refine candidates:
   - **Tier**: A (80+ score), B (60-79), C (<60)
   - **Profile Type**: Technical vs Business
   - **Text Search**: Search names, summaries, justifications
3. View highlighted Tier A candidates
4. Download filtered results as CSV

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   FastAPI API    │    │   HarvestAPI    │
│                 │◄──►│                  │◄──►│   (LinkedIn)    │
│ • Filters       │    │ • Search logic   │    │ • Profile data  │
│ • Tier display  │    │ • Normalization  │    │ • Geo lookup    │
│ • CSV export    │    │ • Scoring        │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  candidates.csv │
                       │                 │
                       │ • Scored data   │
                       │ • Tier assigned │
                       └─────────────────┘
```

## 🎯 Scoring System

Candidates are scored (0-100) and tiered based on:

- **Founder signals** (+25): "founder", "co-founder", "exit"
- **Technical signals** (+25): "CTO", "engineer", "ML", "AI", "data"
- **Education** (+10): "PhD", "MSc", "master"
- **Sector match** (+15): Matches specified sector
- **Leadership** (+15): "head of", "director", "VP", "chief"

**Tiers:**
- **A**: 80+ points (top candidates)
- **B**: 60-79 points (good candidates)
- **C**: <60 points (potential candidates)

## 🧪 Testing

Run the test suite:
```bash
python -m unittest discover -s tests -v

Or run individual test files:
```bash
python -m unittest tests.test_normalize
python -m unittest tests.test_scoring
python -m unittest tests.test_utils
```

## 📁 Project Structure

```
pioneers-founder-scout/
├── backend/
│   └── app/
│       ├── clients/          # HarvestAPI integration
│       ├── services/         # Business logic
│       ├── storage/          # CSV operations
│       ├── models.py         # Data models
│       └── main.py          # FastAPI app
├── frontend/
│   └── streamlit_app.py     # Streamlit UI
├── tests/                   # Unit tests
├── data/
│   └── candidates.csv       # Generated results
├── requirements.txt
├── .env.example
└── README.md
```

## 🔧 Configuration

Environment variables in `.env`:

```bash
HARVEST_API_KEY=your_api_key_here
HARVEST_BASE_URL=https://api.harvest-api.com
APP_USERNAME=demo
APP_PASSWORD=demo
```

## 🚨 Known Limitations

- **HarvestAPI Rate Limits**: Free tier has usage restrictions
- **LinkedIn Member Privacy**: Many profiles show as "LinkedIn Member" due to privacy settings
- **Geographic Coverage**: Best results for major cities and countries
- **Data Freshness**: Profile data depends on HarvestAPI update frequency
- **Scoring Accuracy**: Keyword-based scoring may miss nuanced experience

## 🛠️ Development

### Adding New Features

1. Create feature branch: `git checkout -b feat/feature-name`
2. Make changes with tests
3. Update documentation
4. Submit PR

### Debugging

Enable debug logging:
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

### API Documentation

When running the backend, visit:
- **Interactive docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📊 Example Results

After running a search for "Portugal" with founder and technical signals:

| No. | Name | Tier | Score | Profile Type | Summary |
|-----|------|------|-------|--------------|---------|
| 1 | João Silva | A | 85 | technical | CTO & Co-Founder at AI startup · Lisbon |
| 2 | Maria Santos | B | 65 | business | Founder & CEO · Porto |
| 3 | LinkedIn Member | C | 45 | technical | Senior Engineer · Braga |

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is for educational purposes as part of the Pioneers internship assignment.

---

**Assignment Brief Alignment:**
- ✅ Data source integration (HarvestAPI/LinkedIn)
- ✅ Search and filtering capabilities
- ✅ CSV output format with structured data
- ✅ Scoring and ranking system
- ✅ User interface for browsing results
- ✅ Geographic search with fallbacks
- ✅ Error handling and logging
