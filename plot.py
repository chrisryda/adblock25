import csv
import matplotlib.pyplot as plt

def get_xy(i):
    d = {}
    x = []
    y = []
    with open(f"./2**1{i}-times.csv", newline="") as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            d[row[0]] = [row[1]]
        
        sorted_d = sorted(d.items())
        for l in sorted_d:
            x.append(int(l[0]))
            y.append(float(l[1][0]))
    return x,y

x,y0 = get_xy(0)
_,y1 = get_xy(1)
x2,y2 = get_xy(2)
x2,y3 = get_xy(3)
x2,y4 = get_xy(4)
x2,y5 = get_xy(5)
x2,y6 = get_xy(6)

fig, ax = plt.subplots()
ax.plot(x,y0)
ax.plot(x,y1)
ax.plot(x2,y2)
ax.plot(x2,y3)
ax.plot(x2,y4)
ax.plot(x2,y5)
ax.plot(x2,y6)


plt.legend(["$2^{10}$", "$2^{11}$", "$2^{12}$", "$2^{13}$", "$2^{14}$", "$2^{15}$", "$2^{16}$"], loc="upper left")
plt.show()