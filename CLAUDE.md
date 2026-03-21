# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This repository contains evaluation tasks and research experiments for testing and analyzing LLM capabilities, with a focus on:
1. **Inspect AI evaluation tasks** - Structured benchmarks using the Inspect AI framework
2. **Mathematical understanding research** - Experiments exploring geometric representations of math concepts in LLM latent spaces

## Environment Setup

### Python Environment
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies for Inspect AI tasks
pip install inspect-ai python-dotenv

# Install dependencies for math geometry experiments
pip install openai numpy matplotlib seaborn scikit-learn python-dotenv scipy
```

### Environment Variables
- API keys are stored in `.env` file (never commit this file)
- Required: `OPENAI_API_KEY` for OpenAI API access
- Load using `python-dotenv`: `load_dotenv(".env")`

## Code Architecture

### Inspect AI Tasks (`hellaswag.py`, `security_guide.py`, `task.py`)

These files define evaluation tasks using the Inspect AI framework. The standard pattern is:

```python
from inspect_ai import Task, task
from inspect_ai.dataset import example_dataset, hf_dataset
from inspect_ai.solver import system_message, generate, multiple_choice
from inspect_ai.scorer import model_graded_fact, choice, exact

@task
def task_name():
    return Task(
        dataset=...,        # Data source
        solver=[...],       # Processing pipeline
        scorer=...          # Evaluation metric
    )
```

**Key concepts:**
- `@task` decorator creates an executable evaluation
- `dataset` can be from HuggingFace (`hf_dataset`) or Inspect's examples (`example_dataset`)
- `solver` is a list of processing steps (system message, generation, multiple choice, etc.)
- `scorer` determines how to evaluate model outputs (exact match, model-graded, choice accuracy)

**Running Inspect tasks:**
```bash
# Run a specific task
inspect eval task.py@task_name --model openai/gpt-3.5-turbo

# Run hellaswag evaluation
inspect eval hellaswag.py@hellaswag --model openai/gpt-3.5-turbo
```

### Math Geometry Research (`math_geometry_talk.py`)

This is a standalone research script that generates visualizations for understanding LLM mathematical representations. It runs 5 experiments:

1. **Problem Similarity Clustering** - Maps how similar problems cluster in embedding space
2. **Concept Probing** - Uses linear probes to detect mathematical concepts
3. **Solution Trajectory Tracking** - Visualizes semantic movement during problem-solving
4. **Failure Mode Geometry** - Maps where models fail in latent space
5. **Concept Hierarchy Structure** - Shows hierarchical organization of math concepts

**Architecture:**
- Uses OpenAI embeddings API (`text-embedding-3-small`) for latent representations
- Applies dimensionality reduction (t-SNE, PCA) for visualization
- Generates high-resolution PNG plots (300 DPI) for presentations
- Uses matplotlib with non-interactive backend (`Agg`) for server environments

**Running experiments:**
```bash
source venv/bin/activate
python math_geometry_talk.py
```

Output: 5 PNG files (`experiment_1_*.png` through `experiment_5_*.png`)

**Important implementation detail:**
The script uses `matplotlib.use('Agg')` before importing pyplot to avoid tkinter dependency issues. This must remain at the top of the imports.

## Key Technical Patterns

### Inspect AI Task Pattern
When creating new evaluation tasks:
1. Define a `record_to_sample()` function to transform dataset records into `Sample` objects
2. Use `@task` decorator on the main function
3. Return a `Task` object with dataset, solver pipeline, and scorer
4. Always load environment variables if using external APIs

### Math Visualization Pattern
When adding new experiments to `math_geometry_talk.py`:
1. Get embeddings via `get_embeddings(texts)` helper
2. Apply dimensionality reduction for visualization (t-SNE for non-linear, PCA for linear)
3. Create matplotlib figures with tight layout and proper labeling
4. Save with `plt.savefig(..., dpi=300, bbox_inches='tight')`
5. Print progress messages and key findings

## Common Commands

```bash
# Run Inspect AI evaluations
inspect eval <file>.py@<task_name> --model <model_name>

# Run math geometry experiments
python math_geometry_talk.py

# View experiment logs
tail -f experiment_output.log

# Activate Python environment
source venv/bin/activate
```

## Project Structure Context

- `hellaswag.py` - Commonsense reasoning evaluation using HuggingFace dataset
- `security_guide.py` - Security knowledge evaluation using Inspect's example dataset
- `task.py` - Additional evaluation task (duplicate of security_guide)
- `math_geometry_talk.py` - Research experiments on mathematical concept geometry
- `TALK_SUMMARY.md` - Documentation of math geometry experiment results
- `.env` - API keys (gitignored)
- `venv/` - Python virtual environment
- `experiment_*.png` - Generated visualization outputs
- `logs/` - Inspect AI evaluation logs

## Important Notes

- Inspect AI tasks use the `inspect_ai` package (version 0.3.137 in venv)
- Math experiments require OpenAI API access and consume API credits
- Visualizations are optimized for presentation slides (high DPI, clear labels)
- The math geometry work connects to research on LLM internal representations, inspired by the Inspect AI mathematics evaluation framework
