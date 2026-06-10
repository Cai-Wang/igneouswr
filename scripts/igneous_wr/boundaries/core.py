
# boundaries/core.py — 加载边界坐标的工具函数
import json, os

_BOUNDARIES_DIR = os.path.dirname(os.path.abspath(__file__))


def load_boundary(category: str, name: str) -> dict:
    """加载边界坐标 JSON 文件。

    Args:
        category: 图件大类，'cls'/'src'/'evo'/'tec'
        name: 文件名（不含.json），如 'afm', 'mullen'

    Returns:
        解析后的 dict（包含 arrays、points、lines 等字段）
    """
    VALID_CATEGORIES = {'cls', 'src', 'evo', 'tec'}
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid boundary category: {category!r}")
    if '/' in name or '\\' in name or '..' in name:
        raise ValueError(f"Invalid boundary name: {name!r}")
    path = os.path.join(_BOUNDARIES_DIR, category, f"{name}.json")
    real = os.path.realpath(path)
    if not real.startswith(os.path.realpath(_BOUNDARIES_DIR)):
        raise ValueError(f"Path traversal detected: {name!r}")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Boundary file not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def list_boundaries(category: str = None) -> list:
    """列出所有可用的边界数据文件

    Args:
        category: 可选，'cls'/'src'/'evo'/'tec'，None 则列出全部

    Returns:
        文件名列表（不含.json）
    """
    result = []
    cats = [category] if category else ['cls', 'src', 'evo', 'tec']
    for cat in cats:
        d = os.path.join(_BOUNDARIES_DIR, cat)
        if os.path.isdir(d):
            for f in sorted(os.listdir(d)):
                if f.endswith('.json'):
                    result.append(f"{cat}/{f[:-5]}")
    return result
