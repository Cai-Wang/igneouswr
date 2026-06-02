"""
loader.py — 参考文献加载与查询

功能：
- load_refs(): 从 refs.json 加载所有文献记录，返回 dict
- get_ref(key): 按 key 获取单条记录，找不到则返回占位
- get_short(key): 获取文献短名（印在图上）
- get_full(key): 获取完整引用（用于报告）
- resolve_source_ref(source_ref): 将注册表的 source_ref 字符串解析为 (key, short, full)
   支持两种格式：
   - "lebas1992" → 直接从 refs.json 查找
   - "Le Bas et al. 1992" → 尝试模糊匹配
"""

import json
import os
import re
from typing import Optional

# refs.json 路径（相对于本文件）
_REFS_DIR = os.path.dirname(os.path.abspath(__file__))
_REFS_PATH = os.path.join(_REFS_DIR, "refs.json")

# 缓存
_cache = None


def load_refs() -> dict:
    """加载参考文献库，返回 {key: record}"""
    global _cache
    if _cache is not None:
        return _cache
    with open(_REFS_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
    # 过滤掉以 # 开头的键（注释）
    refs = {k: v for k, v in raw.items() if not k.startswith("#")}
    _cache = refs
    return refs


def get_ref(key: str) -> Optional[dict]:
    """按 key 获取文献记录，找不到返回 None"""
    refs = load_refs()
    return refs.get(key)


def get_short(key: str) -> str:
    """获取文献短名（印在图上）"""
    rec = get_ref(key)
    if rec:
        return rec.get("short", key)
    return key


def get_full(key: str) -> str:
    """获取完整引用（用于报告）"""
    rec = get_ref(key)
    if rec:
        full = rec.get("full", "")
        if full:
            return full
        # fallback 到 short
        return rec.get("short", key)
    return key


def resolve_source_ref(source_ref: str, fallback_desc: str = "") -> tuple:
    """将注册表的 source_ref 解析为 (key, short, full, is_verified)

    支持两种输入格式:
    1. 直接是 key（如 "lebas1992"）→ 精确查找
    2. 普通字符串 → 模糊匹配 refs.json 中的 short 字段

    Returns:
        (key, short, full, is_verified)
        - key: 匹配到的 key，找不到则生成一个临时 key
        - short: 用于印在图上的短引用
        - full: 完整引用字符串
        - is_verified: bool，True 表示有完整的 full 引用信息
    """
    refs = load_refs()

    # 1. 精确匹配 key
    if source_ref in refs:
        rec = refs[source_ref]
        return (
            source_ref,
            rec.get("short", source_ref),
            rec.get("full", ""),
            bool(rec.get("full"))
        )

    # 2. 模糊匹配 short 字段
    for key, rec in refs.items():
        if rec.get("short", "").lower() == source_ref.lower():
            return (
                key,
                rec.get("short", source_ref),
                rec.get("full", ""),
                bool(rec.get("full"))
            )

    # 3. 尝试部分匹配
    src_lower = source_ref.lower()
    for key, rec in refs.items():
        short = rec.get("short", "").lower()
        if src_lower in short or short in src_lower:
            return (
                key,
                rec.get("short", source_ref),
                rec.get("full", ""),
                bool(rec.get("full"))
            )

    # 4. 找不到，生成临时 key
    if fallback_desc:
        print(f"[Refs] ⚠️ 未找到匹配引用: '{source_ref}' (用于 {fallback_desc})")
    else:
        print(f"[Refs] ⚠️ 未找到匹配引用: '{source_ref}'")

    tmp_key = re.sub(r"[^a-z0-9]", "_", source_ref.lower()).strip("_")
    return (tmp_key, source_ref, "", False)


def resolve_diagram_ref(diagram_spec) -> tuple:
    """从 DiagramSpec 解析引用，返回 (key, short, full, is_verified)"""
    # 先用 source_ref 找
    src = getattr(diagram_spec, "source_ref", "")
    desc = getattr(diagram_spec, "desc", "")
    if src:
        return resolve_source_ref(src, fallback_desc=desc)
    # 如果 source_ref 为空，从 desc 推测
    return ("", "", "", False)


def get_all_used_keys() -> list:
    """返回注册表中所有用到的引用 key（有序去重）"""
    from igneous_wr.diagrams.registry import DIAGRAM_REGISTRY
    seen = set()
    keys = []
    for d in DIAGRAM_REGISTRY:
        key, _, _, _ = resolve_diagram_ref(d)
        if key and key not in seen:
            seen.add(key)
            keys.append(key)
    return keys


def get_references_for_report(used_keys: list = None) -> list:
    """获取用于报告参考文献列表的记录

    Returns:
        [(key, short, full), ...]
    """
    if used_keys is None:
        used_keys = get_all_used_keys()

    refs = load_refs()
    results = []
    seen = set()
    for key in used_keys:
        if key in seen:
            continue
        seen.add(key)
        rec = refs.get(key, {})
        full = rec.get("full", "") if rec else ""
        short = rec.get("short", key) if rec else key
        results.append((key, short, full))

    return results


def _format_ref_line(key: str, short: str, full: str) -> str:
    """格式化单条参考文献行"""
    if full:
        return f"[{key}] {full}"
    else:
        return f"[{key}] {short} (完整引用信息待补充)"
