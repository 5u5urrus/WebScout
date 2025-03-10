#!/usr/bin/env python3
# WebScout: This is a very nice tool, give it a try! 
# Author: Vahe Demirkhanyan
import asyncio
import aiohttp
import sys
from bs4 import BeautifulSoup
import argparse
from tqdm import tqdm
import ipaddress
from urllib.parse import urlparse

async def check_url(url, timeout, valid_codes, show_title, show_status, semaphore, progress_bar):
    """
    Checks a single URL for a valid response code and optionally prints title/status.
    """
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        )
    }
    async with semaphore, aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.get(url, timeout=timeout, ssl=False) as response:
                if response.status in valid_codes:
                    output = f"{url}"
                    if show_status:
                        output += f" Status: {response.status}"
                    if show_title:
                        try:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            title = soup.find('title').string if soup.title else 'No Title Found'
                            output += f" Title: {title}"
                        except Exception as e:
                            progress_bar.write(f"Failed to parse HTML for {url}: {e}")
                    progress_bar.write(output)
        except (aiohttp.ClientConnectorError, aiohttp.ClientResponseError, asyncio.TimeoutError):
            pass
        finally:
            progress_bar.update(1)

def expand_octet(octet_str):
    """
    Given a string for a single octet (e.g. '1', '10-12'),
    return a list of the expanded values as strings.
    """
    if '-' in octet_str:
        start, end = octet_str.split('-')
        start, end = int(start), int(end)
        if start > end:
            start, end = end, start  # swap if reversed
        return [str(i) for i in range(start, end + 1)]
    else:
        return [octet_str]

def parse_multi_octet(ip_str):
    """
    Handle multi-octet ranges for IPv4, e.g. '1.1.1-2.1-5'.
    Returns a list of expanded IP strings, or None if not applicable.
    """
    parts = ip_str.split('.')
    # If it's not exactly 4 parts, we can't do multi-octet expansion
    if len(parts) != 4:
        return None

    import itertools
    all_expanded = []
    try:
        expanded_octets = [expand_octet(part) for part in parts]
        for combo in itertools.product(*expanded_octets):
            int_parts = list(map(int, combo))
            # Validate each part is 0..255
            if any(p < 0 or p > 255 for p in int_parts):
                continue
            ip_candidate = ".".join(str(p) for p in int_parts)
            all_expanded.append(ip_candidate)

        return all_expanded if all_expanded else None
    except:
        return None

def parse_target_line(line):
    """
    Expands a single line into one or more targets:
      - If it has a scheme (http:// or https://), parse out and keep just the host:port portion
      - CIDR notation (e.g. 1.1.1.0/24)
      - Multi-octet ranges (e.g. 1.1.1-2.1-5)
      - Otherwise, treat it as a single domain/IP.
    """
    line = line.strip()
    if not line:
        return []

    # 1) If there's an explicit scheme like http:// or https://, parse out the netloc
    parsed = urlparse(line)
    if parsed.scheme and parsed.netloc:
        line = parsed.netloc  # e.g. line="headerguard.com" or "headerguard.com:8443"

    # 2) Check if it's CIDR notation
    if "/" in line:
        try:
            network = ipaddress.ip_network(line, strict=False)
            return [str(ip) for ip in network.hosts()]
        except ValueError:
            # If invalid CIDR, treat it as single target
            return [line]

    # 3) Try multi-octet expansion
    multi = parse_multi_octet(line)
    if multi:
        return multi

    # 4) Otherwise, return as-is
    return [line]

def build_urls_for_target(target, ports, scheme):
    """
    Given a 'target' (IP or domain) and a list of ports,
    return the list of URLs that should be checked.
    
    - If port == 80  and scheme is http/both => http://target
    - If port == 80  and scheme is https only => skip
    - If port == 443 and scheme is https/both => https://target
    - If port == 443 and scheme is http only => skip
    - Any other port => apply either or both schemes depending on user input.
    
    (No ':80' or ':443' in these default cases; we show custom ports with :port.)
    """
    urls = []
    for port in ports:
        # --- Handle port 80 ---
        if port == 80:
            if scheme in ("both", "http"):
                urls.append(f"http://{target}")
            # If scheme == "https" only, skip
        # --- Handle port 443 ---
        elif port == 443:
            if scheme in ("both", "https"):
                urls.append(f"https://{target}")
            # If scheme == "http" only, skip
        # --- Handle everything else ---
        else:
            if scheme in ("both", "http"):
                urls.append(f"http://{target}:{port}")
            if scheme in ("both", "https"):
                urls.append(f"https://{target}:{port}")
    return urls

async def main():
    parser = argparse.ArgumentParser(
        description='Check web servers for live status and optional titles.'
    )
    parser.add_argument('-timeout', type=float, default=3, help='Set timeout for requests.')
    parser.add_argument('-status', action='store_true', help='Whether to show status codes.')
    parser.add_argument('-title', action='store_true', help='Whether to fetch and display page titles.')
    parser.add_argument('-file', type=str, help='Optional file path to read targets from. If omitted, reads from stdin.')
    parser.add_argument('-concurrency', type=int, default=85, help='Maximum number of concurrent requests.')
    parser.add_argument(
        '-mc', '--match-code',
        type=int, nargs='+',
        default=[200, 301, 302, 303, 304, 307, 308, 400, 401, 403, 404, 500, 502, 503],
        help='Acceptable status codes.'
    )
    # Ports
    parser.add_argument(
        '-p', '--ports',
        type=str,
        default='',
        help="Comma-separated list of ports to check. Defaults to '80,443' if not provided."
    )
    # Schemes
    parser.add_argument(
        '-s', '--scheme',
        choices=['both', 'http', 'https'],
        default='both',
        help="Which scheme(s) to check. Default is 'both'."
    )
    parser.add_argument(
        'targets',
        nargs='*',
        help='Optional direct targets (IPs, IP ranges, CIDRs, or domains).'
    )

    args = parser.parse_args()
    semaphore = asyncio.Semaphore(args.concurrency)
    show_status = args.status

    # Parse ports (default to [80, 443] if not given)
    if args.ports.strip():
        port_list = []
        for p in args.ports.split(','):
            try:
                port_list.append(int(p.strip()))
            except ValueError:
                pass
        if not port_list:
            port_list = [80, 443]
    else:
        port_list = [80, 443]

    # Collect lines from file/stdin
    lines = []
    if args.file:
        with open(args.file, 'r') as file:
            lines.extend([ln.strip() for ln in file if ln.strip()])
    else:
        # If not reading from a file, check if anything is piped from stdin
        if not sys.stdin.isatty():
            lines.extend([ln.strip() for ln in sys.stdin if ln.strip()])

    # Also include any direct targets from the CLI
    lines.extend(args.targets)

    # Now expand them into actual IPs/hosts
    final_targets = []
    for line in lines:
        final_targets.extend(parse_target_line(line))

    # Build a list of all URLs we'll check
    all_urls = []
    for target in final_targets:
        all_urls.extend(build_urls_for_target(target, port_list, args.scheme))

    # Create the progress bar with the correct total
    progress_bar = tqdm(
        total=len(all_urls),
        unit='request',
        desc="Checking URLs"
    )

    # Create tasks for every URL
    tasks = []
    for url in all_urls:
        tasks.append(
            check_url(
                url,
                args.timeout,
                args.match_code,
                args.title,
                show_status,
                semaphore,
                progress_bar
            )
        )

    await asyncio.gather(*tasks)
    progress_bar.close()

if __name__ == "__main__":
    asyncio.run(main())
