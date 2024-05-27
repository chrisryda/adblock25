import os
import time 

tor_dir = 'tor-podcasts'
local_dir = "local-podcasts"

local_files = []
for filename in os.scandir(local_dir):
    if filename.is_file():
        local_files.append(filename.name)

tor_files = []
for filename in os.scandir(tor_dir):
    if filename.is_file():
        tor_files.append(filename.name)
tor_files.sort()
local_files.sort()

delta = 2**16

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield bytes(lst[i:i + n])
        
def strip_ads(data: bytes, l: list, url) -> bytes:
    d = b""
    prev_idx = 0
    for chunk in l:
        idx = data.find(chunk)
        if idx != -1 and abs(idx-prev_idx) <= 100*delta:
            d += chunk
            data = data.replace(chunk, b"", 1)
        prev_idx = idx
        
    print()
    return d

def test_time():
    for lf, tf in zip(local_files, tor_files): 
        with open(f"./local-podcasts/{lf}", "rb") as local:
            data = local.read()
        with open(f"./tor-podcasts/{tf}", "rb") as tor:
            tor_data = tor.read()
        
        l = chunks(list(tor_data), delta)
        start = time.perf_counter()
        d = strip_ads(data, l, tf)
        end = time.perf_counter()
        t = (end-start)
        with open("./2**16-times.csv", "a") as out:
            out.write(f"{len(tor_data)},{(end-start)}\n")
        print(t)
    
test_time()
    