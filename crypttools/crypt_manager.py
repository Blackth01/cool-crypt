import struct

from cryptography.fernet import Fernet

ONE_MEGABYTE = 1 << 20

def encrypt(key, fin, fout, *, block = ONE_MEGABYTE):
    fernet = Fernet(key)
    with open(fin, 'rb') as fi, open(fout, 'wb') as fo:
        while True:
            chunk = fi.read(block)
            if len(chunk) == 0:
                break
            enc = fernet.encrypt(chunk)
            fo.write(struct.pack('<I', len(enc)))
            fo.write(enc)
            if len(chunk) < block:
                break

def decrypt(key, fin, fout):
    fernet = Fernet(key)
    with open(fin, 'rb') as fi, open(fout, 'wb') as fo:
        while True:
            size_data = fi.read(4)
            if len(size_data) == 0:
                break
            chunk = fi.read(struct.unpack('<I', size_data)[0])
            dec = fernet.decrypt(chunk)
            fo.write(dec)