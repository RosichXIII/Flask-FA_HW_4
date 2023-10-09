from urllib.parse import urlparse, unquote
from pathlib import Path
import time
import mimetypes
import argparse
import requests
import asyncio
import threading
import multiprocessing

urls_list = []
with open("img_urls.txt", "r") as img_urls:
    for img_url in img_urls.readlines():
        urls_list.append(img_url.strip())

img_path = Path("./img_urls/")
img_path.mkdir(parents=True, exist_ok=True)

def get_file_name(url):
    file_path = Path(unquote(urlparse(url).path)).stem
    extension = mimetypes.guess_extension(requests.get(url).headers['content-type'])
    suggested_extention = ".jpg"
    
    if extension == None:
        return img_path.joinpath(file_path + suggested_extention)
    else:
        return img_path.joinpath(file_path + extension)
    
def save_file(file_name, response):
    with open(file_name, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
    

def show_end_time(start_time, *args):
    end_time = time.time() - start_time
    
    if args:
        print(f"\tЗагрузка {args} завершена, длительность: {end_time: .2f} секунд.")
    else:
        print(f"Загрузка завершена, длительность: {end_time: .2f} секунд.")

def img_download(url):
    start_time = time.time()
    file_name = get_file_name(url)
    response = requests.get(url, stream=True)
    save_file(file_name, response)
    show_end_time(start_time, file_name)
            
async def async_img_download(url):
    start_time = time.time()
    file_name = get_file_name(url)
    response = await asyncio.get_event_loop().run_in_executor(None, requests.get, url, {"stream": True})
    save_file(file_name, response)
    show_end_time(start_time, file_name)
            
def download_img_thread(url):
    start_time = time.time()
    threads = []
    
    for url in urls:
        thread = threading.Thread(target=img_download, args=(url,))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    show_end_time(start_time)
    
def download_img_multip(url):
    start_time = time.time()
    processes = []
    
    for url in urls:
        process = multiprocessing.Process(target=img_download, args=(url,))
        process.start()
        processes.append(process)
    
    for process in processes:
        process.join()
    
    show_end_time(start_time)
    
async def download_img_async(url):
    start_time = time.time()
    tasks = []
    
    for url in urls:
        task = asyncio.ensure_future(async_img_download(url))
        tasks.append(task)
    
    await asyncio.gather(*tasks)
    show_end_time(start_time)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--urls", default=urls_list, nargs="+", )
    args = parser.parse_args()
    
    urls = args.urls
    if not urls:
        urls = urls_list
    
    print(f"\nЗагрузка {len(urls)} изображений - threading")
    download_img_thread(urls)
    
    print(f"\nЗагрузка {len(urls)} изображений - multiprocessing")
    download_img_multip(urls)
    
    print(f"\nЗагрузка {len(urls)} изображений - asyncio")
    asyncio.run(download_img_async(urls))