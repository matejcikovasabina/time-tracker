def format_duration(seconds: float) -> str:
    total_seconds = int(seconds) 

    minutes, sec = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)

    return f"{hours:02d}:{minutes:02d}:{sec:02d}"
