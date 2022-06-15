

def get_int_folders(dir):
    folders = os.listdir(dir)
    int_folders = []
    for folder in folders:
        try:
            n = int(folder)
            int_folders.append(str(n))
        except ValueError:
            continue
    int_folders.sort(key=int)
    return int_folders

