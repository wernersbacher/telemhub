def increment_without_error(num: int) -> int:
    num_int = 0
    try:
        num_int = int(num)
    except Exception:
        pass
    return num_int+1
