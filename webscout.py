import asyncio
import aiohttp
import sys
from bs4 import BeautifulSoup
import argparse
from tqdm import tqdm

async def check_host(target, timeout, valid_codes, show_title, show_status, semaphore, progress_bar):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    urls = [f"http://{target}", f"https://{target}"]
    async with aiohttp.ClientSession(headers=headers) as session:
        for url in urls:
            await semaphore.acquire()
            output = ""
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
            except aiohttp.ClientConnectorError:
                pass #progress_bar.write(f"Connection error for {url}")
            except aiohttp.ClientResponseError as e:
                pass #progress_bar.write(f"HTTP error for {url}: {e}")
            except asyncio.TimeoutError:
                pass #progress_bar.write(f"Request timed out for {url}")
            finally:
                progress_bar.update(1)
                semaphore.release()

async def main():
    parser = argparse.ArgumentParser(description='Check web servers for live status and optional titles.')
    parser.add_argument('-timeout', type=float, default=3, help='Set timeout for requests.')
    parser.add_argument('-status', action='store_true', help='Whether to show status codes.')
    parser.add_argument('-title', action='store_true', help='Whether to fetch and display page titles.')
    parser.add_argument('-file', type=str, help='Optional file path to read targets from. If omitted, reads from stdin.')
    parser.add_argument('-concurrency', type=int, default=85, help='Maximum number of concurrent requests.')
    parser.add_argument('-mc', '--match-code', type=int, nargs='+', default=[200, 301, 302, 303, 304, 307, 308, 400, 401, 403, 404, 500, 502, 503], help='Acceptable status codes.')

    args = parser.parse_args()
    semaphore = asyncio.Semaphore(args.concurrency)
    show_status = args.status

    targets = []

    if args.file:
        with open(args.file, 'r') as file:
            targets = [line.strip() for line in file if line.strip()]
    else:
        targets = [line.strip() for line in sys.stdin if line.strip()]

    progress_bar = tqdm(total=len(targets) * 2, unit='request', desc="Checking URLs")
    tasks = [check_host(target, args.timeout, args.match_code, args.title, show_status, semaphore, progress_bar) for target in targets]
    await asyncio.gather(*tasks)
    progress_bar.close()

if __name__ == "__main__":
    asyncio.run(main())
