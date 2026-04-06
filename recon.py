import argparse
import requests
import sys
import signal
from urllib.parse import urlparse
from colorama import Fore, init

from modules.subdomain import enumerate_subdomains
from modules.portscan import scan_ports
import modules.dirscan as dirscan
import modules.subdomain as subdomain

init(autoreset=True)


# ✅ CTRL+C HANDLER (DO NOT TOUCH AGAIN)
def signal_handler(sig, frame):
    print(Fore.RED + "\n[!] Stopping scan immediately...")
    dirscan.STOP = True
    subdomain.STOP = True
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def fetch_robots(protocol, target, output_lines):
    robots_urls = []
    print(Fore.CYAN + "\n[+] Fetching robots.txt...")

    try:
        url = f"{protocol}://{target}/robots.txt"
        response = requests.get(url, timeout=5)

        print(Fore.YELLOW + f"[DEBUG] Status Code: {response.status_code}")

        if response.status_code == 200:
            for line in response.text.splitlines():
                if line.lower().startswith("disallow:"):
                    path = line.split(":")[1].strip()
                    full_url = f"{protocol}://{target}{path}"

                    print(Fore.CYAN + f"[ROBOTS] {full_url} (200)")
                    robots_urls.append((full_url, 200))

                    if output_lines is not None:
                        output_lines.append(f"[ROBOTS] {full_url} (200)")
        else:
            print(Fore.RED + "[ERROR] robots.txt not found")

    except:
        print(Fore.RED + "[ERROR] Failed to fetch robots.txt")

    return robots_urls


def main():
    print(Fore.YELLOW + "[DEBUG] Script started")

    parser = argparse.ArgumentParser(description="Smart Recon Tool")

    parser.add_argument("target", help="Target URL")
    parser.add_argument("--subs", default="data/wordlist.txt", help="Subdomain wordlist")
    parser.add_argument("--dirs", default="data/dir_wordlist.txt")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--filter", action="store_true")
    parser.add_argument("--output")

    args = parser.parse_args()

    parsed = urlparse(args.target)
    protocol = parsed.scheme if parsed.scheme else "http"
    target = parsed.netloc if parsed.netloc else parsed.path

    print(Fore.GREEN + f"[+] Target: {target}")
    print(Fore.GREEN + f"[+] Protocol: {protocol}")
    print(Fore.GREEN + f"[+] Subdomain Wordlist: {args.subs}")
    print(Fore.GREEN + f"[+] Directory Wordlist: {args.dirs}")
    print(Fore.GREEN + f"[+] Filter Mode: {'ON' if args.filter else 'OFF'}")

    output_lines = []

    # robots
    robots = fetch_robots(protocol, target, output_lines)

    # subdomains
    print(Fore.CYAN + "\n[+] Starting subdomain enumeration...")
    found_subdomains = enumerate_subdomains(target, protocol, args.subs)

    print(Fore.GREEN + "\n[+] Scan Complete")
    print(Fore.GREEN + f"[+] Real Subdomains Found: {len(found_subdomains)}")

    if not found_subdomains:
        print(Fore.RED + "[-] No subdomains found")
        print(Fore.YELLOW + "[*] Using main target...\n")
        targets = [f"{protocol}://{target}"]
    else:
        targets = found_subdomains

    print(Fore.GREEN + f"[+] Targets to Scan: {len(targets)}")

    # port scan
    print(Fore.CYAN + "[+] Starting port scan...")
    port_results = scan_ports(targets)

    for r in port_results:
        output_lines.append(r)

    # directory scan
    print(Fore.CYAN + "\n[+] Starting directory scan...")
    dir_count = dirscan.scan_directories(
        targets,
        protocol,
        args.dirs,
        limit=args.limit,
        filter_mode=args.filter,
        output_lines=output_lines,
        robots=robots
    )

    # summary
    print(Fore.CYAN + "\n[+] Scan Summary")
    print(Fore.GREEN + f"Real Subdomains Found: {len(found_subdomains)}")
    print(Fore.GREEN + f"Targets Scanned: {len(targets)}")
    print(Fore.GREEN + f"Open Ports Found: {len(port_results)}")
    print(Fore.GREEN + f"Directories Found: {dir_count}")

    # save
    if args.output:
        with open(args.output, "w") as f:
            f.write("\n".join(output_lines))

        print(Fore.GREEN + f"\n[+] Saved to {args.output}")


if __name__ == "__main__":
    main()
