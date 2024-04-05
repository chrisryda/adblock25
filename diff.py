
def same(x, y, delta): 
    with open(y, "rb") as two: 
        other = two.read()
    with open(x, "rb") as one: 
            chunk = one.read(delta)
            while chunk:
                if other.find(chunk) != -1:
                    out.write(chunk)
                chunk = one.read(delta)       
            
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
