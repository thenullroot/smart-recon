from colorama import Fore, init
import socket

init(autoreset=True)


def scan_ports(targets):
    results = []
    ports = [80, 443]

    for target in targets:
        host = target.replace("http://", "").replace("https://", "")

        for port in ports:
            try:
                sock = socket.socket()
                sock.settimeout(2)

                sock.connect((host, port))

                try:
                    sock.send(b"HEAD / HTTP/1.1\r\nHost: " + host.encode() + b"\r\n\r\n")
                    banner = sock.recv(100).decode(errors="ignore").strip()
                except:
                    banner = ""

                sock.close()

                output = Fore.GREEN + f"[PORT] {host}:{port} OPEN"

                if banner:
                    banner_clean = banner.replace("\n", " ").replace("\r", "")
                    output += Fore.YELLOW + f" ({banner_clean[:100]})"

                print(output)
                results.append(output)

            except:
                continue

    return results
