# AI-Powered Quiz Generator

**Created By:** Tiandra M Taylor  
**Created On:** 01-2026

---

## Overview

This application uses Anthropic's Claude AI to automatically generate 5-question multiple-choice quizzes. Users enter a topic, take the quiz, and receive instant grading with detailed feedback.

**Features:**
- AI-generated quizzes on any topic
- Interactive web interface
- Instant scoring and detailed results
- Modular architecture with error handling

---

## Prerequisites

- Python 3.8+
- Anthropic API key ([Get one here](https://console.anthropic.com/))

---

## Installation

### 1. Clone and Install
```bash
git clone https://github.com/Tiandra123/ai-quiz-generator.git
cd ai-quiz-generator
pip install -r requirements.txt
```

### 2. Add Your API Key
Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=your-api-key-here
```

### 3. Run
```bash
streamlit run app.py
```
The app opens at `http://localhost:8501`

---

## Architecture
```
app.py                  # Streamlit UI and state management
quiz_generator.py       # Claude API integration
quiz_grader.py          # Validation and scoring
```

**Key Decisions:**
- **Streamlit:** Rapid MVP development without frontend code
- **Modular Structure:** Independent components for testability
- **Error Handling:** Automatic retry logic for API reliability

---

## Technical Decisions

### AI Model Selection: Claude Sonnet 4

**Why Claude over other options:**
- **Structured output reliability:** Claude consistently generates valid JSON, critical for parsing quiz data
- **Quality vs. speed balance:** Sonnet 4 provides high-quality questions while maintaining real-time response speeds
- **Instruction following:** Strong adherence to prompt requirements (exactly 5 questions, 4 options, factual accuracy)
- **Cost effectiveness:** Reasonable API pricing for development and testing (~$0.01-0.03 per quiz)

**Alternative considerations:**
- GPT-4: Comparable quality but I have more experience with Claude's API
- Open-source models: Would require local hosting and lack the reliability needed for MVP timeline

### Framework Selection: Streamlit

**Why Streamlit:**
- **Rapid prototyping:** Build functional web UI in pure Python without HTML/CSS/JavaScript
- **Time constraints:** 2-day deadline required focus on core logic over frontend development
- **Requirements alignment:** Challenge prioritized working code over UI polish
- **Deployment simplicity:** Single command to run, easy for reviewers to test

### Architecture: Modular Design

**Why separate modules:**
- **Testability:** Each component (generation, grading, UI) can be tested independently
- **Maintainability:** Changes to one module don't require changes to others
- **Reusability:** Logic can be adapted for different interfaces (CLI, API, different UI frameworks)
- **Interview demonstration:** Clear structure makes it easier to explain design choices

### Error Handling Strategy

**Retry logic implementation:**
- APIs can fail due to network issues, rate limits, or malformed responses
- Automatic retry (up to 3 attempts) provides resilience without manual intervention
- Detailed error messages help with debugging during development

**Input validation:**
- Validates quiz structure before displaying to user (prevents crashes)
- Validates user answers before grading (ensures data integrity)
- Separated validation into dedicated function for reusability
