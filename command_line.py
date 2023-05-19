import os
import sys
import glob
import getpass
import pyperclip

from cryptography.fernet import InvalidToken

from crypttools.key_generator import derive_key
from crypttools.crypt_manager import encrypt
from crypttools.crypt_manager import decrypt

def remove_file(filepath, ignore_errors=False):
    if(ignore_errors):
        try:
            os.remove(filepath)
        except OSError:
            pass
    else:
        os.remove(filepath)

if(len(sys.argv) > 1):
    arg_1 = sys.argv[1]

    if(arg_1 == "e"):
        mode = arg_1
    else:
        mode = "d"
else:
    mode = input("Would you like to encrypt (e), or decrypt (d)? (Default d): ")

mode_string = "encrypt"

if mode != "e":
    mode_string = "decrypt"

password = getpass.getpass("Enter the password to %s the files: " % mode_string)

if not password:
    print("No password inserted, shutting down execution...")
    sys.exit()

if mode_string == "encrypt":
    confirm_password = getpass.getpass("Please enter the password again to confirm it: ")

    if password != confirm_password:
        print("Password confirmed is different than original password. Shutting down execution...")
        sys.exit()

    copy_password_to_clipboard = input("Would you like to copy the password to your clipboard? (Y/N) ")

    if copy_password_to_clipboard == "Y" or copy_password_to_clipboard == "y":
        try:
            pyperclip.copy(password)
        except Exception as e:
            print("An error occured while trying to copy the password to the clipboard: {}".format(e))
            continue_without_copying = input("Would you still like to continue with the encryption? (Y/N): ")

            if(continue_without_copying != "Y" and continue_without_copying != "y"):
                print("Alright! Shutting down execution...")
                sys.exit()

passphrase = password.encode()

key = derive_key(passphrase)

directory = input("Insert the path for the directory you want to {}: ".format(mode_string))

if not directory:
    print("Directory not informed! Shutting down execution.")
    sys.exit()

for filepath in glob.iglob("%s/**/*" % directory, recursive=True):
    if(os.path.isfile(filepath)):
        if(mode == "e"):
            if(filepath[-6:] != ".enctb"):
                print("Will encrypt: %s" % filepath)
                try:
                    encrypt(key, filepath, filepath+".enctb")
                    os.remove(filepath)
                except Exception as e:
                    print("An error occured while encrypting file %s Error: %s" % (filepath, str(e)))
                    break
        else:
            if(filepath[-6:] == ".enctb"):
                print("Will decrypt: %s" % filepath)
                try:
                    decrypt(key, filepath, filepath[0:-6])
                    remove_file(filepath, ignore_errors=False)
                except InvalidToken:
                    remove_file(filepath[0:-6], ignore_errors=True)
                    print("Can't decrypt the files! Please check if the password is right.")
                    break;
                except Exception as e:
                    remove_file(filepath[0:-6], ignore_errors=True)
                    print("An error occured while decrypting file %s Error: %s" % (filepath, str(e)))
                    break