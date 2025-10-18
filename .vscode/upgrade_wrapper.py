#!/usr/bin/env python3
"""
Odoo Upgrade Wrapper
Supports two modes:
1. Simple mode: Checks out repos to target version (default)
2. Worktree mode: Uses pre-configured version-specific workspaces (faster)

To enable worktree mode, run: python3 .vscode/setup_worktrees.py

=============================================================================
ANNUAL VERSION UPDATE CHECKLIST (when new Odoo version is released):
=============================================================================
1. Update ALL_VERSIONS list (line ~93)
   - Add new major version (e.g., 20.0)
   - Update saas versions (e.g., saas-18.x → saas-19.x)
   - Optionally drop oldest version

2. Update SAAS_TRACKS dictionary (line ~112)
   - Update to new saas track (e.g., saas-19.2, saas-19.3, saas-19.4)
   - Update entry point (e.g., "saas-19.2": "19.0")

3. Update launch.json dropdown (../launch.json line ~101)
   - Add new versions to "options" list

See README.md for detailed examples.
=============================================================================
"""
import subprocess
import sys
import os

def get_db_version(db):
    """Detect current database version"""
    query = "SELECT latest_version FROM ir_module_module WHERE name='base' LIMIT 1"
    try:
        result = subprocess.check_output(
            ["psql", "-d", db, "-t", "-c", query],
            text=True, stderr=subprocess.DEVNULL
        ).strip()
        return result
    except:
        return "Unknown"

def parse_version(version_str):
    """
    Parse version string to comparable tuple.
    Handles:
      - '16.0' -> (16, 0)
      - '16.0.1.3' -> (16, 0, 1, 3)
      - 'saas-18.2' -> (18, 2)
      - 'saas~18.2.1.3' -> (18, 2, 1, 3)
    """
    try:
        # Handle saas versions (with ~ or -)
        if version_str.startswith('saas'):
            # Remove 'saas-' or 'saas~' prefix
            version_str = version_str.replace('saas-', '').replace('saas~', '')
            parts = version_str.split('.')
            return tuple(int(p) for p in parts)
        
        # Parse regular versions "16.0.1.3" as (16, 0, 1, 3)
        parts = version_str.split('.')
        return tuple(int(p) for p in parts)
    except:
        return None

def get_major_version(version_str):
    """
    Extract major version from any version string.
    Examples:
      '16.0.1.3' -> '16.0'
      '18.0' -> '18.0'
      'saas-18.2' -> 'saas-18.2'
      'saas~18.2.1.3' -> 'saas-18.2'
    """
    # Handle saas versions (normalize ~ to -)
    if version_str.startswith('saas'):
        # Normalize to saas- format
        normalized = version_str.replace('saas~', 'saas-')
        # Take first two version parts: saas-18.2.1.3 -> saas-18.2
        if normalized.startswith('saas-'):
            parts = normalized[5:].split('.')  # Remove 'saas-' prefix
            if len(parts) >= 2:
                return f"saas-{parts[0]}.{parts[1]}"
        return normalized
    
    # Take first two parts (major.minor) for regular versions
    parts = version_str.split('.')
    if len(parts) >= 2:
        return f"{parts[0]}.{parts[1]}"
    return version_str

