import base64
import os
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import getpass
import time


def new_db():
    while True:
        p = getpass.getpass(prompt='Set New Password: ').encode()
        p2 = getpass.getpass(prompt='Confirm New Password: ').encode()
        if p == p2:
            break
        print('Passwords do not match')
    salt = os.urandom(16)  # cryptographic salt to protect against rainbow table attacks
    dbpath = input('Path/Name for the new db: ')  # path for the new database
    # metadata = database created timestamp, total transactions included, categories:accounts:payees, last opened time
    metadata = str(time.time()) + ',' + '0' + ',' + 'Misc:Cash:Misc' + ',' + str(time.time()) + '\n'
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
    key = base64.urlsafe_b64encode(kdf.derive(p))  # remove problematic characters
    f_obj = Fernet(key)  # symmetric encyption
    metadata_enc = f_obj.encrypt(metadata.encode())
    with open(dbpath, 'wb') as f:
        f.write(salt)
        f.write(metadata_enc)
    print('File saved as ' + dbpath)


def decrypt_db(dbpath):
    while True:
        with open(dbpath, 'rb') as file_enc:
            salt = file_enc.read(16)
            p = getpass.getpass().encode()
            kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000,
                             backend=default_backend())
            key = base64.urlsafe_b64encode(kdf.derive(p))
            f_obj = Fernet(key)
            mainfile_enc = file_enc.read()
            try:
                mainfile = f_obj.decrypt(mainfile_enc)
                print('Success.')
                break
            except InvalidToken:
                print('Failed to decrypt. Re-enter password.')
    return mainfile, p


def encrypt_db(dbpath, password, sdate, df, t_count, categories, accounts, payees):
    while True:
        pf = getpass.getpass(prompt='Enter Password: ').encode()
        if pf == password:
            break
        print('Incorrect Password.')
    salt = os.urandom(16)  # a new salt every time the database is saved
    metadata = sdate + ',' + str(t_count) + ',' + ':'.join(
        [';'.join(categories), ';'.join(accounts), ';'.join(payees)]) + ',' + str(time.time()) + '\n'
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
    key = base64.urlsafe_b64encode(kdf.derive(pf))
    f_obj = Fernet(key)
    df_string = ''
    for i, j in df.iterrows():
        df_string = df_string + ','.join([str(x) for x in j]) + '\n'  # as a csv with the first line metadata
    df_string = df_string.rstrip()  # removing the rightmost last newline character
    final_enc = f_obj.encrypt(metadata.encode() + df_string.encode())
    with open(dbpath, 'wb') as f:
        f.write(salt)
        f.write(final_enc)
    print('File saved as ' + dbpath)
