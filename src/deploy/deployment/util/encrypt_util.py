# -*- coding=utf-8 -*-
# author: yanyang.xie@gmail.com

import pyDes
import binascii

# using pyDes to do encrypt
def encrypt(key, encrypt_string):
    # Key must be exactly 8 bytes long
    DESKey = pyDes.des(key, padmode=pyDes.PAD_PKCS5)
    return binascii.b2a_hex(DESKey.encrypt(encrypt_string))

def decrypt(key, encrypted_string):
    # Key must be exactly 8 bytes long
    DESKey = pyDes.des(key, padmode=pyDes.PAD_PKCS5)
    return DESKey.decrypt(binascii.a2b_hex(encrypted_string))  

if __name__ == '__main__':
    key = 'Thistech'
    pwd = 'Vicky123$'
    
    encrypted_string = encrypt(key, pwd)
    print encrypted_string
    print decrypt(key, encrypted_string)