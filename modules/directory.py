import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich import print
from modules.output import save


def scan_directories(targets, wordlist_path, limit, filter_mode, robots_paths=None):
    print("\n[+] Starting directory scan...")

    try:
        with open(wordlist_path, "r") as f:
            paths = [line.strip() for line in f if line.strip() and not line.startswith("#")]

        if limit > 0:
            paths = paths[:limit]

        print(f"[*] Loaded {len(paths)} paths")

    except FileNotFoundError:
        print("[ERROR] Wordlist not found")
        return

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for target in targets:
        print(f"[*] Scanning: {target}")

        # 🔥 Robots paths first
        if robots_paths:
            print("[cyan][*] Checking robots.txt paths first...[/cyan]")
            for rpath in robots_paths:
                url = f"{target}{rpath}"
                try:
                    res = requests.get(url, headers=headers, timeout=3, allow_redirects=False)
                    result = f"[ROBOTS] {url} ({res.status_code})"
                    print(result)
                    save(result)
                except:
                    pass

        checked = 0

        def check_path(path):
            url = f"{target}/{path}"
            try:
                res = requests.get(url, headers=headers, timeout=3, allow_redirects=False)

                if filter_mode:
                    if res.status_code in [200, 301, 302, 403]:
                        return f"[DIR] {url} ({res.status_code})"
                else:
                    return f"[DIR] {url} ({res.status_code})"

            except:
                return None

        try:
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(check_path, p) for p in paths]

                for future in as_completed(futures):
                    result = future.result()
                    checked += 1

                    if result:
                        print(result)
                        save(result)

                    if checked % 100 == 0:
                        print(f"[PROGRESS] {checked}/{len(paths)} checked")

        except KeyboardInterrupt:
            print("\n[red][!] Directory scan stopped by user[/red]")
            return
