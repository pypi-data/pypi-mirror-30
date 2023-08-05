import os, sys
from cryptography.fernet import Fernet

def encode():
    key = Fernet.generate_key() #this is your "password"
    cipher_suite = Fernet(key)
    decoded_text = sys.stdin.read()

    encoded_text = cipher_suite.encrypt(decoded_text)
    print(key)
    print(encoded_text)
    return key, encoded_text

def decode():
    key = sys.stdin.readline()
    cipher_suite = Fernet(key)
    encoded_text = sys.stdin.read()

    decoded_text = cipher_suite.decrypt(encoded_text)
    print(decoded_text)
    return decoded_text

if   sys.argv[1] == '-e': encode()
elif sys.argv[1] == '-d': decode()
else: print("BAD ARGS") ; exit(1)
