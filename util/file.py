import os

def write_to_file(store: dict):
    path = os.path.join("/", "Users", "gurleen", "dtv.txt")
    with open(path, "w+") as out:
        for key, value in store.items():
            if type(value) in [str, int]:
                out.write(f"{key} = {value}\n")