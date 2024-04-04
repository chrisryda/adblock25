
def same(x, y, delta): 
    with open(x, "rb") as one: 
        with open(y, "rb") as two:
            chunk = other = True 
            while chunk or other: 
                chunk = one.read(delta)
                other = two.read(delta)
                if chunk != other:
                    print("Diff")
                    flag = 1
                    while flag != 0:
                        chunk += one.read(delta)
                        other += two.read(delta)
                        idx = chunk.find(other[-1000:])
                        if idx == -1:
                            continue
                        else:
                            flag = 0
                            chunk = chunk[idx:]
                            # other = other[-1000:]
                out.write(chunk)       
            
# with open("out.mp3", "wb") as out:
#     same("/home/crd/Downloads/TheInfiniteMonkeyCage-20091130-ScienceAndComedians.mp3",
#     "/home/crd/Downloads/TheInfiniteMonkeyCage-20091130-ScienceAndComedians(1).mp3",
#     10_000
#     )
    
with open("out.mp3", "wb") as out:
    same("/home/crd/Downloads/GlobalNewsPodcast-20240401-GazaHospitalInRuinsAfterTwoWeekIsraeliRaid.mp3",
    "/home/crd/Downloads/GlobalNewsPodcast-20240401-GazaHospitalInRuinsAfterTwoWeekIsraeliRaid(1).mp3",
    10_000
    )
