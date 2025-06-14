# 🔍 Truth Detector

> An AI-powered Telegram bot for fact-checking news articles and detecting misinformation

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)



## 📖 About

Truth Detector is a Telegram bot that helps users verify news articles and identify potential misinformation. Using advanced AI and multiple source verification, it provides credibility scores and detailed analysis to help users make informed decisions about the information they consume.

<p align="center">
<a href="https://t.me/event_analyser_ai_bot?start=source=github" alt="Run Telegram Bot shield">
  <img src="https://img.shields.io/badge/RUN-Telegram-blue" alt="Run on Telegram" width="200">
</a>
</p>



### ✨ Key Features

- **🤖 AI-Powered Analysis**: Uses OpenAI GPT models for intelligent fact-checking
- **📊 Credibility Scoring**: Provides 1-10 credibility ratings for news articles
- **🔍 Source Verification**: Cross-references claims with multiple reliable sources
- **🌍 Multilingual Support**: Available in English, Russian, Spanish, German, and French
- **⚙️ Customizable Analysis**: Personalize the analysis style to your preferences
- **📱 Telegram Integration**: Easy-to-use bot interface with inline keyboards

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Telegram Bot Token
- OpenAI API Key
- Exa API Key (for source searching)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/truth-detector.git
   cd truth-detector
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp example.env .env
   ```
   
   Edit `.env` and add your API keys:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   OPENAI_API_KEY=your_openai_api_key
   EXA_API_KEY=your_exa_api_key
   OPENAI_BASE_URL=https://openrouter.ai/api/v1
   OPENAI_MODEL=google/gemini-2.5-flash-preview-05-20
   DATABASE_URL=sqlite:///eventanalyzer.db
   ```

4. **Run the bot**
   ```bash
   python main.py
   ```

## 🎯 How It Works

1. **Send a news article** to the bot via Telegram
2. **AI extracts claims** from the article text
3. **Sources are searched** using Exa API for verification
4. **Analysis is generated** comparing claims with found sources
5. **Results are delivered** with credibility score and detailed breakdown


## 📱 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize bot and set up preferences |
| `/language` | Change interface language |
| `/setting` | Customize analysis style |


## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | Required |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `EXA_API_KEY` | Exa search API key | Required |
| `OPENAI_BASE_URL` | OpenAI API base URL | `https://openrouter.ai/api/v1` |
| `OPENAI_MODEL` | AI model to use | `anthropic/claude-3.5-sonnet` |
| `DATABASE_URL` | Database connection string | `sqlite:///eventanalyzer.db` |

### Custom Analysis Styles

Users can customize how the bot analyzes news by:
- Using the default balanced approach
- Creating custom instructions for tone and focus areas
- Adjusting analysis depth and detail level


## 🔒 Privacy & Security

- **User Privacy**: Only Telegram IDs and preferences are saved

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


⭐ **Star this repo if you find it useful!**
