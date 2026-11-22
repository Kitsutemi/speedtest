#!/usr/bin/env python3
"""
Последовательно скачивает URL несколько раз, замеряет время и объём,
печатает средние показатели и скорость.
Зависимостей нет — только стандартная библиотека.
"""

import argparse
import sys
import time
import urllib.request
import urllib.error

CHUNK_SIZE = 64 * 1024  # 64 KiB


def fetch(url: str, timeout: float = 60.0) -> tuple[int, float]:
    """Скачивает url целиком. Возвращает (bytes, seconds)."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "speedtest-script/1.0"},
    )
    start = time.perf_counter()
    total = 0
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        while True:
            chunk = resp.read(CHUNK_SIZE)
            if not chunk:
                break
            total += len(chunk)
    elapsed = time.perf_counter() - start
    return total, elapsed


def human_bytes(n: float) -> str:
    for unit in ("B", "KiB", "MiB", "GiB"):
        if n < 1024.0:
            return f"{n:.2f} {unit}"
        n /= 1024.0
    return f"{n:.2f} TiB"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Скачивает URL N раз подряд и замеряет скорость."
    )
    parser.add_argument("url", help="Адрес ресурса (например, большая картинка)")
    parser.add_argument(
        "-n", "--count", type=int, default=10,
        help="Количество запросов (по умолчанию 10)",
    )
    parser.add_argument(
        "-t", "--timeout", type=float, default=60.0,
        help="Таймаут одного запроса, сек (по умолчанию 60)",
    )
    args = parser.parse_args()

    sizes: list[int] = []
    times: list[float] = []

    for i in range(1, args.count + 1):
        try:
            size, elapsed = fetch(args.url, timeout=args.timeout)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            print(f"[{i}/{args.count}] ошибка: {e}", file=sys.stderr)
            continue

        sizes.append(size)
        times.append(elapsed)
        mb_s = size / elapsed / (1024 * 1024)
        print(
            f"[{i}/{args.count}] {human_bytes(size):>10}  "
            f"{elapsed:.3f} s  {mb_s:.2f} MB/s"
        )

    if not times:
        print("Ни один запрос не завершился успешно.", file=sys.stderr)
        return 1

    total_bytes = sum(sizes)
    total_time = sum(times)
    avg_time = total_time / len(times)
    avg_size = total_bytes / len(times)
    overall_mb_s = total_bytes / total_time / (1024 * 1024)
    overall_mbps = total_bytes * 8 / total_time / 1_000_000

    print()
    print(f"Успешных запросов:   {len(times)}/{args.count}")
    print(f"Всего скачано:       {human_bytes(total_bytes)}")
    print(f"Общее время:         {total_time:.3f} s")
    print(f"Среднее время:       {avg_time:.3f} s")
    print(f"Средний размер:      {human_bytes(avg_size)}")
    print(f"Скорость:            {overall_mb_s:.2f} MB/s ({overall_mbps:.2f} Mbps)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())