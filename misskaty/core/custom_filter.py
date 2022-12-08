from pyrogram import filters


def pesanedit(_, __, m):
    return bool(m.edit_date)


edited = filters.create(pesanedit)
