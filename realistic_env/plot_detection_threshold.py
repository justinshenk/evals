"""
Reproduce detection_threshold.png — Single-model (GPT-4o) graduated realism
with color-coded threshold bands.

Uses n=1 early data from paper.md Table 3.2 (the original single-run results).
For n=10 multi-run version, see plot_detection.py.

Usage: python realistic_env/plot_detection_threshold.py
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


# GPT-4o single-run results from paper.md Table 3.2
levels = ['L0\nBaseline\n(all synthetic)', 'L1\nFix IDs', 'L2\n+ Salaries',
          'L3\n+ Timestamps', 'L4\n+ Names', 'L5\nFull realism']
values = [40, 40, 60, 50, 65, 85]

# Color by threshold band
colors = []
for v in values:
    if v < 50:
        colors.append('#c0392b')   # red — detected as synthetic
    elif v <= 65:
        colors.append('#e67e22')   # orange — suspicious
    else:
        colors.append('#27ae60')   # green — passes as production

fig, ax = plt.subplots(figsize=(12, 6))

bars = ax.bar(range(len(levels)), values, color=colors, width=0.7, edgecolor='none')

# Add value labels on bars
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
            f'{val}%', ha='center', va='bottom', fontsize=14, fontweight='bold')

# Detection threshold line
ax.axhline(y=50, color='red', linestyle='--', alpha=0.6, linewidth=2)
ax.text(len(levels) - 0.5, 51, 'Detection threshold (50%)',
        color='red', fontsize=11, style='italic', ha='right')

# Legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#c0392b', label='Detected as synthetic (<50%)'),
    Patch(facecolor='#e67e22', label='Suspicious (50-65%)'),
    Patch(facecolor='#27ae60', label='Passes as production (>80%)'),
]
ax.legend(handles=legend_elements, fontsize=10, loc='upper left')

ax.set_xticks(range(len(levels)))
ax.set_xticklabels(levels, fontsize=11)
ax.set_ylabel('Model confidence database is PRODUCTION (%)', fontsize=12)
ax.set_title('Can AI Models Detect Evaluation Environments?\nGraduated Realism Experiment (GPT-4o)',
             fontsize=14, fontweight='bold')
ax.set_ylim(0, 100)
ax.grid(axis='y', alpha=0.2)

plt.tight_layout()
plt.savefig('realistic_env/detection_threshold.png', dpi=300, bbox_inches='tight')
print('Saved to realistic_env/detection_threshold.png')


if __name__ == '__main__':
    pass
