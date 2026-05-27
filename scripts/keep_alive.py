import os
import sys
import urllib.error
import urllib.request


def main() -> int:
    target_url = os.getenv("KEEP_ALIVE_URL")
    timeout_seconds = int(os.getenv("KEEP_ALIVE_TIMEOUT_SECONDS", "10"))

    if not target_url:
        print("KEEP_ALIVE_URL is required")
        return 1

    try:
        with urllib.request.urlopen(target_url, timeout=timeout_seconds) as response:
            print(f"Ping OK: {target_url} -> {response.status}")
            return 0 if 200 <= response.status < 500 else 1
    except urllib.error.HTTPError as error:
        print(f"Ping HTTP error: {target_url} -> {error.code}")
        return 0 if 200 <= error.code < 500 else 1
    except Exception as error:
        print(f"Ping failed: {target_url} -> {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
