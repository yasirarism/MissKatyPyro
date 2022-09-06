SIZE_UNITS = ["B", "KB", "MB", "GB", "TB", "PB"]


def get_readable_file_size(size_in_bytes) -> str:
    if size_in_bytes is None:
        return "0B"
    index = 0
    while size_in_bytes >= 1024:
        size_in_bytes /= 1024
        index += 1
    try:
        return f"{round(size_in_bytes, 2)}{SIZE_UNITS[index]}"
    except IndexError:
        return "File too large"


def get_readable_time(seconds: int) -> str:
    result = ""
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f"{days} hari "
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f"{hours} jam "
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f"{minutes} menit "
    seconds = int(seconds)
    result += f"{seconds} detik "
    return result


def get_readable_time2(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["detik", "menit", "jam", "hari", "minggu", "bulan", "tahun"]
    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for i in range(len(time_list)):
        time_list[i] = str(time_list[i]) + time_suffix_list[i]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "
    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time
