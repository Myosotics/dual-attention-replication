#!/usr/bin/env python3
import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent
for table in ['table2','table3','table4']:
    subprocess.run([sys.executable,str(root/table/'run.py'),*sys.argv[1:]],check=True)
