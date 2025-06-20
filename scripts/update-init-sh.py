#!/usr/bin/env python3
"""Update init.sh with latest AgenticScrum commands using robust parser."""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from agentic_scrum_setup.patching.utils.init_sh_updater import InitShUpdater


def main():
    """Update init.sh in the current directory."""
    init_sh_path = Path.cwd() / "init.sh"
    
    if not init_sh_path.exists():
        print(f"❌ No init.sh found in {Path.cwd()}")
        sys.exit(1)
    
    print(f"🔧 Updating init.sh in {Path.cwd()}")
    
    try:
        updater = InitShUpdater(init_sh_path)
        saved, updates = updater.update_all()
        
        if saved:
            print("✅ Successfully updated init.sh")
            if updates:
                print("\nApplied updates:")
                for update in updates:
                    print(f"  • {update}")
        else:
            print("ℹ️  init.sh is already up to date")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Error updating init.sh: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()