import re
from math import ceil

from pyrogram.types import InlineKeyboardButton

from misskaty import HELPABLE, MOD_LOAD, MOD_NOLOAD


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
    else:
        pairs = pairs[modulo_page * COLUMN_SIZE : COLUMN_SIZE * (modulo_page + 1)] + [
            (
                EqInlineKeyboardButton(
                    "Back", callback_data=f"{prefix}_home({modulo_page})"
                ),
            )
        ]

    return pairs


def is_module_loaded(name):
    return (not MOD_LOAD or name in MOD_LOAD) and name not in MOD_NOLOAD


def _parse_help_lines(help_text: str) -> list[tuple[str, str]]:
    lines = help_text.strip().split("\n")
    pairs = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"^(.+?)\s+-\s+(.+)$", line)
        if not m:
            m2 = re.match(r"^(/\S+)$", line)
            if m2:
                pairs.append((m2.group(1), ""))
            continue
        cmd_part, desc = m.group(1).strip(), m.group(2).strip()
        cmd = re.sub(r"\s*\|\s*", " / ", cmd_part)
        pairs.append((cmd, desc))
    return pairs


def build_help_table(help_text: str, *, title: str = "") -> str:
    pairs = _parse_help_lines(help_text)
    if not pairs:
        return ""
    rows = "".join(
        f"<tr><td><code>{cmd}</code></td><td>{desc or '—'}</td></tr>\n"
        for cmd, desc in pairs
    )
    cap = f"<caption>📋 {title}</caption>\n" if title else ""
    return (
        f"<table bordered striped>\n{cap}"
        f"<tr><td><b>Command</b></td><td><b>Description</b></td></tr>\n"
        f"{rows}</table>"
    )


def build_module_list_table() -> str:
    modules = sorted(HELPABLE.values(), key=lambda m: m.__MODULE__.lower())
    if not modules:
        return ""
    rows = []
    for mod in modules:
        name = mod.__MODULE__
        raw = (mod.__HELP__ or "").strip()
        first_line = ""
        for ln in raw.split("\n"):
            ln = ln.strip()
            if ln and not ln.startswith("/"):
                first_line = ln
                break
        if not first_line:
            first_line = raw.split("\n")[0].strip() if raw else "—"
        desc = re.sub(r"<[^>]+>", "", first_line)[:80]
        rows.append(
            f"<tr><td><code>/{name.lower()}</code></td><td>{desc}</td></tr>\n"
        )
    return (
        "<table bordered striped>\n"
        "<caption>📚 Semua Module</caption>\n"
        "<tr><td><b>Module</b></td><td><b>Description</b></td></tr>\n"
        + "".join(rows)
        + "</table>"
    )


import asyncio


async def run_sync(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
