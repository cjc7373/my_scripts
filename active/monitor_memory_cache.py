"""
使用了 pcstat (https://github.com/tobert/pcstat)
首先用 
find . -type f | xargs -I {} ~/Downloads/pcstat -sort -nohdr -terse "{}" > ~/test/cached.csv
来生成当前文件夹下的所有文件的 cached page 情况, 然后用本脚本分析
"""
import csv

size = 0
pages = 0
cached = 0

with open("cached.csv") as c:
    reader = csv.reader(c)
    for row in reader:
        # size, pages, cached
        # print(row[1], row[-3], row[-2])
        size += int(row[1])
        pages += int(row[-3])
        cached += int(row[-2])

print(f"Total size {size/1024/1024} MB")
print(f"Cached size {cached/pages*size/1024/1024} MB")
print(f"Page size {size/pages} B")
print(f"Cache rate {cached/pages*100:.2f}%")
