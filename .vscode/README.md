# Odoo Development Workspace Setup

VSCode launch configurations and helper scripts for Odoo development and database upgrades.

## 🚀 Quick Start

### Prerequisites
- PostgreSQL with databases named `oes_*` 
- Odoo repos cloned in `~/dev/src/`
- VSCode with Python extension

### Running an Upgrade

1. Press `F5` or open Run and Debug
2. Select **"Upgrade Odoo"**
3. Choose your database from the list (without `oes_` prefix)
4. Choose target version (from the dropdown)
5. Watch it go! ✨

The script will:
- ✅ Detect current database version
- ✅ Calculate the sequential upgrade path
- ✅ Prevent downgrades (e.g., 18.0 → 16.0)
- ✅ Upgrade through each intermediate version automatically
- ✅ Checkout repos to each version as needed

### Supported Versions (in order)

The upgrade path follows Odoo's standard sequence:

```
15.0 → 16.0 → 17.0 → 18.0 → saas-18.2 → saas-18.3 → saas-18.4 → 19.0
```

**Version Format Notes:**
- **Current version** can be any format (e.g., `16.0.1.3`, `saas~18.2.1.3`)
- **Target version** must be from the supported list
- Script automatically handles database formats (tilde `~` vs dash `-`)

**Examples:**
- Upgrading from `15.0` to `17.0`: Goes through `16.0`
- Upgrading from `16.0.1.3` to `19.0`: Goes through `17.0 → 18.0 → 19.0` (skipping SaaS versions)
- Upgrading from `17.0` to `19.0`: Goes through `18.0 → 19.0` (skipping SaaS versions)
- Upgrading from `saas~18.2.1.3` to `19.0`: Goes through `saas-18.3 → saas-18.4 → 19.0`
- Upgrading from `18.0` to `saas-18.4`: Goes through `saas-18.2 → saas-18.3`

**SaaS Version Rules:**
- SaaS versions are **only used** if you're already on a SaaS version OR upgrading from their immediate predecessor (e.g., `18.0`)
- If you're on `17.0` or earlier, you skip SaaS versions and go directly: `18.0 → 19.0`
- If you're on `18.0` and target `19.0`, you skip SaaS: `18.0 → 19.0`
- If you're on `saas~18.x`, you stay on the SaaS track until leaving it

## 📋 Available Launch Configurations

### Run Odoo
Start Odoo with a selected database in debug mode.

### Upgrade Odoo
Upgrade a database to a specific version with automatic repo checkout.

### odoo-bin test file/tag/module
Run specific tests in debug mode.

## 🎯 Working with Multiple Database Versions

If you frequently work with databases on different versions (e.g., testing upgrades from 15→17, 16→18 simultaneously), you can **optionally** set up git worktrees for faster switching.

### Optional: Setup Worktrees (Advanced)

**This is NOT required** - the default mode works fine!

But if you want instant version switching without git checkouts:

```bash
# One-time setup (takes a few minutes)
python3 .vscode/setup_worktrees.py
```

This creates separate workspaces:
```
~/dev/
├── src/         # Your main workspace (any version)
├── src-15.0/    # Always on 15.0
├── src-16.0/    # Always on 16.0
├── src-17.0/    # Always on 17.0
├── src-18.0/    # Always on 18.0
└── src-19.0/    # Always on 19.0
```

**Benefits:**
- ⚡ No checkout delays (instant upgrades)
- 🔄 Work with multiple versions simultaneously
- 🪶 Disk efficient (git worktrees share objects)

The `upgrade_wrapper.py` script automatically detects and uses worktrees if available.

## 📁 Files Overview

### Scripts
- `upgrade_wrapper.py` - Main upgrade orchestrator
- `checkout_repos.py` - Checks out repos to specific version
- `get_dbs.py` - Lists available databases
- `setup_worktrees.py` - Optional worktree setup (advanced users)

### Configuration
- `launch.json` - VSCode debug configurations
- `src.code-workspace` - Workspace settings

## 🛡️ Safety Features

### Downgrade Prevention
The upgrade script prevents you from accidentally downgrading:

```bash
❌ ERROR: Cannot downgrade from 18.0 to 16.0
```

### Version Detection
Automatically detects current database version and shows upgrade path:

```
🚀 ODOO UPGRADE
======================================================================
📊 Database:      oes_my_db
📍 Current:       16.0
🎯 Target:        18.0
💼 Workspace:     /home/odoo/dev/src
🔧 Mode:          checkout
======================================================================
```

