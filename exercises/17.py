import math
from random import choice

packages = [
    {"name": "pygithub", "downloads": 54000, "description": "GitHub API wrapper"},
    {"name": "requests", "downloads": 890000, "description": ""},
    {"name": "flask", "downloads": 312000, "description": "Micro web framework"},
    {"name": "obscure-tool", "downloads": 15, "description": "An obscure utility"},
    {"name": "numpy", "downloads": 1450000, "description": "Numerical computing"},]

def popularity(download_count, threshhold=1000):
    popularity_level = ("popular" if download_count >= threshhold else "niche")
    return (download_count, popularity_level,)

# print(popularity(packages[3]["downloads"], 15))

for package in packages:
    name = package["name"]
    count = package["downloads"]
    decimal_popularity = math.log10(count)
    popularity_level = popularity(count)
    print(f"{name:<12} | {count:>7,} | log10: {decimal_popularity:>3.2f} | {popularity_level[1]:<}")
    if not package["description"]:
        print("   (no description provided)")

print()
random_package = choice(packages)
print(f"Random spotlight: {random_package["name"]} - {random_package["description"]}")
