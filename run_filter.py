#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import sys

# Run final_boss.py and auto-confirm with 'y'
process = subprocess.Popen(
    [sys.executable, 'final_boss.py'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding='utf-8'
)

# Auto-send 'y' for confirmation
stdout, _ = process.communicate(input='y\n')
print(stdout)
