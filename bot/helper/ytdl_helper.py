import string
import random

def random_char(y):
    return ''.join(random.choice(string.ascii_letters) for _ in range(y))