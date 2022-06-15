import os


def makeDirs(*dirs):
    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)

def read_database(dir):
    files = os.listdir(dir)
    files.sort()
    if len(files) == 0:
        print(f"error - no airfoils found in {dir}")
    return files