def calculate_upgrade_path(current_version, target_version):
    """
    Calculate the sequential upgrade path.
    Odoo requires upgrading through each major version.
    Current version can be any version (e.g., 16.0.1.3).
    Target version must be in the supported list.
    
    SaaS (rolling release) versions are only used if:
    - Current version is already a SaaS version, OR
    - Current version is the immediate predecessor (e.g., 18.0 → saas-18.2)
    
    Returns: (is_valid, path_or_error)
    - path is a list of versions to upgrade through
    - error is a string if invalid
    """
    # All supported versions in order (including SaaS versions)
    # MANUAL UPDATE THIS LIST when new versions are released
    # Next year (2026) it will be: 15, 16, 17, 18, 19, saas-19.2, saas-19.3, saas-19.4, 20.0
    ALL_VERSIONS = [
        "15.0",
        "16.0",
        "17.0",
        "18.0",
        "saas-18.2",  # Rolling release versions (current year)
        "saas-18.3",
        "saas-18.4",
        "19.0"
    ]
    
    # Map of saas versions and their predecessors
    # UPDATE THIS when saas versions change (annually)
    # Next year (2026) it will be:
    # SAAS_TRACKS = {
    #     "saas-19.2": "19.0",
    #     "saas-19.3": "saas-19.2",
    #     "saas-19.4": "saas-19.3",
    # }
    SAAS_TRACKS = {
        "saas-18.2": "18.0",      # Entry point: 18.0 can go to saas-18.2
        "saas-18.3": "saas-18.2", # Chain: each saas follows the previous
        "saas-18.4": "saas-18.3",
    }
    
    if current_version == "Unknown":
        return False, (
            f"Cannot detect current database version.\n"
            f"   Please verify the database exists and is accessible.\n"
            f"   Database might not exist or connection failed."
        )
    
    # Validate target version is in our list
    try:
        target_idx = ALL_VERSIONS.index(target_version)
    except ValueError:
        return False, (
            f"Target version '{target_version}' is not supported.\n"
            f"   Supported versions: {', '.join(ALL_VERSIONS)}"
        )
    
    # Parse versions for comparison
    current_parsed = parse_version(current_version)
    target_parsed = parse_version(target_version)
    
    if current_parsed is None:
        return False, f"Cannot parse current version '{current_version}'"
    
    if target_parsed is None:
        return False, f"Cannot parse target version '{target_version}'"
    
    # Check for downgrade
    if target_parsed < current_parsed:
        return False, (
            f"Cannot downgrade from {current_version} to {target_version}!\n"
            f"   Downgrades are not supported by Odoo."
        )
    
    # Check if already on target version (compare major versions)
    current_major = get_major_version(current_version)
    target_major = get_major_version(target_version)
    if current_major == target_major:
        return False, f"Database is already on version {current_version} (same as {target_version})"
    
    # Validate SaaS target: can only target a SaaS version if you're on the right track
    if target_version.startswith('saas-'):
        # Check if current version is valid to reach this SaaS target
        valid_for_saas = False
        
        # Case 1: Already on SaaS track
        if current_major.startswith('saas-'):
            valid_for_saas = True
        
        # Case 2: On the immediate predecessor
        if target_version in SAAS_TRACKS and SAAS_TRACKS[target_version] == current_major:
            valid_for_saas = True
        
        # Case 3: On a SaaS predecessor in the chain
        for saas_ver, predecessor in SAAS_TRACKS.items():
            if predecessor.startswith('saas-') and current_major.startswith('saas-'):
                valid_for_saas = True
                break
        
        if not valid_for_saas:
            return False, (
                f"Cannot upgrade to {target_version} from {current_version}.\n"
                f"   SaaS versions can only be targeted from:\n"
                f"   - Another SaaS version, OR\n"
                f"   - Their immediate predecessor (e.g., 18.0 → saas-18.2)\n"
                f"   Consider upgrading to 19.0 instead."
            )
    
    # Find where to start the upgrade path
    # Get the major version and find its position
    try:
        current_idx = ALL_VERSIONS.index(current_major)
    except ValueError:
        # Current major version not in list, find the closest one before target
        # This handles cases like upgrading from 14.0 or very old versions
        current_idx = -1  # Start from beginning
        for i, v in enumerate(ALL_VERSIONS):
            v_parsed = parse_version(v)
            if v_parsed and v_parsed > current_parsed:
                current_idx = i - 1
                break
        
        if current_idx == -1:
            # Current version is before all our versions, start from first
            current_idx = -1
    
    # Build initial upgrade path (all versions from after current to target, inclusive)
    upgrade_path = ALL_VERSIONS[current_idx + 1:target_idx + 1]
    
    if not upgrade_path:
        return False, f"No upgrade path found from {current_version} to {target_version}"
    
    # Filter out SaaS versions if not applicable
    current_major = get_major_version(current_version)
    
    # Check if we should include SaaS versions
    include_saas = False
    
    # Case 1: Already on a SaaS version
    if current_major.startswith('saas-'):
        include_saas = True
    
    # Case 2: Current is the immediate predecessor to a SaaS version
    for saas_ver, predecessor in SAAS_TRACKS.items():
        if current_major == predecessor:
            include_saas = True
            break
    
    # If we shouldn't include SaaS, filter them out
    if not include_saas:
        filtered_path = []
        for version in upgrade_path:
            if not version.startswith('saas-'):
                filtered_path.append(version)
        upgrade_path = filtered_path
    
    if not upgrade_path:
        return False, f"No upgrade path found from {current_version} to {target_version}"
    
    return True, upgrade_path

def find_workspace(version):
    """
    Find the appropriate workspace for the version.
    Priority:
    1. Version-specific worktree (~/dev/src-{version})
    2. Current workspace with checkout
    """
    base_dir = os.path.expanduser("~/dev")
    worktree_path = os.path.join(base_dir, f"src-{version}")
    
    if os.path.exists(worktree_path) and os.path.exists(os.path.join(worktree_path, "odoo")):
        return worktree_path, "worktree"
    
    return os.getcwd(), "checkout"

