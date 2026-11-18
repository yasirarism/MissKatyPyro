import time

GAP = {}


async def check_time_gap(user_id: int):

    if str(user_id) in GAP:
        current_time = time.time()
        previous_time = GAP[str(user_id)]
        if round(current_time - previous_time) < 10:
            return True, round(previous_time - current_time + 10)
        del GAP[str(user_id)]
    else:
        GAP[str(user_id)] = time.time()
    return False, None
