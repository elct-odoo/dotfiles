#!/usr/bin/env python3
import subprocess
import sys
import os

if len(sys.argv) != 3:
    print("Usage: upgrade_wrapper.py <db> <version>")
    sys.exit(1)

db = sys.argv[1]
db = f"oes_{db}"

version = sys.argv[2]

# checkout main 3 repos and then pull to master for the rest
subprocess.run(["python3", ".vscode/checkout_repos.py", version], check=True)

# get path to odoo-bin and cd into src
odoo_bin = os.path.join(os.getcwd(), "odoo", "odoo-bin")
addons_path = ",".join([
    os.path.join(os.getcwd(), "odoo", "addons"),
    os.path.join(os.getcwd(), "enterprise"),
    os.path.join(os.getcwd(), "design-themes"),
])
upgrade_path = ",".join([
    os.path.join(os.getcwd(), "upgrade-util", "src"),
    os.path.join(os.getcwd(), "upgrade", "migrations"),
])

# launch upgrade
subprocess.run([
    odoo_bin,
    "-d", db,
    "--addons-path", addons_path,
    "-u", "all",
    "--stop-after-init",
    "--upgrade-path", upgrade_path
], check=True, cwd=os.path.join(os.getcwd()))
