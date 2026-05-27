#!/usr/bin/env python3
"""
batch_backgrounds_main.py — CLI 包装器

委托给 igneous_geochem.batch.backgrounds.run_batch
"""
import argparse, sys, os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from igneous_geochem.batch.backgrounds import run_batch, DEFAULT_OUT_DIR

parser = argparse.ArgumentParser(description='批量生成纯底图')
parser.add_argument('--mode', default='full', choices=['minimal', 'full'],
                    help="'minimal'=纯NaN（0样品） | 'full'=伪造数据+patch scatter（推荐）")
parser.add_argument('--out-dir', default=None,
                    help=f"输出目录（默认 {DEFAULT_OUT_DIR}）")
args = parser.parse_args()
run_batch(mode=args.mode, out_dir=args.out_dir)
