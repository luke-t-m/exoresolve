from cryptography.fernet import Fernet
import subprocess
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))


def gigaread(filename):
    try:
        with open(filename) as file:
            contents = file.read()
    except Exception:
        contents = ""
    return contents


def gigawrite(filename, contents):
    gigarun(["chattr", "-ia", filename])
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as file:
        file.write(contents)


def gigarun(args):
    try:
        subprocess.run(args)
    except Exception:
        pass


def sort_sections(raw):
    sections = raw.split("#")
    sections = [section.strip().split("\n") for section in sections if section != ""]
    return {section[0]: set(section[1:]) for section in sections}


hovm = "/usr/local/exoresolve"

# Generate key.
if False:
    key = Fernet.generate_key()  # store in a secure location
    gigawrite("trollololollolllolol", "sned")


key = gigaread(f"{hovm}/keyed").encode()
ferny = Fernet(key)

# TO DO: make backups.
for list_name in ["always", "sometimes", "never"]:
    raw = gigaread(f"{hovm}/lists/{list_name}.list")
    sections = sort_sections(raw)
    enc_raw = gigaread(f"{dir_path}/encrypted_lists/{list_name}.list.enc")
    if len(enc_raw) != 0:
        enc_raw = ferny.decrypt(enc_raw.encode()).decode()
    
    enc_sections = sort_sections(enc_raw)

    for section in enc_sections:
        if section in sections:
            sections[section].update(enc_sections[section])
        else:
            sections[section] = enc_sections[section]

    out = []
    for k, v in sections.items():
        v = list(v)
        v.sort()
        head = f"# {k}"
        tail = "\n".join(v)
        out.append(f"\n{head}\n{tail}\n")
    out.sort()
    out = "".join(out)

    gigawrite(f"{hovm}/lists/{list_name}.list", out)

    enc_out = ferny.encrypt(out.encode())
    gigawrite(f"{dir_path}/encrypted_lists/{list_name}.list.enc", enc_out.decode())
    


exit()
#e = ferny.encrypt(b"testing testing\ncan you hear me?\nno?\noh well.")
#gigawrite("e_test", e.decode())
e = gigaread("e_test").encode()


print(e)
d = ferny.decrypt(e)
print(d.decode())