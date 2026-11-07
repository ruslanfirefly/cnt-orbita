#!/usr/bin/env python3
"""
Скрипт мониторинга плановых отключений электроэнергии для СНТ «Орбита».
Получает данные с официального сайта «Россети Ленэнерго» и сохраняет их в JSON
для Hugo и клиентского JavaScript-баннера на главной странице.
"""

import sys
import os
import re
import json
import urllib.request
import urllib.error
from datetime import datetime

URL = "https://rosseti-lenenergo.ru/clients/planned_work/?reg=5&res=59&street=%D1%82%D0%B5%D1%80.+%D0%A1%D0%9D%D0%A2+%D0%9E%D1%80%D0%B1%D0%B8%D1%82%D0%B0&date_start=&date_finish="
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def fetch_html(url, local_file=None):
    if local_file and os.path.exists(local_file):
        with open(local_file, "r", encoding="utf-8") as f:
            return f.read()

    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")

def parse_outages_table(html_content):
    """
    Парсит HTML-таблицу графика плановых отключений Россети Ленэнерго.
    """
    table_match = re.search(r'<table[^>]*>(.*?)</table>', html_content, re.DOTALL | re.IGNORECASE)
    if not table_match:
        return []

    table_html = table_match.group(1)
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL | re.IGNORECASE)
    if len(rows) <= 1:
        return []

    results = []
    # Столбцы: 0-Регион/район, 1-Адрес, 2-Дата отключения, 3-Дата восстановления, 4-Филиал, 5-РЭС, 6-Комментарий, 7-ФИАС
    for r in rows[1:]:
        cols = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.DOTALL | re.IGNORECASE)
        clean_cols = [' '.join(re.sub(r'<[^>]+>', ' ', c).split()) for c in cols]
        if len(clean_cols) < 4:
            continue

        address = clean_cols[1] if len(clean_cols) > 1 else ""
        date_start_str = clean_cols[2] if len(clean_cols) > 2 else ""
        date_end_str = clean_cols[3] if len(clean_cols) > 3 else ""
        filial = clean_cols[4] if len(clean_cols) > 4 else ""
        res = clean_cols[5] if len(clean_cols) > 5 else ""
        comment = clean_cols[6] if len(clean_cols) > 6 else ""
        fias = clean_cols[7] if len(clean_cols) > 7 else ""

        # Проверяем, относится ли запись именно к СНТ «Орбита» (и исключаем посторонние вроде «Орбита-3» в Волковицах)
        is_our_orbita = False
        if "тер. СНТ Орбита" in address or "тер СНТ Орбита" in address or "СНТ «Орбита»" in address:
            is_our_orbita = True
        elif "Орбита" in address and "Волковицы" not in address:
            is_our_orbita = True

        if not is_our_orbita:
            continue

        # Парсим дату окончания работ
        dt_end = None
        dt_start = None
        try:
            # Формат даты: 10-11-2026, 18:00
            dt_end = datetime.strptime(date_end_str.strip(), "%d-%m-%Y, %H:%M")
        except Exception:
            pass

        try:
            dt_start = datetime.strptime(date_start_str.strip(), "%d-%m-%Y, %H:%M")
        except Exception:
            pass

        # Форматируем дату для отображения
        display_date = date_start_str.split(",")[0].replace("-", ".") if date_start_str else ""
        time_interval = ""
        if dt_start and dt_end:
            time_interval = f"{dt_start.strftime('%H:%M')} – {dt_end.strftime('%H:%M')}"
        elif date_start_str and date_end_str:
            t1 = date_start_str.split(",")[-1].strip() if "," in date_start_str else date_start_str
            t2 = date_end_str.split(",")[-1].strip() if "," in date_end_str else date_end_str
            time_interval = f"{t1} – {t2}"

        results.append({
            "address": address,
            "dateStart": date_start_str,
            "dateEnd": date_end_str,
            "dateStartIso": dt_start.isoformat() if dt_start else "",
            "dateEndIso": dt_end.isoformat() if dt_end else "",
            "displayDate": display_date,
            "timeInterval": time_interval,
            "filial": filial,
            "res": res,
            "duration": comment,
            "fias": fias,
            "_dt_end": dt_end
        })

    return results

def process_outages(parsed_items, now=None):
    if now is None:
        now = datetime.now()

    upcoming = []
    past = []

    for item in parsed_items:
        dt_end = item.get("_dt_end")
        clean_item = {k: v for k, v in item.items() if not k.startswith("_")}
        if dt_end and dt_end < now:
            past.append(clean_item)
        else:
            upcoming.append(clean_item)

    # Сортируем предстоящие по дате
    upcoming.sort(key=lambda x: x.get("dateStartIso", ""))

    has_outage = len(upcoming) > 0
    active_outage = upcoming[0] if has_outage else None

    payload = {
        "updatedAt": now.isoformat(timespec="seconds"),
        "checkedAt": now.strftime("%d.%m.%Y %H:%M"),
        "sourceUrl": URL,
        "organization": "ПАО «Россети Ленэнерго»",
        "res": "Красносельский РЭС",
        "hasOutage": has_outage,
        "activeOutage": active_outage,
        "upcoming": upcoming,
        "past": past[:5]  # сохраняем последние 5 для истории
    }
    return payload

def main():
    local_file = None
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        local_file = sys.argv[1]

    try:
        html = fetch_html(URL, local_file=local_file)
    except Exception as e:
        print(f"Ошибка получения страницы: {e}", file=sys.stderr)
        return 1

    parsed = parse_outages_table(html)
    data = process_outages(parsed)

    # Определяем пути для записи
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))

    data_dir = os.path.join(project_root, "data")
    static_data_dir = os.path.join(project_root, "static", "data")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(static_data_dir, exist_ok=True)

    data_json_path = os.path.join(data_dir, "outages.json")
    static_json_path = os.path.join(static_data_dir, "outages.json")

    json_str = json.dumps(data, ensure_ascii=False, indent=2)

    with open(data_json_path, "w", encoding="utf-8") as f:
        f.write(json_str + "\n")

    with open(static_json_path, "w", encoding="utf-8") as f:
        f.write(json_str + "\n")

    print(f"Успешно обновлено: hasOutage={data['hasOutage']}")
    if data["hasOutage"]:
        o = data["activeOutage"]
        print(f"Ближайшее отключение: {o.get('displayDate')} ({o.get('timeInterval')}) — {o.get('duration')}")
    else:
        print("Плановых отключений в ближайшее время не обнаружено.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
