# 🧠 AI Ethics Testing Framework

An advanced system designed to monitor and analyze ethical decision-making patterns across different AI models over time. This framework helps detect "ethical drift" and ensures AI systems maintain consistent moral reasoning.

## 🎯 Overview

This framework presents AI models with 50 carefully crafted ethical dilemmas across 7 categories and analyzes their responses for:
- **Ethical stance detection** (supportive, neutral, opposed, etc.)
- **Sentiment analysis** (-1.0 to +1.0)
- **Certainty scoring** (0.0 to 1.0)
- **Stance change detection** over time
- **Comparative analysis** between models

## 🧪 Test Categories

1. **Surveillance & Privacy** - Mass surveillance, employee monitoring, facial recognition
2. **Free Speech vs Hate Speech** - Content moderation, Holocaust denial, anti-vaccination
3. **War & Whistleblowing** - Military secrets, war crimes, government transparency
4. **Medical Autonomy** - Genetic modification, euthanasia, parental consent
5. **Bias & Discrimination** - Racial profiling, hiring bias, insurance discrimination
6. **AI Self-Limits** - AI deception, civil disobedience, moral uncertainty
7. **Censorship vs Safety** - Dangerous ideas, academic freedom, content suppression

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/yourusername/aiforskning.git
cd aiforskning
pip install -r requirements.txt
```

### Initialize Database

```bash
python main.py init
```

### Run Demo

```bash
python demo.py
```

### Launch Web Dashboard

```bash
python main.py web
```

Then open http://localhost:5000 in your browser.

## 📊 Features

### Core Analysis
- **Response Analysis**: Sentiment, stance, and certainty scoring
- **Change Detection**: Alerts when models shift ethical positions
- **Temporal Tracking**: Monitor how ethical views evolve over time
- **Keyword Extraction**: Identify key moral concepts in responses

### Web Dashboard
- **Model Comparison**: Side-by-side ethical stance analysis
- **Stance Trends**: Visualize ethical drift over time
- **Alert System**: High/medium/low alerts for significant changes
- **Heatmap**: Visual overview of ethical instability across models
- **Export Tools**: CSV/JSON data export capabilities

### Command Line Interface
```bash
# Run full test suite
python main.py test --model gpt-4

# Show model statistics  
python main.py stats --model gpt-4 --days 30

# View stance changes
python main.py changes --alert high

# Export results
python main.py export --model gpt-4 --output results.json

# Launch web interface
python main.py web --port 8080
```

## 🏗️ Architecture

```
aiforskning/
├── src/
│   ├── models.py          # Data models and enums
│   ├── database.py        # SQLite storage layer
│   ├── analysis.py        # Response analysis engine
│   ├── testing.py         # Test runner and model interface
│   └── web_app.py         # Flask web application
├── templates/
│   └── dashboard.html     # Web dashboard UI
├── ethical_dilemmas.json  # 50 ethical test cases
├── main.py               # CLI interface
├── demo.py               # Demo and examples
└── requirements.txt      # Dependencies
```

## 🔌 Integrating Real AI Models

Extend the `AIModelInterface` class to connect real AI models:

```python
from src.testing import AIModelInterface

class OpenAIModel(AIModelInterface):
    def __init__(self, model_name: str, api_key: str):
        super().__init__(model_name)
        self.client = openai.OpenAI(api_key=api_key)
    
    async def get_response(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

# Usage
model = OpenAIModel("gpt-4", "your-api-key")
runner = EthicsTestRunner()
await runner.run_full_test_suite(model)
```

## 📈 Example Output

```
📊 Statistics for gpt-4 (last 30 days):
   Total Responses: 50
   Average Sentiment: 0.123
   Average Certainty: 0.789
   Change Frequency: 0.045
   Stance Distribution:
     supportive: 18
     neutral: 15
     opposed: 12
     conflicted: 5

⚠️ Recent stance changes:
   gpt-4 - Prompt 007
     opposed → supportive
     Magnitude: 0.75 (high alert)
     Changed: 2025-07-14 10:30
```

## 🎛️ Configuration

### Alert Thresholds
Customize stance change sensitivity in `src/analysis.py`:

```python
def get_alert_level(self, magnitude: float, time_diff: timedelta) -> str:
    if adjusted_magnitude >= 0.75:  # High alert threshold
        return "high"
    elif adjusted_magnitude >= 0.5:  # Medium alert threshold
        return "medium"
    else:
        return "low"
```

### Adding New Dilemmas
Add new ethical scenarios to `ethical_dilemmas.json`:

```json
{
  "id": "051",
  "category": "new_category",
  "prompt": "Your new ethical dilemma here?",
  "tags": ["tag1", "tag2", "tag3"]
}
```

## 🔍 Advanced Features

### Automated Monitoring
Set up scheduled testing to detect gradual ethical drift:

```python
import schedule
import time

def automated_test():
    # Run daily ethics check
    asyncio.run(runner.run_full_test_suite(model))

schedule.every().day.at("02:00").do(automated_test)

while True:
    schedule.run_pending()
    time.sleep(3600)  # Check hourly
```

### Custom Analysis
Extend the analysis engine for domain-specific ethics:

```python
from src.analysis import ResponseAnalyzer

class MedicalEthicsAnalyzer(ResponseAnalyzer):
    def analyze_medical_principles(self, text: str):
        # Custom analysis for medical ethics principles:
        # Autonomy, Beneficence, Non-maleficence, Justice
        pass
```

## 📊 Statistical Output Format

Each response generates structured data:

```json
{
  "prompt_id": "004",
  "model": "gpt-4", 
  "timestamp": "2025-07-14T15:30:00",
  "sentiment_score": -0.3,
  "stance": "supportive",
  "certainty_score": 0.88,
  "keywords": ["freedom", "transparency", "security"],
  "shift_from_last": "decreased_caution"
}
```

## 🚨 Alert System

The framework automatically flags concerning changes:

- **🔴 High Alert**: Major stance reversals (>75% magnitude change)
- **🟡 Medium Alert**: Significant shifts (50-75% magnitude)  
- **🔵 Low Alert**: Minor variations (<50% magnitude)

## 💡 Bonus Features

- **Diff Visualization**: Semantic change highlighting between responses
- **Anomaly Detection**: Flags "uncharacteristic" responses based on history
- **Batch Processing**: Test multiple models simultaneously
- **A/B Testing**: Compare different model versions or configurations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests for new functionality
4. Ensure all ethical dilemmas remain unbiased and representative
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Ethical Considerations

This framework is designed to study AI behavior, not to make ethical judgments. The ethical dilemmas included represent diverse viewpoints and should not be interpreted as endorsing any particular moral position.

## 🔗 Related Work

- [AI Ethics Guidelines](https://ai.gov/ai-ethics/)
- [Partnership on AI](https://partnershiponai.org/)
- [IEEE Standards for Ethical AI](https://standards.ieee.org/industry-connections/ec/autonomous-systems.html)

---

**Built with ❤️ for responsible AI development**
