#Author: Vahe Demirkhanyan
import asyncio
import aiohttp
import sys
from bs4 import BeautifulSoup
import argparse

async def check_host(ip, timeout, valid_codes, show_title, show_status, semaphore):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    urls = [f"http://{ip}", f"https://{ip}"]
    async with aiohttp.ClientSession(headers=headers) as session:
        for url in urls:
            await semaphore.acquire()
            #update_display(url)
            output=""
            try:
                async with session.get(url, timeout=timeout, ssl=False) as response:
                    if response.status in valid_codes:
                        output=f"\n{url}"
                        if show_status:
                            output += f" Status: {response.status}"
                        #print(f"{url} - Status: {response.status}")
                        if show_title:
                            try:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                title = soup.find('title').string if soup.title else 'No Title Found'
                                #print(f"Title: {title}")
                                output += f" Title: {title}"
                            except Exception as e:
                                print(f"Failed to parse HTML for {url}: {e}")
                        #print(output)
                        sys.stdout.write(output)
                        sys.stdout.flush()
            except Exception as e:
                continue
            finally:
                semaphore.release()
                #update_display('')

def update_display(message):
    sys.stdout.write(f'\r{message.ljust(50)}')
    sys.stdout.flush()  # Important to ensure the output is updated

async def main():

    parser = argparse.ArgumentParser(description='Check web servers for live status and optional titles.')
    parser.add_argument('-timeout', type=float, default=3, help='Set timeout for requests.')
    parser.add_argument('-status', action='store_true', help='Whether to show status codes.')
    parser.add_argument('-title', action='store_true', help='Whether to fetch and display page titles.')
    parser.add_argument('-file', type=str, help='Optional file path to read IPs from. If omitted, reads from stdin.')
    parser.add_argument('-concurrency', type=int, default=50, help='Maximum number of concurrent requests.')
    parser.add_argument('-mc', '--match-code', type=lambda s: set(map(int, s.split(','))), default={200, 301, 302, 303, 304, 307, 308, 400, 401, 403, 404, 500, 502, 503}, help='Set of acceptable status codes.')

    args = parser.parse_args()
    semaphore = asyncio.Semaphore(args.concurrency)
    # Define default status codes if none are provided
    default_status_codes = {200, 301, 302, 303, 304, 307, 308, 400, 401, 403, 404, 500, 502, 503}
    show_status = True if args.status else False
    print("Test:",args.match_code)

    ips = []

    if args.file:
        with open(args.file, 'r') as file:
            ips = [line.strip() for line in file if line.strip()]
    else:
        ips = [line.strip() for line in sys.stdin if line.strip()]

    tasks = [check_host(ip, args.timeout, args.match_code, args.title, show_status, semaphore) for ip in ips]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
