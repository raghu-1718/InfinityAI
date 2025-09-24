#!/usr/bin/env python
"""Generate a bcrypt hash for a plaintext password.
Usage:
  python scripts/generate_bcrypt_hash.py 'YourPassword'
"""
import sys
from passlib.hash import bcrypt

if len(sys.argv) != 2:
    print("Usage: python scripts/generate_bcrypt_hash.py 'YourPassword'", file=sys.stderr)
    sys.exit(1)

password = sys.argv[1]
print(bcrypt.hash(password))
