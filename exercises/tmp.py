from itertools import islice
import re

# Get the 3rd match (index 2)
m = re.finditer(r"\d+", "a1 b22 c333")
info = next(islice(m, 2, None))

print(info.group())
print(info.start())
print(info.end())
print(info.span())
