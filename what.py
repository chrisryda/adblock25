
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield bytes(lst[i:i + n])

with open(f"./local-podcasts/1.mp3", "rb") as local:
    data = local.read()
with open(f"./tor-podcasts/1.mp3", "rb") as tor:
    tor_data = tor.read()

delta = 2**13
l = list(chunks(list(tor_data), delta))

i = 0
d = b""
for chunk in l:
    d += chunk
    if i < 50:
        print(data.find(chunk))
    i += 1
    
with open(f"./XX.mp3", "wb") as out:
    out.write(d)