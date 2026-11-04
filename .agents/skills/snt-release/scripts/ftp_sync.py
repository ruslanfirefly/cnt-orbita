#!/usr/bin/env python3
"""
Скрипт синхронизации статического сайта Hugo по FTP.
Зеркалирует каталог public/ на удаленный FTP-сервер с удалением устаревших файлов.
Использует встроенную библиотеку ftplib (без внешних зависимостей).
"""

import os
import sys
import ftplib
import posixpath
import argparse
from pathlib import Path


def load_config(config_path):
    config = {}
    if not os.path.exists(config_path):
        return config
    with open(config_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                config[key.strip()] = val.strip().strip('"').strip("'")
    return config


class FTPSync:
    def __init__(self, host, port, user, passwd, remote_base_dir, local_base_dir, dry_run=False):
        self.host = host
        self.port = int(port)
        self.user = user
        self.passwd = passwd
        self.remote_base = remote_base_dir.rstrip("/")
        self.local_base = Path(local_base_dir).resolve()
        self.dry_run = dry_run
        self.ftp = None
        self.uploaded_count = 0
        self.deleted_count = 0

    def connect(self):
        if self.ftp:
            try:
                self.ftp.quit()
            except Exception:
                pass
        self.ftp = ftplib.FTP()
        self.ftp.connect(self.host, self.port, timeout=30)
        self.ftp.login(self.user, self.passwd)
        self.ftp.set_pasv(True)
        try:
            self.ftp.sendcmd("OPTS UTF8 ON")
        except Exception:
            pass

    def ensure_connection(self):
        try:
            self.ftp.voidcmd("NOOP")
        except Exception:
            print("🔄 Переподключение к FTP...")
            self.connect()

    def get_remote_tree(self):
        """Рекурсивно получает список всех удаленных файлов и папок через MLS."""
        remote_files = {}  # rel_path -> size
        remote_dirs = set()

        def scan_dir(r_dir, rel_prefix):
            self.ensure_connection()
            try:
                entries = list(self.ftp.mlsd(r_dir))
            except Exception as e:
                print(f"⚠️ Ошибка чтения директории {r_dir}: {e}")
                return

            for name, facts in entries:
                if name in (".", ".."):
                    continue
                f_type = facts.get("type")
                rel_p = posixpath.join(rel_prefix, name) if rel_prefix else name
                full_p = posixpath.join(r_dir, name)

                if f_type == "dir":
                    remote_dirs.add(rel_p)
                    scan_dir(full_p, rel_p)
                elif f_type == "file":
                    try:
                        sz = int(facts.get("size", -1))
                    except (ValueError, TypeError):
                        sz = -1
                    remote_files[rel_p] = sz

        base = self.remote_base if self.remote_base else "/"
        scan_dir(base, "")
        return remote_files, remote_dirs

    def ensure_remote_dir(self, remote_dir):
        if not remote_dir or remote_dir == "/":
            return
        parts = remote_dir.strip("/").split("/")
        current = ""
        for part in parts:
            current += "/" + part
            self.ensure_connection()
            try:
                self.ftp.cwd(current)
            except ftplib.error_perm:
                try:
                    self.ftp.mkd(current)
                except ftplib.error_perm:
                    pass

    def sync(self):
        print(f"🔌 Подключение к FTP {self.host}:{self.port}...")
        self.connect()
        print(f"✅ Авторизация успешна! (Режим: {'DRY-RUN (симуляция)' if self.dry_run else 'БОЕВОЙ ДЕПЛОЙ'})")

        # 1. Сканирование локальных файлов
        local_files = {}
        local_dirs = set()
        for root, dirs, files in os.walk(self.local_base):
            for d in dirs:
                rel_d = os.path.relpath(os.path.join(root, d), self.local_base).replace("\\", "/")
                local_dirs.add(rel_d)
            for f in files:
                full_path = os.path.join(root, f)
                rel_f = os.path.relpath(full_path, self.local_base).replace("\\", "/")
                local_files[rel_f] = os.path.getsize(full_path)

        print(f"📂 Локальных файлов для синхронизации: {len(local_files)}")

        # 2. Сканирование сервера
        print("🔍 Сканирование удаленного сервера...")
        remote_files, remote_dirs = self.get_remote_tree()
        print(f"📡 На сервере найдено файлов: {len(remote_files)}, папок: {len(remote_dirs)}")

        # 3. Удаление устаревших файлов
        files_to_delete = [rf for rf in remote_files if rf not in local_files]
        if files_to_delete:
            print(f"🗑 Удаление устаревших файлов ({len(files_to_delete)} шт.)...")
            for rf in files_to_delete:
                full_r_path = posixpath.join(self.remote_base, rf) if self.remote_base else "/" + rf
                if self.dry_run:
                    print(f"   [DRY-RUN] Удаление файла: {full_r_path}")
                else:
                    self.ensure_connection()
                    try:
                        self.ftp.delete(full_r_path)
                        self.deleted_count += 1
                    except Exception as e:
                        print(f"   ⚠️ Ошибка при удалении {full_r_path}: {e}")

        # Удаление устаревших пустых папок (в обратном порядке)
        dirs_to_delete = sorted([rd for rd in remote_dirs if rd not in local_dirs], reverse=True)
        if dirs_to_delete:
            for rd in dirs_to_delete:
                full_r_dir = posixpath.join(self.remote_base, rd) if self.remote_base else "/" + rd
                if self.dry_run:
                    print(f"   [DRY-RUN] Удаление директории: {full_r_dir}")
                else:
                    self.ensure_connection()
                    try:
                        self.ftp.rmd(full_r_dir)
                    except Exception:
                        pass

        # 4. Загрузка новых и изменившихся файлов
        files_to_upload = []
        for rel_f, local_sz in local_files.items():
            remote_sz = remote_files.get(rel_f)
            if remote_sz != local_sz:
                files_to_upload.append(rel_f)

        print(f"⬆️ Файлов к загрузке/обновлению: {len(files_to_upload)} из {len(local_files)}")

        base = self.remote_base if self.remote_base else ""
        for i, rel_f in enumerate(files_to_upload, 1):
            local_full_p = self.local_base / rel_f
            remote_full_p = posixpath.join(base, rel_f) if base else "/" + rel_f
            remote_parent_dir = posixpath.dirname(remote_full_p)

            if self.dry_run:
                print(f"   [DRY-RUN] Загрузка: {rel_f}")
                self.uploaded_count += 1
                continue

            self.ensure_remote_dir(remote_parent_dir)

            for attempt in range(3):
                try:
                    self.ensure_connection()
                    with open(local_full_p, "rb") as fp:
                        self.ftp.storbinary(f"STOR {remote_full_p}", fp)
                    self.uploaded_count += 1
                    if i % 20 == 0 or i == len(files_to_upload):
                        print(f"   Загружено: {i}/{len(files_to_upload)}...")
                    break
                except Exception as e:
                    if attempt == 2:
                        print(f"   ❌ Сбой при загрузке {rel_f}: {e}")
                    else:
                        print(f"   ⚠️ Повторная попытка для {rel_f}...")
                        self.connect()

        try:
            self.ftp.quit()
        except Exception:
            pass

        print("\n" + "=" * 45)
        print(f"🎉 Синхронизация {'(симуляция) ' if self.dry_run else ''}завершена!")
        print(f"   Загружено/обновлено: {self.uploaded_count} файлов")
        print(f"   Удалено устаревших:  {self.deleted_count if not self.dry_run else len(files_to_delete)} файлов")
        print("=" * 45)


def main():
    parser = argparse.ArgumentParser(description="FTP Deployer for Hugo")
    parser.add_argument("--dry-run", action="store_true", help="Симуляция без реальных изменений")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[4]
    config_file = repo_root / ".deploy_config"
    cfg = load_config(config_file)

    host = cfg.get("REMOTE_HOST", "")
    port = cfg.get("REMOTE_PORT", "21")
    user = cfg.get("REMOTE_USER", "")
    passwd = cfg.get("REMOTE_PASSWORD", "")
    remote_path = cfg.get("REMOTE_PATH", "")

    if not host or not user or not passwd:
        print("❌ Ошибка: В .deploy_config должны быть указаны REMOTE_HOST, REMOTE_USER и REMOTE_PASSWORD!", file=sys.stderr)
        sys.exit(1)

    local_dir = repo_root / "public"
    if not local_dir.is_dir():
        print(f"❌ Каталог {local_dir} не найден. Сначала запустите сборку Hugo!", file=sys.stderr)
        sys.exit(1)

    syncer = FTPSync(host, port, user, passwd, remote_path, local_dir, dry_run=args.dry_run)
    syncer.sync()


if __name__ == "__main__":
    main()
