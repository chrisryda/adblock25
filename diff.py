
def same(x, y, delta): 
    with open(x, "rb") as one: 
        with open(y, "rb") as two:
            d = 0 
            chunk = other = True 
            while chunk or other: 
                chunk = one.read(delta)
                other = two.read(delta)
                if chunk != other:
                    d += 1
                    print("Diff", d)
                    chunk = process(chunk, other, int(delta/10))
                out.write(chunk)


def process(chunk, other, delta):
    pass
    
    
with open("out.mp3", "wb") as out:
    same("/home/crd/Downloads/TheInfiniteMonkeyCage-20091130-ScienceAndComedians.mp3",
         "/home/crd/Downloads/TheInfiniteMonkeyCage-20091130-ScienceAndComedians(1).mp3",
         10_000
    )


# Når vanlig podcast starter igjen (ad er ferdig), må man bare finne den sequencen i andre fil 