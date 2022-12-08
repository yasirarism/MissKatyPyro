from pyrogram import filters


def pesanedit(_, __, m: Message):
    return bool(m.edit_date)


edited = filters.create(pesanedit)
