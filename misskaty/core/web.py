"""FastAPI app used for webhooks (autopay callback) and the /status page."""

import hashlib
from asyncio import create_subprocess_shell, subprocess
from contextlib import suppress
from datetime import datetime, timedelta
from logging import ERROR, getLogger
from os import path
from time import time

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from psutil import boot_time, disk_usage, net_io_counters
from pytz import timezone as zones
from starlette.exceptions import HTTPException

api = FastAPI()

LOGGER = getLogger(__name__)
getLogger("fastapi").setLevel(ERROR)

botStartTime = time()

# Commit date is expensive to compute (spawns a subprocess), so cache it
# and only refresh every COMMIT_CACHE_TTL seconds.
COMMIT_CACHE_TTL = 600
_commit_cache = {"ts": 0.0, "value": ""}


async def _get_commit_date() -> str:
    now = time()
    if now - _commit_cache["ts"] < COMMIT_CACHE_TTL:
        return _commit_cache["value"]

    value = "No UPSTREAM_REPO"
    if path.exists(".git"):
        try:
            proc = await create_subprocess_shell(
                "git log -1 --date=format:'%y/%m/%d %H:%M' --pretty=format:'%cd'",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            stdout, _ = await proc.communicate()
            value = stdout.decode().strip() or value
        except Exception as e:
            LOGGER.warning("Failed to read git commit date: %s", e)

    _commit_cache.update(ts=now, value=value)
    return value


@api.post("/callback")
async def autopay(request: Request):
    from database.payment_db import delete_autopay, get_autopay
    from misskaty import app
    from misskaty.vars import OWNER_ID, PAYDISINI_KEY

    data = await request.form()
    client_ip = request.client.host
    if PAYDISINI_KEY != data["key"] and client_ip != "194.233.92.170":
        raise HTTPException(status_code=403, detail="Access forbidden")
    signature_data = f"{PAYDISINI_KEY}{data['unique_code']}CallbackStatus"
    gen_signature = hashlib.md5(signature_data.encode()).hexdigest()
    if gen_signature != data["signature"]:
        raise HTTPException(status_code=403, detail="Invalid Signature")
    unique_code = data["unique_code"]
    status = data["status"]
    exp_date = (datetime.now(zones("Asia/Jakarta")) + timedelta(days=30)).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    r = await get_autopay(unique_code)
    msg = (
        f"╭────〔 <b>TRANSAKSI SUKSES🎉</b> 〕──\n"
        f"│・ <b>Transaksi ID :</b> {unique_code}\n"
        f"│・ <b>Product :</b> MissKaty Support by YS Dev\n"
        f"│・ <b>Durasi :</b> 30 hari\n"
        f"│・ <b>Total Dibayar :</b> {r.get('amount')}\n"
        f"│・ Langganan Berakhir: {exp_date}\n"
        f"╰─────────"
    )
    if not r:
        return JSONResponse({"status": False, "data": "Data not found on DB"}, 404)
    if status == "Success":
        with suppress(Exception):
            await app.send_message(
                r.get("user_id"), f"{msg}\n\nJika ada pertanyaan silahkan hubungi pemilik bot ini."
            )
            await app.delete_messages(r.get("user_id"), r.get("msg_id"))
        await app.send_message(OWNER_ID, msg)
        await delete_autopay(unique_code)
        return JSONResponse(
            {"status": status, "msg": "Pesanan berhasil dibayar oleh customer."}, 200
        )
    else:
        with suppress(Exception):
            await app.send_message(
                r.get("user_id"), "QRIS Telah Expired, Silahkan Buat Transaksi Baru."
            )
            await app.delete_messages(r.get("user_id"), r.get("msg_id"))
        await delete_autopay(unique_code)
        return JSONResponse(
            {"status": status, "msg": "Pesanan telah dibatalkan/gagal dibayar."}, 403
        )


@api.get("/status")
async def status():
    from misskaty.helper.human_read import get_readable_file_size, get_readable_time

    bot_uptime = get_readable_time(time() - botStartTime)
    uptime = get_readable_time(time() - boot_time())
    sent = get_readable_file_size(net_io_counters().bytes_sent)
    recv = get_readable_file_size(net_io_counters().bytes_recv)
    commit_date = await _get_commit_date()
    return {
        "commit_date": commit_date,
        "uptime": uptime,
        "on_time": bot_uptime,
        "free_disk": get_readable_file_size(disk_usage(".").free),
        "total_disk": get_readable_file_size(disk_usage(".").total),
        "network": {
            "sent": sent,
            "recv": recv,
        },
    }


@api.api_route("/")
async def homepage():
    return "Hello World"


@api.exception_handler(HTTPException)
async def page_not_found(request: Request, exc: HTTPException):
    return HTMLResponse(content=f"<h1>Error: {exc}</h1>", status_code=exc.status_code)
