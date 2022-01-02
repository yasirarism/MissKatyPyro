import time

GAP = {}


async def check_time_gap(user_id: int):
    """A Function for checking user time gap!
    :parameter user_id Telegram User ID"""

    if str(user_id) in GAP:
        current_time = time.time()
        previous_time = GAP[str(user_id)]
        if round(current_time - previous_time) < 120:
            return True, round(previous_time - current_time + 120)
        elif round(current_time - previous_time) >= 120:
            del GAP[str(user_id)]
            return False, None
    elif str(user_id) not in GAP:
        GAP[str(user_id)] = time.time()
        return False, None
