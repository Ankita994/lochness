import hashlib

def get_sha(file_loc: str) -> str:
    '''return sha256 hexdigest of a file'''
    BUF_SIZE = 65536
    sha256 = hashlib.sha256()

    with open(file_loc, 'rb') as f:
        data = f.read(BUF_SIZE)
        sha256.update(data)

    return sha256.hexdigest()
