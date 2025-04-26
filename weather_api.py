import requests
from datetime import datetime, timedelta

def get_weather(city: str, api_key: str):
    """
    Возвращает список словарей с прогнозом на 3 дня:
    [
      {'day': 'Среда', 'date': '25.04.2025', 'temp_day': 18, 'temp_night': 7},
      ...
    ]
    """
    # Отладочный вывод для проверки ключа и URL
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}&appid={api_key}&units=metric&lang=ru&cnt=24"
    )
    print(f"[DBG] WEATHER_API_KEY = {api_key}")
    print(f"[DBG] URL = {url}")

    try:
        res = requests.get(url)
    except Exception as e:
        print(f"[DBG] Request exception: {e}")
        return None

    print(f"[DBG] status_code = {res.status_code}")
    print(f"[DBG] response = {res.text[:200]}...")

    if res.status_code != 200:
        return None

    data = res.json()
    daily = {}
    for entry in data.get('list', []):
        d = datetime.fromtimestamp(entry['dt']).date()
        daily.setdefault(d, []).append(entry['main']['temp'])

    result = []
    today = datetime.now().date()
    for i, (date, temps) in enumerate(daily.items()):
        if i >= 3:
            break
        result.append({
            'day': (today + timedelta(days=i)).strftime('%A'),
            'date': date.strftime('%d.%m.%Y'),
            'temp_day': round(max(temps)),
            'temp_night': round(min(temps))
        })
    return result
