from colorama import Fore, init
import requests

init(autoreset=True)

STOP = False


def enumerate_subdomains(target, protocol, wordlist_path):
    global STOP
    live_subdomains = []

    try:
        with open(wordlist_path, "r") as f:
            subdomains = [line.strip() for line in f if line.strip()]
    except:
        print(Fore.RED + "[ERROR] Subdomain wordlist not found")
        return []

    for sub in subdomains:
        if STOP:
            break

        url = f"{protocol}://{sub}.{target}"

        try:
            r = requests.get(url, timeout=2)

            if STOP:
                break

            if r.status_code < 400:
                print(Fore.GREEN + f"[LIVE] {url}")
                live_subdomains.append(url)

        except:
            continue

    return live_subdomains
