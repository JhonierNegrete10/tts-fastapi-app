from datetime import datetime
# Función para formatear la fecha y hora
def format_datetime(dt_str: str) -> str:
    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    return dt.strftime("%Y-%m-%d %H:%M:%S")
