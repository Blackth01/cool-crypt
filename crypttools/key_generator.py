#!/usr/bin/env python3
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import os
import base64


def derive_key(passphrase, iterations=1460000):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"",
        iterations=iterations,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(passphrase))