from math import ceil

from pyrogram.types import InlineKeyboardButton

from misskaty import MOD_LOAD, MOD_NOLOAD


# skipcq: PYL-W1641
class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text


def paginate_modules(page_n, module_dict, prefix, chat=None):
    modules = (
        sorted(
            [
                EqInlineKeyboardButton(
                    x.__MODULE__,
                    callback_data=f"{prefix}_module({chat},{x.__MODULE__.lower()})",
                )
                for x in module_dict.values()
            ]
        )
        if chat
        else sorted(
            [
                EqInlineKeyboardButton(
                    x.__MODULE__,
                    callback_data=f"{prefix}_module({x.__MODULE__.lower()})",
                )
                for x in module_dict.values()
            ]
        )
    )

    pairs = list(zip(modules[::3], modules[1::3], modules[2::3]))
    i = 0
    for m in pairs:
        for _ in m:
            i += 1
    if len(modules) - i == 1:
        pairs.append((modules[-1],))
    elif len(modules) - i == 2:
        pairs.append(
            (
                modules[-2],
                modules[-1],
            )
        )

    COLUMN_SIZE = 4

    max_num_pages = ceil(len(pairs) / COLUMN_SIZE)
    modulo_page = page_n % max_num_pages

    # can only have a certain amount of buttons side by side
    if len(pairs) > COLUMN_SIZE:
        pairs = pairs[modulo_page * COLUMN_SIZE : COLUMN_SIZE * (modulo_page + 1)] + [
            (
                EqInlineKeyboardButton(
                    "❮", callback_data=f"{prefix}_prev({modulo_page})"
                ),
                EqInlineKeyboardButton(
                    "Back", callback_data=f"{prefix}_home({modulo_page})"
                ),
                EqInlineKeyboardButton(
                    "❯", callback_data=f"{prefix}_next({modulo_page})"
                ),
            )
        ]

    return pairs


def is_module_loaded(name):
    return (not MOD_LOAD or name in MOD_LOAD) and name not in MOD_NOLOAD
