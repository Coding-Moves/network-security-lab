"""Lesson 00.01.01 — What is computer networking?

Shows basic network information about YOUR OWN device.
It does not scan or contact other devices on your network.

Run:  python3 my_network_info.py
"""

import platform
import socket


def local_ip() -> str:
    """Find the address this device uses on the local network.

    Connecting a UDP socket does not send any packet. It only asks the
    operating system which network card and address it would use.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("1.1.1.1", 80))
        return s.getsockname()[0]
    except OSError:
        return "not connected"
    finally:
        s.close()


def main() -> None:
    system = platform.system()

    print("=== My network info ===")
    print(f"Device name : {socket.gethostname()}")
    print(f"System      : {system} {platform.release()}")
    print(f"Local IP    : {local_ip()}")

    print("\nTo see more, run these on your system:")
    if system == "Windows":
        print("  ipconfig          → address, subnet mask, default gateway")
        print("  ping 1.1.1.1      → test the path to a public server")
    elif system == "Darwin":
        print("  ifconfig          → network cards and addresses")
        print("  netstat -nr       → routing table ('default' = your router)")
        print("  ping -c 4 1.1.1.1 → test the path to a public server")
    else:
        print("  ip addr           → network cards and addresses")
        print("  ip route          → 'default via ...' = your router")
        print("  ping -c 4 1.1.1.1 → test the path to a public server")


if __name__ == "__main__":
    main()
