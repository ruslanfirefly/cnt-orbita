#!/usr/bin/env python3
"""
Скрипт мониторинга плановых отключений электроэнергии для СНТ «Орбита».
Получает данные с официального сайта «Россети Ленэнерго» и сохраняет их в JSON
для Hugo и клиентского JavaScript-баннера на главной странице.

Может запускаться как локально при сборке, так и по CRON на хостинге (Reg.ru / ISPmanager).
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
    table_match = re.search(r'<table[^>]*>(.*?)</table>', html_content, re.DOTALL | re.IGNORECASE)
    if not table_match:
        return []

    table_html = table_match.group(1)
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL | re.IGNORECASE)
    if len(rows) <= 1:
        return []

    results = []
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

        is_our_orbita = False
        if "тер. СНТ Орбита" in address or "тер СНТ Орбита" in address or "СНТ «Орбита»" in address:
            is_our_orbita = True
        elif "Орбита" in address and "Волковицы" not in address:
            is_our_orbita = True

        if not is_our_orbita:
            continue

        dt_end = None
        dt_start = None
        try:
            dt_end = datetime.strptime(date_end_str.strip(), "%d-%m-%Y, %H:%M")
        except Exception:
            pass

        try:
            dt_start = datetime.strptime(date_start_str.strip(), "%d-%m-%Y, %H:%M")
        except Exception:
            pass

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
        "past": past[:5]
    }
    return payload

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Обновление данных графика отключений Россети Ленэнерго")
    parser.add_argument("--file", help="Путь к локальному HTML-файлу для парсинга (тестирование)")
    parser.add_argument("--output", "-o", help="Прямой путь для сохранения outages.json")
    args = parser.parse_args()

    try:
        html = fetch_html(URL, local_file=args.file)
    except Exception as e:
        print(f"Ошибка получения данных: {e}", file=sys.stderr)
        return 1

    parsed = parse_outages_table(html)
    data = process_outages(parsed)
    json_str = json.dumps(data, ensure_ascii=False, indent=2)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))

    targets = []
    if args.output:
        targets.append(args.output)
    else:
        # 1. Основной путь: data/outages.json (работает и в корне репозитория, и в корне веб-сервера /www/cnt-orbita.ru/)
        targets.append(os.path.join(project_root, "data", "outages.json"))

        # 2. Если есть static/data (локальный репозиторий Hugo), также обновляем его
        static_data_dir = os.path.join(project_root, "static", "data")
        if os.path.isdir(static_data_dir) or os.path.isdir(os.path.join(project_root, "content")):
            targets.append(os.path.join(static_data_dir, "outages.json"))

    for target_path in targets:
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(json_str + "\n")
        print(f"Записано: {target_path}")

    print(f"Статус: hasOutage={data['hasOutage']}")
    if data["hasOutage"]:
        o = data["activeOutage"]
        print(f"Ближайшее отключение: {o.get('displayDate')} ({o.get('timeInterval')}) — {o.get('duration')}")
    else:
        print("В ближайшее время плановых отключений не запланировано.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
