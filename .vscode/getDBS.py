#!/usr/bin/env python3
import subprocess
import re

query = f"SELECT datname FROM pg_database WHERE datname LIKE 'oes_%'"
out = subprocess.check_output(
    ["psql", "-c", query, "-d", "postgres", "-q"], universal_newlines=True
)
dbs = re.findall("oes_(\S+)", out)
for db in dbs:
    print(db)
