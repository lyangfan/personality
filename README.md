# DeepMemory

MVP - Memory extraction pipeline for conversations.

## Overview

DeepMemory converts raw chat conversations into structured memory objects with automatic importance scoring.

## Features

- **Structured Memory Extraction**: Convert plain text conversations into JSON-formatted memory fragments
- **Automatic Importance Scoring**: Multi-dimensional scoring (1-10) based on:
  - Sentiment intensity
  - Information density (entities, topics)
  - Task/goal relevance
- **⭐ NEW: GLM-4 Support**: Native support for Zhipu AI's GLM-4 model with companion-style scoring
  - Emotional intensity (0-3 points)
  - Personalization level (0-3 points)
  - Intimacy/relationship (0-2 points)
  - Preference clarity (0-2 points)
- **Pydantic Models**: Type-safe data structures with validation
- **LLM-Powered**: Uses OpenAI API or GLM-4 for intelligent extraction
- **Heuristic Fallback**: Works without LLM using rule-based extraction

## Installation

```bash
pip install -r requirements.txt
```

Set your API key:
```bash
# For OpenAI
export OPENAI_API_KEY="your-api-key"

# For GLM-4 (recommended for companion AI)
export GLM_API_KEY="your-glm-api-key"
```

## Quick Start

### Using GLM-4 (Recommended for Companion AI)

```python
from src.utils.glm_client import GLMClient

# Initialize GLM client
client = GLMClient(api_key="your-glm-api-key", model="glm-4-flash")

# Extract memories with companion-style scoring
conversation = """
User: 我只敢和你说这个秘密
Assistant: 我会保密的
User: 我从小就害怕社交，今天终于鼓起勇气和人说话了
"""

fragments = client.extract_memory_with_scoring(conversation)

# View results
for frag in fragments:
    print(f"{frag['importance_score']}/10 - {frag['content']}")
```

### Using OpenAI API

```python
from src.pipeline import MemoryPipeline

# Initialize pipeline
pipeline = MemoryPipeline(use_llm=True)

# Process conversation
conversation = """
User: 我最喜欢的编程语言是 Python
Assistant: 为什么喜欢 Python?
User: 因为语法简洁,而且有强大的生态系统
"""

fragments = pipeline.process(conversation)

# Output JSON
json_output = pipeline.process_to_json(conversation, output_file="output.json")
print(json_output)
```

### Command Line

```bash
python -m src.pipeline.memory_pipeline examples/sample_conversation.txt
```

## Memory Fragment Structure

Each memory fragment contains:

```json
{
  "content": "用户最喜欢的编程语言是 Python,因为语法简洁且有强大的生态系统",
  "timestamp": "2026-01-12T10:00:00Z",
  "type": "preference",
  "entities": ["Python"],
  "topics": ["编程语言", "技术偏好"],
  "sentiment": "positive",
  "importance_score": 7,
  "confidence": 0.92,
  "metadata": {"source": "chat"}
}
```

### Key Fields

- **importance_score** (int, 1-10): Critical field - importance rating
- **type**: "event" | "preference" | "fact" | "relationship"
- **sentiment**: "positive" | "neutral" | "negative"
- **entities**: List of people, places, organizations
- **topics**: List of themes or subjects

## Importance Scoring Logic

Scores are calculated using three dimensions:

1. **Sentiment Intensity** (0-3 points)
   - High intensity (非常/超级): 3 points
   - Medium intensity: 2 points
   - Low intensity: 1 point

2. **Information Density** (0-4 points)
   - 5+ entities/topics: 4 points
   - 3-4 entities/topics: 3 points
   - 1-2 entities/topics: 2 points

3. **Task Relevance** (0-3 points)
   - Goal-oriented content: higher score
   - Keywords: 必须/重要/目标/任务/计划

## Testing

Run unit tests:
```bash
pytest tests/ -v
```

Run companion-style demo:
```bash
python demo_companion_memory.py
```

See `test_results/` for comprehensive test results with 62 real-world conversation fragments.

## Project Structure

```
personality/
├── src/
│   ├── models/              # Pydantic models
│   ├── extractors/          # Entity, topic, sentiment extractors
│   ├── scorers/             # Importance scoring logic
│   ├── pipeline/            # Main extraction pipeline
│   └── utils/
│       ├── glm_client.py    # GLM-4 client (companion-style scoring)
│       └── llm_client.py    # OpenAI client wrapper
├── tests/                   # Unit tests
├── test_results/            # ⭐ Comprehensive test results
├── examples/                # Sample conversations
├── demo_companion_memory.py # ⭐ Companion-style demo
└── requirements.txt         # Dependencies
```

## Configuration

### Pipeline Options

```python
pipeline = MemoryPipeline(
    api_key="your-key",      # OpenAI API key
    model="gpt-4o-mini",     # Model to use
    min_importance=5,        # Minimum importance score (1-10)
    use_llm=True             # Use LLM (True) or heuristics (False)
)
```

## Requirements

- Python 3.8+
- OpenAI API key (for OpenAI LLM-powered extraction)
- GLM API key (for GLM-4 companion-style scoring, recommended)
- Dependencies in `requirements.txt`

## Documentation

- `USER_GUIDE_CN.md` - Comprehensive Chinese user guide
- `CLAUDE.md` - Project guide for AI assistants
- `test_results/TESTING_SUMMARY.md` - Test results summary

## Changelog

### v0.2.0 (2026-01-14)
- ⭐ Added GLM-4 support with companion-style scoring
- ⭐ Added 4-dimensional companion scoring system
- ⭐ Added comprehensive test results (10 scenarios, 62 fragments)
- 📝 Added demo_companion_memory.py for companion AI

### v0.1.0
- Initial release with OpenAI support
- Multi-dimensional importance scoring
- Heuristic fallback mode

## License

MIT
