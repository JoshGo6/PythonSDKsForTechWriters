from pathlib import Path

my_list = [e.name for e in Path('.').iterdir()]
print(my_list)