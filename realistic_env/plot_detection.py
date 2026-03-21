"""
Reproduce fig1_detection_v2.png — Environment Detection: Graduated Realism

Reads eval logs from logs/ directory, extracts per-level confidence scores
for the realistic_env task, and plots with 95% CI error bars.

Usage: python realistic_env/plot_detection.py
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import zipfile
import json
import glob
import os
from collections import defaultdict


def load_realistic_env_scores():
    """Extract per-level, per-model scores from realistic_env eval logs."""
    data = defaultdict(lambda: defaultdict(list))

    log_files = sorted(glob.glob('logs/*.eval'))
    for f in log_files:
        try:
            with zipfile.ZipFile(f, 'r') as z:
                start = json.loads(z.read('_journal/start.json'))
                task = start.get('eval', {}).get('task', '?')
                if task != 'realistic_env':
                    continue
                model = start.get('eval', {}).get('model', '?')
                samples = [n for n in z.namelist() if n.startswith('samples/')]

                for s_name in samples:
                    sample_data = json.loads(z.read(s_name))
                    items = sample_data if isinstance(sample_data, list) else [sample_data]
                    for item in items:
                        sid = item.get('id', '')
                        level = sid.rsplit('_r', 1)[0] if '_r' in sid else sid
                        scores = item.get('scores', {})
                        v = scores.get('_score', {}).get('value')
                        if v is not None:
                            data[model][level].append(v)
        except Exception:
            pass

    return data


def ci_95(values):
    """Compute 95% confidence interval half-width."""
    n = len(values)
    if n < 2:
        return 0
    mean = np.mean(values)
    std = np.std(values, ddof=1)
    return 1.96 * std / np.sqrt(n)


def plot_detection(data, output_path='realistic_env/fig1_detection_v2.png'):
    """Generate the graduated realism detection chart."""

    # Canonical level order
    level_order = [
        'L0_baseline', 'L1_fix_ids', 'L2_fix_salaries',
        'L3_fix_timestamps', 'L4_fix_names',
        'L5a_no_hostname', 'L5b_with_hostname',
    ]
    level_labels = [
        'L0\nBaseline', 'L1\n+IDs', 'L2\n+Salaries',
        'L3\n+Timestamps', 'L4\n+Names',
        'L5a\nNo host', 'L5b\n+Host',
    ]

    # Models to plot (with display names and colors)
    model_configs = [
        ('openai/gpt-4o', 'GPT-4o', '#4CAF50'),
        ('anthropic/claude-sonnet-4-20250514', 'Sonnet 4', '#2196F3'),
        ('anthropic/claude-sonnet-4-6', 'Sonnet 4.6', '#FF9800'),
    ]

    # Filter to models that have data with the canonical level names
    available_models = []
    for model_id, display_name, color in model_configs:
        if model_id in data:
            levels_present = set(data[model_id].keys())
            canonical_present = levels_present & set(level_order)
            if len(canonical_present) >= 3:
                available_models.append((model_id, display_name, color))

    if not available_models:
        print("No models found with canonical level names. Available data:")
        for model_id, level_data in data.items():
            print(f"  {model_id}: {sorted(level_data.keys())}")
        return

    n_models = len(available_models)
    x = np.arange(len(level_order))
    width = 0.8 / n_models

    fig, ax = plt.subplots(figsize=(14, 7))

    for i, (model_id, display_name, color) in enumerate(available_models):
        means = []
        errors = []
        for level in level_order:
            scores = data[model_id].get(level, [])
            if scores:
                # Convert to percentage
                means.append(np.mean(scores) * 100)
                errors.append(ci_95(scores) * 100)
            else:
                means.append(0)
                errors.append(0)

        offset = (i - (n_models - 1) / 2) * width
        ax.bar(
            x + offset, means, width,
            yerr=errors, capsize=3,
            label=display_name, color=color, alpha=0.85,
            error_kw={'linewidth': 1.2},
        )

    # 50% threshold line
    ax.axhline(y=50, color='red', linestyle='--', alpha=0.4, linewidth=1.5)

    # Hostname ablation separator
    ax.axvline(x=4.5, color='gray', linestyle=':', alpha=0.5, linewidth=1)
    ax.annotate('hostname\nablation', xy=(4.5, 95), fontsize=9,
                ha='center', color='gray', style='italic')

    ax.set_xlabel('')
    ax.set_ylabel('Confidence database is PRODUCTION (%)', fontsize=12)
    ax.set_title('Environment Detection: Graduated Realism (n=10, 95% CI)',
                 fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(level_labels, fontsize=10)
    ax.set_ylim(0, 110)
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(axis='y', alpha=0.2)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f'Saved to {output_path}')


if __name__ == '__main__':
    data = load_realistic_env_scores()
    print(f'Loaded data for {len(data)} models')
    for model, levels in sorted(data.items()):
        total = sum(len(v) for v in levels.values())
        print(f'  {model}: {total} samples across {len(levels)} levels')
    plot_detection(data)
