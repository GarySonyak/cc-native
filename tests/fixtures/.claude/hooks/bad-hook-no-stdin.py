#!/usr/bin/env python3
"""Negative fixture — a hook script that crashes on empty stdin.

The verify hook smoke-tests every hook script with `echo '{}' | python3 <script>`
and expects exit 0 or 2. This fixture raises, so the verifier should flag it as
a hard error.
"""
import json
import sys

raise RuntimeError("intentional crash to validate cc-native-verify smoke test")
