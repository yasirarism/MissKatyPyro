import random, string


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = "".join(random.choice(letters) for i in range(length))
    return result_str

def rentry(teks):
    # buat dapetin cookie
    session = requests.Session()
    response = session.get('https://rentry.co')
    kuki = session.cookies.get_dict()
    # headernya
    header = {"Referer": 'https://rentry.co'}

    payload = {'csrfmiddlewaretoken': kuki['csrftoken'], 'text': teks}
    res = requests.post('https://rentry.co/api/new',
                        payload,
                        headers=header,
                        cookies=kuki).json().get("url")
    return res