def perform_upgrade(db, version, workspace, mode):
    """
    Perform a single upgrade step to the specified version.
    Returns True on success, False on failure.
    """
    print(f"\n{'='*70}")
    print(f"🔄 UPGRADING TO {version}")
    print(f"{'='*70}")
    
    # Checkout if needed
    if mode == "checkout":
        print(f"⏳ Checking out repositories to version {version}...")
        result = subprocess.run(
            ["python3", ".vscode/checkout_repos.py", version],
            cwd=os.getcwd()
        )
        if result.returncode != 0:
            print(f"❌ Checkout failed for version {version}")
            return False
        print("✅ Checkout complete\n")
        workspace = os.getcwd()
    else:
        workspace = os.path.expanduser(f"~/dev/src-{version}")
        print(f"✨ Using worktree: {workspace}\n")
    
    # Prepare paths
    odoo_bin = os.path.join(workspace, "odoo", "odoo-bin")
    addons_path = ",".join([
        os.path.join(workspace, "odoo", "addons"),
        os.path.join(workspace, "enterprise"),
        os.path.join(workspace, "design-themes"),
    ])
    upgrade_path = ",".join([
        os.path.join(workspace, "upgrade-util", "src"),
        os.path.join(workspace, "upgrade", "migrations"),
    ])
    
    # Verify odoo-bin exists
    if not os.path.exists(odoo_bin):
        print(f"❌ Error: odoo-bin not found at {odoo_bin}")
        return False
    
    print(f"🚀 Running upgrade to {version}...")
    print(f"{'='*70}\n")
    
    # Launch upgrade
    result = subprocess.run([
        odoo_bin,
        "-d", db,
        "--addons-path", addons_path,
        "-u", "all",
        "--stop-after-init",
        "--upgrade-path", upgrade_path
    ], cwd=workspace)
    
    if result.returncode == 0:
        print(f"\n{'='*70}")
        print(f"✅ Successfully upgraded to {version}")
        print(f"{'='*70}")
        return True
    else:
        print(f"\n{'='*70}")
        print(f"❌ Upgrade to {version} FAILED")
        print(f"{'='*70}")
        return False

if len(sys.argv) != 3:
    print("Usage: upgrade_wrapper.py <db> <version>")
    print("\nExample: upgrade_wrapper.py my_db 18.0")
    sys.exit(1)

db = sys.argv[1]
full_db = f"oes_{db}"
target_version = sys.argv[2]

# Pre-flight info
print("\n" + "="*70)
print("🚀 ODOO SEQUENTIAL UPGRADE")
print("="*70)
print(f"📊 Database:      {full_db}")

current_version = get_db_version(full_db)
print(f"📍 Current:       {current_version}")
print(f"🎯 Target:        {target_version}")

# Calculate upgrade path
is_valid, result = calculate_upgrade_path(current_version, target_version)
if not is_valid:
    print("="*70)
    print(f"❌ ERROR: {result}")
    print("="*70 + "\n")
    sys.exit(1)

upgrade_path = result

# Extra safety check for empty path
if not upgrade_path or len(upgrade_path) == 0:
    print("="*70)
    print(f"❌ ERROR: No upgrade path calculated")
    print(f"   This might indicate a downgrade attempt or version mismatch")
    print("="*70 + "\n")
    sys.exit(1)

print(f"🛣️  Path:          {' → '.join(upgrade_path)}")

# Determine workspace mode
_, mode = find_workspace(upgrade_path[0])
print(f"🔧 Mode:          {mode}")
print("="*70)

if len(upgrade_path) > 1:
    print(f"\n⚠️  Multi-step upgrade: Will upgrade through {len(upgrade_path)} versions")
    print(f"   This may take a while...")

# Perform sequential upgrades
for step_num, version in enumerate(upgrade_path, 1):
    print(f"\n{'#'*70}")
    print(f"# STEP {step_num}/{len(upgrade_path)}: Upgrading to {version}")
    print(f"{'#'*70}")
    
    workspace, mode = find_workspace(version)
    success = perform_upgrade(full_db, version, workspace, mode)
    
    if not success:
        print(f"\n{'='*70}")
        print(f"❌ UPGRADE FAILED AT VERSION {version}")
        print(f"{'='*70}")
        print(f"\n⚠️  Database is now at an intermediate version.")
        print(f"   You can retry the upgrade from {version} to {target_version}")
        print(f"{'='*70}\n")
        sys.exit(1)

# All upgrades completed successfully
print(f"\n{'='*70}")
print(f"✅ ALL UPGRADES COMPLETED SUCCESSFULLY!")
print(f"{'='*70}")
print(f"📊 Database:      {full_db}")
print(f"🎉 Final Version: {target_version}")
print(f"📈 Upgraded:      {current_version} → {target_version}")
print(f"🔢 Total Steps:   {len(upgrade_path)}")
print(f"{'='*70}\n")
