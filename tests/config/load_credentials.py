#!/usr/bin/env python3
"""Load integration test credentials from local_credentials.py.

This script loads credentials from the local_credentials.py file and
sets them as environment variables for integration tests.

"""
Usage:
    # Option A: Export to current shell
    eval "$(python tests/config/load_credentials.py --print-exports)"

    # Option B: Just validate loading (env set only for this process)
    python tests/config/load_credentials.py
"""

import os
import sys
from pathlib import Path
import argparse
# Add the tests/config directory to the path
config_dir = Path(__file__).parent
sys.path.insert(0, str(config_dir))

try:
    from local_credentials import (
        EXCHANGE_API_KEY,
        EXCHANGE_ID,
        EXCHANGE_SECRET,
        MOCKX_API_KEY,
        MOCKX_BASE_URL,
    )

    if args.print_exports:
        print(f'export MOCKX_BASE_URL="{MOCKX_BASE_URL}"')
        print(f'export MOCKX_API_KEY="{MOCKX_API_KEY}"')
        print(f'export EXCHANGE_ID="{EXCHANGE_ID}"')
        print(f'export EXCHANGE_API_KEY="{EXCHANGE_API_KEY}"')
        print(f'export EXCHANGE_SECRET="{EXCHANGE_SECRET}"')
        sys.exit(0)

    # Set environment variables
    os.environ["MOCKX_BASE_URL"] = MOCKX_BASE_URL
    os.environ["MOCKX_API_KEY"] = MOCKX_API_KEY
    os.environ["EXCHANGE_ID"] = EXCHANGE_ID
    os.environ["EXCHANGE_API_KEY"] = EXCHANGE_API_KEY
    os.environ["EXCHANGE_SECRET"] = EXCHANGE_SECRET
    # Set environment variables
    os.environ["MOCKX_BASE_URL"] = MOCKX_BASE_URL
    os.environ["MOCKX_API_KEY"] = MOCKX_API_KEY
    os.environ["EXCHANGE_ID"] = EXCHANGE_ID
    os.environ["EXCHANGE_API_KEY"] = EXCHANGE_API_KEY
    os.environ["EXCHANGE_SECRET"] = EXCHANGE_SECRET

    print("✅ Credentials loaded successfully!")
    print(f"   MOCKX_BASE_URL: {MOCKX_BASE_URL}")
    print(f"   EXCHANGE_ID: {EXCHANGE_ID}")
    print(f"   EXCHANGE_API_KEY: {'*' * 8}...{EXCHANGE_API_KEY[-4:]}")

except ImportError as e:
    print("❌ Could not load credentials:")
    print(f"   {e}")
    print("\nMake sure you have created tests/config/local_credentials.py")
    print("Run: cp tests/config/credentials.example.py tests/config/local_credentials.py")
    print("Then edit local_credentials.py with your actual credentials")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error loading credentials: {e}")
    sys.exit(1)
