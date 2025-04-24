import requests
from datetime import datetime, timedelta

def get_weather(city, api_key):
    url = (
        f"http://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}&appid={api_key}&units=metric&lang=ru&cnt=24"
    )
    res = requests.get(url)
    if res.status_code != 200:
        return None

    data = res.json()
    daily = {}
    for entry in data['list']:
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
