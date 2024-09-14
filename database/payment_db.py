from database import dbname

autopay = dbname["autpay"]


async def delete_autopay(uniqueCode: str):
    await autopay.delete_one({"_id": uniqueCode})

async def get_autopay(self, uniqueCode: str):
    exists = await autopay.find_one({"_id": uniqueCode})
    return exists

async def autopay_update(self, msg_id: Optional[int] = "", note: Optional[str] = "", user_id: Optional[int] = "", amount: Optional[int] = "", status: Optional[str] = "", uniqueCode: Optional[str] = "", createdAt: Optional[str] = ""):
    data = {"msg_id": msg_id, "note": note, "user_id": user_id, "amount": amount, "status": status, "createdAt": createdAt}
    await autopay.update_one({"_id": uniqueCode}, {"$set": data}, upsert=True)