### Duplicate Version Protection
Won't let you "upgrade" to the same version:

```bash
❌ ERROR: Database is already on version 17.0
```

## 🔧 Customization

### Changing Workspace Path
Edit the `workspace` variable in `checkout_repos.py`:

```python
workspace = os.path.expanduser("~/dev/src")  # Change this
```

### Adding More Versions
Update both files when new versions are released:

When new Odoo versions are released (typically yearly), you need to update version lists in **three places**:

#### **1. Update `upgrade_wrapper.py` - ALL_VERSIONS list:**
```python
# Example for 2026 (when 20.0 is released):
ALL_VERSIONS = [
    "16.0",      
    "17.0",
    "18.0",
    "saas-18.2", # Drop SaaS RR nextx year - Manual Update
    "saas-18.3",
    "saas-18.4",
    "19.0",
    # Add new version - Manual Update
]
```

#### **2. Update `upgrade_wrapper.py` - SAAS_TRACKS dictionary:**
```python
# Example for 2026:
SAAS_TRACKS = {
    "saas-19.2": "19.0",       # Update to new saas track
    "saas-19.3": "saas-19.2",
    "saas-19.4": "saas-19.3",
}
```

#### **3. Update `launch.json` - version dropdown:**
```json
"options": [
    "20.0",        // Add new version
    "saas-19.4",   // Update saas versions
    "saas-19.3",
    "saas-19.2",
    "19.0",
    "18.0",
    "17.0",
    "16.0",        // Drop oldest if desired
]
```

**Why?** Odoo drops old rolling release versions annually. When 20.0 comes out, `saas-18.x` versions are replaced with `saas-19.x`.

### Custom Database Prefix
Edit `upgrade_wrapper.py` and `get_dbs.py` if your databases don't use `oes_` prefix.

## 🤝 Sharing with Team

This setup is ready to share! Just:

1. Commit these `.vscode` files to your repo
2. Team members can use it immediately
3. Worktrees are optional (script works both ways)

Everyone will get:
- ✅ Same launch configurations
- ✅ Database selection dropdown
- ✅ Upgrade safety checks
- ✅ Pretty output formatting

## 📚 Tips & Tricks

### Quick Database List
```bash
python3 .vscode/get_dbs.py
```

### Manual Checkout
```bash
python3 .vscode/checkout_repos.py 18.0
```

### Check Current DB Version
```bash
psql -d oes_my_db -t -c "SELECT latest_version FROM ir_module_module WHERE name='base' LIMIT 1"
```

## ❓ Troubleshooting

### "Cannot detect current database version"
- Database might not exist or not be accessible
- Script will ask if you want to continue anyway

### "odoo-bin not found"
- Check that repos are in the expected location
- Verify `workspace` path is correct

### Checkout conflicts
```bash
cd ~/dev/src/odoo
git stash  # Save your changes
# Then run upgrade again
```

## 🎨 Example Workflows

### Simple Upgrade (One Version)
```
F5 → "Upgrade Odoo" → my_db → 17.0

🚀 ODOO SEQUENTIAL UPGRADE
======================================================================
📊 Database:      oes_my_db
📍 Current:       16.0
🎯 Target:        17.0
🛣️  Path:          17.0
======================================================================
✅ Successfully upgraded to 17.0
```

### Multi-Step Upgrade (Through SaaS Versions)
```
F5 → "Upgrade Odoo" → old_db → 19.0

🚀 ODOO SEQUENTIAL UPGRADE
======================================================================
📊 Database:      oes_old_db
📍 Current:       17.0
🎯 Target:        19.0
🛣️  Path:          18.0 → saas-18.2 → saas-18.3 → saas-18.4 → 19.0
======================================================================

⚠️  Multi-step upgrade: Will upgrade through 5 versions
   This may take a while...

# STEP 1/5: Upgrading to 18.0
✅ Successfully upgraded to 18.0

# STEP 2/5: Upgrading to saas-18.2
✅ Successfully upgraded to saas-18.2

# STEP 3/5: Upgrading to saas-18.3
✅ Successfully upgraded to saas-18.3

# STEP 4/5: Upgrading to saas-18.4
✅ Successfully upgraded to saas-18.4

# STEP 5/5: Upgrading to 19.0
✅ Successfully upgraded to 19.0

✅ ALL UPGRADES COMPLETED SUCCESSFULLY!
```

### With Worktrees (Optional)
- All upgrades are instant (no checkout time)
- Can work with multiple versions simultaneously

---

Made with ❤️ for Odoo developers

