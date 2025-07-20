import socket
import ssl
import socks
import dns.resolver
import dns.zone
import dns.query
import pyfiglet
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style, init
import os
import requests

init(autoreset=True)

def enable_tor_proxy():
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
    socket.socket = socks.socksocket

def check_tor_ip():
    try:
        proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        res = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=10)
        print(f"{Fore.GREEN}[+] TOR IP Detected: {res.json()['origin']}")
    except Exception as e:
        print(f"{Fore.RED}[-] Could not connect through TOR: {e}")


def scan_port(resolved_ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex((resolved_ip, port))

        if result == 0:
            banner = "No banner"
            try:
                if port == 80:
                    s.send("GET / HTTP/1.1\r\nHost: {}\r\n\r\n".format(resolved_ip).encode())
                    banner = s.recv(1024).decode(errors="ignore").strip()
                elif port == 443:
                    context = ssl.create_default_context()
                    ssl_sock = context.wrap_socket(s, server_hostname=resolved_ip)
                    ssl_sock.send(f"HEAD / HTTP/1.1\r\nHost: {resolved_ip}\r\n\r\n".encode())
                    banner = ssl_sock.recv(1024).decode(errors="ignore").strip()
                    ssl_sock.close()
                else:
                    s.send(b"\r\n")
                    banner = s.recv(1024).decode(errors="ignore").strip()
            except:
                banner = "Banner not found"

            print(f"{Fore.GREEN}[+] Port {port} is OPEN. Version: {banner}")
        s.close()
    except Exception:
        pass

def port_scan():
    while True:
        ip = input("Enter the IP or domain: ").strip()
        try:
            resolved_ip = socket.gethostbyname(ip)
            break
        except socket.gaierror:
            print("IP or domain not found. Try again.")

    while True:
        try:
            ports = input("Enter the number of ports you want to scan (default 1000): ").strip()
            count_port = int(ports) if ports else 1000
            if 1 <= count_port <= 65535:
                break
            else:
                print("Enter a number between 1 and 65535.")
        except ValueError:
            print("Invalid input.")

    print(f"\n{Fore.RED}[+] Starting scan on {resolved_ip} (ports 1 to {count_port})...\n")

    with ThreadPoolExecutor(max_workers=100) as executor:
        for port in range(1, count_port + 1):
            executor.submit(scan_port, resolved_ip, port)


def dns_enum(domain):
    print(f"{Fore.CYAN}[+] Starting DNS Enumeration for: {domain}")
    print("=" * 60)

    record_types = ["A", "AAAA", "NS", "MX", "TXT", "SOA", "CNAME"]
    for rtype in record_types:
        try:
            answers = dns.resolver.resolve(domain, rtype, lifetime=3)
            print(f"\n{Fore.GREEN}[{rtype}] Records:")
            for rdata in answers:
                print(f"  - {str(rdata)}")
        except Exception as e:
            print(f"{Fore.YELLOW}[{rtype}] No data or failed: {e}")

    print(f"\n{Fore.CYAN}[+] Subdomain brute-force:")
    subdomains = ["www", "mail", "ftp", "dev", "staging", "admin", "vpn", "ns1", "ns2", "blog"]
    for sub in subdomains:
        full_domain = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(full_domain)
            print(f"{Fore.GREEN}  [+] Found: {full_domain} → {ip}")
        except:
            pass

    try:
        print(f"\n{Fore.CYAN}[+] Zone Transfer Test:")
        ns_records = dns.resolver.resolve(domain, "NS")
        for ns in ns_records:
            ns = str(ns).rstrip('.')
            try:
                ns_ip = socket.gethostbyname(ns)
                zone = dns.zone.from_xfr(dns.query.xfr(ns_ip, domain, timeout=5))
                names = zone.nodes.keys()
                print(f"{Fore.RED}  [!!] Zone transfer successful on {ns} ({ns_ip}):")
                for name in names:
                    print(f"     - {zone[name].to_text(name)}")
            except Exception as e:
                print(f"{Fore.YELLOW}  [-] Zone transfer failed on {ns}: {e}")
    except Exception as e:
        print(f"{Fore.YELLOW}  [-] Failed to get NS records: {e}")


def dns_port_scan():
    while True:
        ip = input("Enter the IP or domain: ").strip()
        try:
            resolved_ip = socket.gethostbyname(ip)
            break
        except socket.gaierror:
            print("IP or domain not found. Try again.")

    dns_enum(ip)
    while True:
        try:
            ports = input("Enter the number of ports you want to scan (default 1000): ").strip()
            count_port = int(ports) if ports else 1000
            if 1 <= count_port <= 65535:
                break
            else:
                print("Enter a number between 1 and 65535.")
        except ValueError:
            print("Invalid input.")

    print(f"\n{Fore.RED}[+] Starting scan on {resolved_ip} (ports 1 to {count_port})...\n")

    with ThreadPoolExecutor(max_workers=100) as executor:
        for port in range(1, count_port + 1):
            executor.submit(scan_port, resolved_ip, port)


def port_scan_tor():
    enable_tor_proxy()
    check_tor_ip()
    port_scan()

def dns_enum_port_scan_tor():
    enable_tor_proxy()
    check_tor_ip()
    ip = input("Enter the domain name: ").strip()
    dns_enum(ip)
    port_scan()


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = pyfiglet.figlet_format("RED-WIZARD", font="epic")
    print(Fore.RED + banner)
    print(Fore.RED + "Author: Mrhoodie")
    print(Fore.RED + "Version: 1.0")
    print(Fore.RED + "-" * 60)
    print(Fore.RED + "[1] Port Scan")
    print(Fore.RED + "[2] DNS Enumeration")
    print(Fore.RED + "[3] DNS Enumeration + Port Scan")
    print(Fore.RED + "[4] Port Scan via TOR network")
    print(Fore.RED + "[5] DNS Enumeration + Port Scan via TOR network")
    print(Fore.RED + "[6] Exit")

    while True:
        choice = input("Your choice: ").strip()
        if choice == "1":
            port_scan()
        elif choice == "2":
            domain = input("Enter a domain name: ").strip()
            dns_enum(domain)
        elif choice == "3":
            dns_port_scan()
        elif choice == "4":
            port_scan_tor()
        elif choice == "5":
            dns_enum_port_scan_tor()
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
