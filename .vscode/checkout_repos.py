#!/usr/bin/env python3
import subprocess
import sys
import os

# Arguments passed from launch.json
if len(sys.argv) != 2:
    print("Usage: checkout_repos.py <version>")
    sys.exit(1)

version = sys.argv[1]

workspace = os.path.expanduser("~/dev/src")  # adjust to your dev folder
repos_versioned = ["odoo", "enterprise", "design-themes"]
repos_master = ["internal", "upgrade", "upgrade-specific", "upgrade-util"]

# Git helper
def git_checkout(path, branch):
    print(f"Checking out {path} -> {branch}")
    subprocess.run(["git", "fetch", "--all"], cwd=path, check=True)
    subprocess.run(["git", "checkout", branch], cwd=path, check=True)
    subprocess.run(["git", "pull", "--ff-only"], cwd=path, check=True)

# Checkout main repos to target version
for repo in repos_versioned:
    repo_path = os.path.join(workspace, repo)
    git_checkout(repo_path, version)

# Checkout upgrade and internal repos to master
for repo in repos_master:
    repo_path = os.path.join(workspace, repo)
    git_checkout(repo_path, "master")

print("All repositories checked out successfully.")
