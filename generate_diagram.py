import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import os

os.makedirs('docs', exist_ok=True)

fig, ax = plt.subplots(1, 1, figsize=(14, 18))
fig.patch.set_facecolor('#0F1117')
ax.set_facecolor('#0F1117')
ax.set_xlim(0, 14)
ax.set_ylim(0, 18)
ax.axis('off')

def box(ax, x, y, w, h, title, subtitle=None, color='#1E2130', border='#534AB7', title_color='#C5C2F8', sub_color='#8B88D4', radius=0.3):
    fancy = FancyBboxPatch((x, y), w, h, boxstyle=f'round,pad=0,rounding_size={radius}',
        facecolor=color, edgecolor=border, linewidth=1.5, zorder=3)
    ax.add_patch(fancy)
    if subtitle:
        ax.text(x + w/2, y + h*0.62, title, ha='center', va='center',
            fontsize=16, fontweight='bold', color=title_color, zorder=4)
        ax.text(x + w/2, y + h*0.28, subtitle, ha='center', va='center',
            fontsize=14, color=sub_color, zorder=4)
    else:
        ax.text(x + w/2, y + h/2, title, ha='center', va='center',
            fontsize=16, fontweight='bold', color=title_color, zorder=4)

def arrow(ax, x1, y1, x2, y2, color='#534AB7'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle='->', color=color, lw=2), zorder=5)

ax.text(7, 17.4, 'SIFT-BENCH', ha='center', fontsize=30, fontweight='bold', color='#FFFFFF', zorder=4)
ax.text(7, 17.0, 'Autonomous IR Accuracy Benchmarking System', ha='center', fontsize=16, color='#8B88D4', zorder=4)

box(ax, 3.5, 15.4, 7, 1.1, 'Evidence Input',
    'Disk images  ·  memory captures  ·  logs  ·  network captures',
    color='#1E1A0A', border='#BA7517', title_color='#FAC775', sub_color='#BA7517')
arrow(ax, 7, 15.4, 7, 14.6)

box(ax, 1.5, 13.2, 11, 1.3, 'MCP Server — read-only by architectural design',
    'get_file_hash  ·  list_directory  ·  extract_strings  ·  search_iocs  ·  analyze_metadata  ·  generate_timeline',
    color='#160F2A', border='#534AB7', title_color='#C5C2F8', sub_color='#7F77DD')
arrow(ax, 7, 13.2, 7, 12.3)

agent_bg = FancyBboxPatch((0.5, 8.8), 13, 3.3, boxstyle='round,pad=0,rounding_size=0.3',
    facecolor='#0A1F1A', edgecolor='#0F6E56', linewidth=1.5, zorder=2)
ax.add_patch(agent_bg)
ax.text(7, 11.85, 'Autonomous IR Agent  —  LLaMA 3.3 70B via Groq', ha='center',
    fontsize=15, fontweight='bold', color='#9FE1CB', zorder=4)

iters = [
    (0.8, 9.8, 'Iteration 1', 'Initial triage'),
    (4.0, 9.8, 'Iteration 2', 'Deep analysis'),
    (7.2, 9.8, 'Iteration 3', 'Self-correction'),
    (10.4, 9.8, 'Iteration 4', 'Report generation'),
]
for (ix, iy, t, s) in iters:
    box(ax, ix, iy, 2.8, 1.5, t, s, color='#1A1F2E', border='#444441', title_color='#D3D1C7', sub_color='#888780')

for xa in [3.6, 6.8, 10.0]:
    ax.annotate('', xy=(xa+0.4, 10.55), xytext=(xa, 10.55),
        arrowprops=dict(arrowstyle='->', color='#1D9E75', lw=1.5), zorder=5)

guard = FancyBboxPatch((0.8, 9.0), 12.4, 0.65, boxstyle='round,pad=0,rounding_size=0.2',
    facecolor='#081510', edgecolor='#0F6E56', linewidth=1, zorder=3)
ax.add_patch(guard)
ax.text(7, 9.33, 'Architectural guardrail: no destructive commands exist in the MCP server API',
    ha='center', va='center', fontsize=14, color='#5DCAA5', zorder=4)

ax.annotate('', xy=(7, 5.8), xytext=(7, 8.9),
    arrowprops=dict(arrowstyle='->', color='#534AB7', lw=1.5,
    mutation_scale=15), zorder=5)

box(ax, 0.5, 6.5, 6, 1.3, 'Ground Truth Evaluator',
    'Accuracy score  ·  hallucination rate  ·  grade',
    color='#1F0E08', border='#993C1D', title_color='#F5C4B3', sub_color='#D85A30')
box(ax, 7.5, 6.5, 6, 1.3, 'Report Generator',
    'Structured IR report  ·  confidence score',
    color='#060F1F', border='#185FA5', title_color='#B5D4F4', sub_color='#378ADD')

ax.annotate('', xy=(3.5, 7.8), xytext=(5.5, 8.8),
    arrowprops=dict(arrowstyle='->', color='#993C1D', lw=1.5), zorder=5)
ax.annotate('', xy=(10.5, 7.8), xytext=(8.5, 8.8),
    arrowprops=dict(arrowstyle='->', color='#185FA5', lw=1.5), zorder=5)

ax.annotate('', xy=(5.0, 5.7), xytext=(3.5, 6.5),
    arrowprops=dict(arrowstyle='->', color='#639922', lw=1.5), zorder=5)
ax.annotate('', xy=(9.0, 5.7), xytext=(10.5, 6.5),
    arrowprops=dict(arrowstyle='->', color='#639922', lw=1.5), zorder=5)

box(ax, 2.5, 4.5, 9, 1.3, 'Output — Accuracy: 100%  ·  Hallucinations: 0%  ·  Grade: EXCELLENT',
    'Full audit trail  ·  execution logs  ·  professional IR report',
    color='#0A1A06', border='#3B6D11', title_color='#C0DD97', sub_color='#639922')

ax.text(0.5, 3.8, 'Legend:', fontsize=14, color='#888780', fontweight='bold')
legend_items = [
    ('#BA7517', 'Evidence input'),
    ('#534AB7', 'MCP server'),
    ('#0F6E56', 'IR agent'),
    ('#993C1D', 'Evaluator'),
    ('#185FA5', 'Report generator'),
    ('#3B6D11', 'Output'),
]
for i, (c, label) in enumerate(legend_items):
    lx = 0.5 + (i % 3) * 4.5
    ly = 3.2 - (i // 3) * 0.5
    rect = FancyBboxPatch((lx, ly), 0.3, 0.28, boxstyle='round,pad=0,rounding_size=0.05',
        facecolor=c, edgecolor='none', zorder=4)
    ax.add_patch(rect)
    ax.text(lx + 0.45, ly + 0.14, label, va='center', fontsize=14, color='#B4B2A9', zorder=4)

ax.text(7, 0.4, 'FIND EVIL! Hackathon  ·  MIT License  ·  github.com/Farhanahmadansari0173/sift-bench',
    ha='center', fontsize=16, color="#5F5E5A")

plt.tight_layout(pad=0)
plt.savefig('docs/architecture_diagram.png', dpi=180, bbox_inches='tight',
    facecolor='#0F1117', edgecolor='none')
print('Saved to docs/architecture_diagram.png')
