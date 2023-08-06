y = []
with open('scraping.txt','r') as f:
    for x in f:
        y.append(x.replace("\n", ""))
print(y)



