import hashlib


salt = 'Василий'


def hash_password(password, salt):
    res = salt + password
    return hashlib.sha256(res.encode()).hexdigest()

test = 'vatikom'

print(hash_password(test, salt))

# tmp = [{'id': 1, 'name': 'asddfg', 'link': 'link1'}, {'id': 2, 'name': 'asddfg', 'link': 'link1'}, {'id': 3, 'name': 'asddfg', 'link': 'link1'}]

