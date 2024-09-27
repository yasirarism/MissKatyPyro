from logging import INFO, StreamHandler, basicConfig, getLogger, ERROR, handlers
from os import path
from time import time
from datetime import datetime, timedelta

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.exceptions import HTTPException
from psutil import boot_time, disk_usage, net_io_counters
from contextlib import suppress
from asyncio import to_thread, subprocess, create_subprocess_shell
from apscheduler.triggers.date import DateTrigger
from pytz import timezone as zones
import hashlib

api = FastAPI()

basicConfig(
    level=INFO,
    format="[%(levelname)s] - [%(asctime)s - %(name)s - %(message)s] -> [%(module)s:%(lineno)d]",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        handlers.RotatingFileHandler(
            "MissKatyLogs.txt", mode="w+", maxBytes=5242880, backupCount=1
        ),
        StreamHandler(),
    ],
)
botStartTime = time()

LOGGER = getLogger(__name__)
getLogger("fastapi").setLevel(ERROR)

@api.post("/callback")
async def autopay(request: Request):
    from misskaty import app
    from database.payment_db import delete_autopay, get_autopay
    from misskaty.vars import PAYDISINI_KEY, OWNER_ID
    data = await request.form()
    client_ip = request.client.host
    if PAYDISINI_KEY != data["key"] and client_ip != "194.233.92.170":
        raise HTTPException(status_code=403, detail="Access forbidden")
    signature_data = f"{PAYDISINI_KEY}{data['unique_code']}CallbackStatus"
    gen_signature = hashlib.md5(signature_data.encode()).hexdigest()
    if gen_signature != data["signature"]:
        raise HTTPException(status_code=403, detail="Invalid Signature")
    unique_code = data['unique_code']
    status = data['status']
    exp_date = (datetime.now(zones("Asia/Jakarta")) + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    r = await get_autopay(unique_code)
    msg = f"╭────〔 <b>TRANSAKSI SUKSES🎉</b> 〕──\n│・ <b>Transaksi ID :</b> {unique_code}\n│・ <b>Product :</b> MissKaty Support by YS Dev\n│・ <b>Durasi :</b> 30 hari\n│・ <b>Total Dibayar :</b> {r.get('amount')}\n│・ Langganan Berakhir: {exp_date}\n╰─────────"
    if not r:
        return JSONResponse({"status": false, "data": "Data not found on DB"}, 404)
    if status == "Success":
        with suppress(Exception):
            await app.send_message(r.get("user_id"), f"{msg}\n\nJika ada pertanyaan silahkan hubungi pemilik bot ini.")
            await app.delete_messages(r.get("user_id"), r.get("msg_id"))
        await app.send_message(OWNER_ID, msg)
        await delete_autopay(unique_code)
        return JSONResponse({"status": status, "msg": "Pesanan berhasil dibayar oleh customer."}, 200)
    else:
        with suppress(Exception):
            await app.send_message(r.get("user_id"), "QRIS Telah Expired, Silahkan Buat Transaksi Baru.")
            await app.delete_messages(r.get("user_id"), r.get("msg_id"))
        await delete_autopay(unique_code)
        return JSONResponse({"status": status, "msg": "Pesanan telah dibatalkan/gagal dibayar."}, 403)

@api.get("/status")
async def status():
    from misskaty.helper.human_read import get_readable_file_size, get_readable_time
    bot_uptime = get_readable_time(time() - botStartTime)
    uptime = get_readable_time(time() - boot_time())
    sent = get_readable_file_size(net_io_counters().bytes_sent)
    recv = get_readable_file_size(net_io_counters().bytes_recv)
    if path.exists(".git"):
        commit_date = (await (await create_subprocess_shell("git log -1 --date=format:'%y/%m/%d %H:%M' --pretty=format:'%cd'", stdout=subprocess.PIPE, stderr=subprocess.STDOUT)).communicate())[0].decode()
    else:
        commit_date = "No UPSTREAM_REPO"
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
