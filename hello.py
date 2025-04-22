from collections import Counter

s = "Python is Fun!"
v = "aeiouAEIOU"
cnt = Counter([i for i in s if i in v])
print(cnt)

