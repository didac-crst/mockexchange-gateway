#!/usr/bin/env python3
"""Script to load credentials and run integration tests.

This script loads credentials from local_credentials.py and runs
the integration tests with the proper environment variables set.
"""

import os
import subprocess
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from local_credentials import (
        EXCHANGE_API_KEY,
        EXCHANGE_ID,
        EXCHANGE_SECRET,
        MOCKX_API_KEY,
        MOCKX_BASE_URL,
    )
except ImportError:
    print("❌ Error: Could not import local_credentials.py")
    print("Make sure you have created tests/config/local_credentials.py with your credentials")
    sys.exit(1)


def set_environment_variables():
    """Set environment variables from local_credentials.py."""
    env_vars = {
        "MOCKX_BASE_URL": MOCKX_BASE_URL,
        "MOCKX_API_KEY": MOCKX_API_KEY,
        "EXCHANGE_ID": EXCHANGE_ID,
        "EXCHANGE_API_KEY": EXCHANGE_API_KEY,
        "EXCHANGE_SECRET": EXCHANGE_SECRET,
    }

    # Only set non-None values
    for key, value in env_vars.items():
        if value is not None:
            os.environ[key] = str(value)
            is_secret = any(token in key for token in ("KEY", "SECRET", "TOKEN", "PASSWORD"))
            display = "[redacted]" if is_secret else (f"{str(value)[:10]}..." if len(str(value)) > 10 else str(value))
            print(f"✅ Set {key} = {display}")
        else:
            print(f"⚠️  {key} is None (will be skipped)")

def run_integration_tests():
    """Run the integration tests."""
    print("\n🚀 Running integration tests...")

    # Change to project root
    os.chdir(project_root)

    # Run pytest with integration flag
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/integration/",
        "--integration",
        "-v",
        "--tb=short",
    ]

    result = subprocess.run(cmd, env=os.environ)
    return result.returncode


def main():
    """Main function."""
    print("🔐 Loading credentials from local_credentials.py...")
    set_environment_variables()

    print("\n📊 Credentials Summary:")
    print(f"   MockExchange URL: {MOCKX_BASE_URL}")
    print(f"   Exchange ID: {EXCHANGE_ID}")
    print(f"   Paper mode: {'✅ Ready' if MOCKX_BASE_URL else '❌ Not configured'}")
    print(
        f"   Production mode: {'✅ Ready' if EXCHANGE_API_KEY and EXCHANGE_SECRET else '❌ Not configured'}"
    )

    exit_code = run_integration_tests()

    if exit_code == 0:
        print("\n🎉 All integration tests passed!")
    else:
        print(f"\n❌ Integration tests failed with exit code {exit_code}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
