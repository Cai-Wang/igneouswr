"""
_diagram_utils.py — 绘图函数末尾通用模式：tight_layout + save + return

每个绘图函数都以这三行结尾：
    plt.tight_layout(pad=0.3)
    if save: save_fig(fig, 'filename.png', out_dir)
    return fig, ax

这里不做任何事，仅声明通用模式。
"""
