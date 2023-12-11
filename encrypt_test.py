from cryptography.fernet import Fernet
import subprocess


def gigaread(filename):
    try:
        with open(filename) as file:
            contents = file.read()
    except Exception:
        contents = ""
    return contents


def gigawrite(filename, contents):
    gigarun(["chattr", "-ia", filename])
    with open(filename, "w") as file:
        file.write(contents)


def gigarun(args):
    try:
        subprocess.run(args)
    except Exception:
        pass


#key = Fernet.generate_key()  # store in a secure location
#gigawrite("key_test", key.decode())
key = gigaread("key_test").encode()
ferny = Fernet(key)

#e = ferny.encrypt(b"testing testing\ncan you hear me?\nno?\noh well.")
#gigawrite("e_test", e.decode())
e = gigaread("e_test").encode()


print(e)
d = ferny.decrypt(e)
print(d.decode())