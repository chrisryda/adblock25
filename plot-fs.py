import csv
import matplotlib.pyplot as plt

def get_xy(i):
    d = {}
    x = []
    y = []
    with open(f"./fs-2**1{i}.times.csv", newline="") as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            d[row[0]] = [row[1]]
        
        sorted_d = sorted(d.items())
        for l in sorted_d:
            x.append(int(l[0]))
            y.append(float(l[1][0]))
    return x,y


x,y3 = get_xy(3)
_,y4 = get_xy(4)

fig, ax = plt.subplots()
ax.plot(x,y3)
ax.plot(x,y4)

plt.legend(["$2^{13}$", "$2^{14}$"], loc="upper left")
plt.xlabel("Size of episode $(1^{7}$ bytes)")
plt.ylabel("Time (s)")
plt.show()
