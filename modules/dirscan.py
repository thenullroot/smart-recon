from colorama import Fore, init
import requests

init(autoreset=True)

STOP = False


def scan_directories(targets, protocol, wordlist, limit=None, filter_mode=False, output_lines=None, robots=None):
    global STOP
    found_count = 0

    try:
        with open(wordlist, "r") as f:
            paths = [line.strip() for line in f if line.strip()]

        if limit:
            paths = paths[:limit]

        print(Fore.YELLOW + f"[*] Loaded {len(paths)} paths")

    except:
        print(Fore.RED + "[ERROR] Wordlist not found")
        return 0

    for target in targets:
        if STOP:
            return found_count

        print(Fore.YELLOW + f"[*] Scanning: {target}")

        if robots:
            print(Fore.CYAN + "[*] Checking robots.txt paths first...")
            for url, status in robots:
                if STOP:
                    return found_count

                print(Fore.CYAN + f"[ROBOTS] {url} ({status})")

                if status in [200, 301, 302, 403]:
                    found_count += 1

        for path in paths:
            if STOP:
                return found_count

            url = f"{target}/{path}"

            try:
                r = requests.get(url, timeout=2)
                status = r.status_code

                if filter_mode and status not in [200, 301, 302, 403]:
                    continue

                if status == 200:
                    color = Fore.GREEN
                elif status in [301, 302]:
                    color = Fore.YELLOW
                elif status == 403:
                    color = Fore.MAGENTA
                else:
                    color = Fore.RED

                print(color + f"[DIR] {url} ({status})")

                if output_lines is not None:
                    output_lines.append(f"[DIR] {url} ({status})")

                if status in [200, 301, 302, 403]:
                    found_count += 1

            except:
                continue

    return found_count
