#!/usr/bin/env python3
"""Точка входа: саммари папки Google Drive."""

import argparse
import logging
import sys
from pathlib import Path

from src.config import (
    CACHE_DIR,
    GOOGLE_CREDENTIALS_PATH,
    GOOGLE_DRIVE_FOLDER_ID,
    PROJECT_ROOT,
    check_api_key,
    ensure_cache_dirs,
)


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--verbose", "-v", action="store_true", help="Подробный вывод")
    parser.add_argument("--cache-dir", default=None, help="Путь к кешу")
    parser.add_argument("--max-files", type=int, default=None, help="Лимит файлов для теста")


def cmd_ingest(args: argparse.Namespace) -> None:
    """Команда ingest — скачать файлы из папки."""
    from src.sources import ingest

    credentials = Path(args.credentials or PROJECT_ROOT / GOOGLE_CREDENTIALS_PATH)
    folder_id = args.folder_id or GOOGLE_DRIVE_FOLDER_ID
    try:
        files = ingest(folder_id, credentials, force=args.force)
        files = files[: args.max_files] if args.max_files else files
        downloaded = sum(1 for f in files if f.local_path)
        print(f"Обработано: {len(files)} файлов, скачано: {downloaded}")
        for f in files:
            status = "✓" if f.local_path else "✗"
            print(f"  {status} {f.path} ({f.mime_type})")
    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
        print("Положите credentials.json в корень проекта.")
    except Exception as e:
        print(f"Ошибка: {e}")


def cmd_summarize(args: argparse.Namespace) -> None:
    """Команда summarize — прогнать саммаризацию."""
    from src.pipelines.run import run_summarize, save_summary_result
    from src.storage.load_cached import load_cached_files

    if not check_api_key():
        print("⚠️  Задайте OPENROUTER_API_KEY в .env")
        return

    ensure_cache_dirs()
    files = load_cached_files(max_files=args.max_files)
    if not files:
        print("Нет файлов в кеше. Сначала выполните: python main.py ingest")
        return

    print(f"Саммаризация {len(files)} файлов...")
    result = run_summarize(files, max_files=args.max_files, progress=True)
    save_summary_result(result)
    failed = result.get("failed", [])
    if failed:
        print(f"\n⚠️  Не обработано {len(failed)} файлов:")
        for f in failed[:10]:
            print(f"  — {f['path']}: {f['reason']}")
        if len(failed) > 10:
            print(f"  ... и ещё {len(failed) - 10}")
        print(f"Подробности: .cache/errors.log")
    print(f"\nГотово. Результат: .cache/summary_result.json")
    print(f"Global summary: {result['global_summary'][:200]}...")


def cmd_report(args: argparse.Namespace) -> None:
    """Команда report — собрать отчёт (--format md|json, --output)."""
    from src.report import build_report, build_report_json, build_report_md
    from src.pipelines.run import load_summary_result

    result = load_summary_result()
    if not result:
        print("Нет результата саммаризации. Сначала: python main.py ingest && python main.py summarize")
        return

    report = build_report(
        global_summary=result["global_summary"],
        doc_summaries=result.get("doc_summaries", []),
        files_meta=result.get("files_meta", []),
    )

    fmt = (args.format or "md").lower()
    if fmt == "json":
        out = build_report_json(report)
    else:
        out = build_report_md(report, folder_name=args.folder_name or "")

    output = Path(args.output) if args.output else None
    if output:
        output.write_text(out, encoding="utf-8")
        print(f"Отчёт сохранён: {output}")
    else:
        print(out)


def cmd_run(args: argparse.Namespace) -> None:
    """Один запуск: ingest → summarize → report."""
    ensure_cache_dirs()
    args.force = getattr(args, "force", False)
    args.credentials = getattr(args, "credentials", None)
    args.folder_id = getattr(args, "folder_id", None)
    cmd_ingest(args)
    cmd_summarize(args)
    args.format = getattr(args, "format", "md")
    args.output = getattr(args, "output", Path("summary.md"))
    args.folder_name = getattr(args, "folder_name", "")
    cmd_report(args)


def main() -> None:
    parser = argparse.ArgumentParser(description="Саммари папки Google Drive")
    _add_common_args(parser)
    subparsers = parser.add_subparsers(dest="cmd", help="Команда")

    # ingest
    p_ingest = subparsers.add_parser("ingest", help="Скачать файлы из папки")
    p_ingest.add_argument("--folder-id", default=None, help="ID папки Drive")
    p_ingest.add_argument("--credentials", default=None, help="Путь к credentials.json")
    p_ingest.add_argument("--force", action="store_true", help="Перекачать даже без изменений")
    _add_common_args(p_ingest)
    p_ingest.set_defaults(func=cmd_ingest)

    # summarize
    p_sum = subparsers.add_parser("summarize", help="Прогнать саммаризацию")
    p_sum.add_argument("--mode", choices=["fast", "deep"], default="fast", help="Режим: fast или deep")
    p_sum.add_argument("--resume", action="store_true", help="Использовать кеш LLM (пропуск пересчёта)")
    _add_common_args(p_sum)
    p_sum.set_defaults(func=cmd_summarize)

    # report
    p_rep = subparsers.add_parser("report", help="Собрать отчёт")
    p_rep.add_argument("--format", choices=["md", "json"], default="md", help="Формат вывода")
    p_rep.add_argument("--output", "-o", default=None, help="Путь к файлу вывода")
    p_rep.add_argument("--folder-name", default="", help="Название папки")
    _add_common_args(p_rep)
    p_rep.set_defaults(func=cmd_report)

    # run (ingest → summarize → report)
    p_run = subparsers.add_parser("run", help="Полный цикл: ingest → summarize → report")
    p_run.add_argument("--folder-id", default=None)
    p_run.add_argument("--credentials", default=None)
    p_run.add_argument("--force", action="store_true")
    p_run.add_argument("--format", choices=["md", "json"], default="md")
    p_run.add_argument("--output", "-o", default="summary.md")
    p_run.add_argument("--folder-name", default="")
    _add_common_args(p_run)
    p_run.set_defaults(func=cmd_run)

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)

    if args.cache_dir:
        import src.config as cfg
        cfg.CACHE_DIR = Path(args.cache_dir)
        cfg.CACHE_DOWNLOADS = cfg.CACHE_DIR / "downloads"
        cfg.CACHE_TEXTS = cfg.CACHE_DIR / "texts"
        cfg.CACHE_LLM = cfg.CACHE_DIR / "llm"

    if args.cmd and hasattr(args, "func"):
        args.func(args)
    else:
        ensure_cache_dirs()
        if not check_api_key():
            print("⚠️  Задайте OPENROUTER_API_KEY в .env")
        print(f"Drive Summary — folder_id: {GOOGLE_DRIVE_FOLDER_ID}")
        print("Команды: ingest, summarize, report, run")
        print("Пример: python main.py ingest && python main.py summarize && python main.py report -o summary.md")


if __name__ == "__main__":
    main()
