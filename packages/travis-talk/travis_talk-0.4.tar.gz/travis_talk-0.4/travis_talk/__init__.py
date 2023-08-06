import hashlib

def hash_string():
    return hashlib.md5("i'm a string").hexdigest()