"""将 normalize.py 中的字典常量提取到 JSON"""
import ast
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NORMALIZE_PATH = os.path.join(SCRIPT_DIR, '..', 'igneous_wr', 'core', 'normalize.py')
JSON_PATH = os.path.join(SCRIPT_DIR, 'references', 'normalization.json')

with open(NORMALIZE_PATH) as f:
    source = f.read()

tree = ast.parse(source)

data = {}
norm_dict_keys = {}  # name -> list of (key_str, name)
ree_order = None
spider_order = None
aliases = {}
docstring_seen = False

for node in ast.walk(tree):
    # Extract docstring
    if isinstance(node, ast.Module):
        for child in node.body:
            if isinstance(child, ast.Expr) and isinstance(child.value, ast.Constant) and isinstance(child.value.value, str):
                data['_docstring'] = child.value.value.replace('\n', ' ')
                break
    
    # Find dict assignments
    if isinstance(node, ast.Assign):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Dict):
            name = node.targets[0].id
            if name.startswith('_'):
                continue
            d = {}
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant):
                    key = k.value
                else:
                    continue
                if isinstance(v, ast.Constant):
                    d[key] = v.value
                elif isinstance(v, ast.UnaryOp) and isinstance(v.op, ast.USub) and isinstance(v.operand, ast.Constant):
                    d[key] = -v.operand.value
            if d:
                data[name] = d
    
    # NORM_DICT
    if isinstance(node, ast.Assign):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == 'NORM_DICT':
            if isinstance(node.value, ast.Dict):
                for k, v in zip(node.value.keys, node.value.values):
                    if isinstance(k, ast.Constant) and isinstance(v, ast.Name):
                        norm_dict_keys[k.value] = v.id
    
    # REE_ORDER / SPIDER_ORDER
    if isinstance(node, ast.Assign):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in ('REE_ORDER', 'SPIDER_ORDER') and isinstance(node.value, ast.List):
                lst = [e.value for e in node.value.elts if isinstance(e, ast.Constant)]
                data[f'_{name}'] = lst
    
    # Aliases (CHONDRITE = ..., CHONDRITE_MS95 = ..., etc.)
    if isinstance(node, ast.Assign):
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if isinstance(node.value, ast.Name) and node.value.id in data:
                aliases[name] = node.value.id

# Remove entries that are aliases from data
for alias, target in list(aliases.items()):
    data.pop(alias, None)

data['_NORM_DICT'] = norm_dict_keys
data['_aliases'] = aliases

os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"✅ Extracted {len([k for k in data if not k.startswith('_')])} dict constants to {JSON_PATH}")
print(f"   NORM_DICT entries: {len(norm_dict_keys)}")
print(f"   Aliases: {len(aliases)}")
