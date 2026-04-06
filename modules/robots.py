import requests


def fetch_robots(domain, protocol):
    robots = []

    url = f"{protocol}://{domain}/robots.txt"

    try:
        response = requests.get(url, timeout=5)

        print(f"[DEBUG] Status Code: {response.status_code}")

        if response.status_code == 200:
            lines = response.text.splitlines()

            for line in lines:
                if line.lower().startswith("disallow:"):
                    path = line.split(":")[1].strip()

                    if path:
                        full_url = f"{protocol}://{domain}{path}"
                        print(f"[ROBOTS] {full_url} (200)")
                        robots.append((full_url, 200))

        else:
            print("[ERROR] robots.txt not found")

    except requests.Timeout:
        print("[ERROR] Timeout while fetching robots.txt")

    except requests.RequestException:
        print("[ERROR] Failed to fetch robots.txt")

    return robots
