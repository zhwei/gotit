import os
#from time import ctime

f = file("proxy1.txt")

for i in f.readlines():
    a = i.strip().split(":")
    com = "echo logout | telnet "+a[0]+" "+ a[1] +" | grep ] | wc -l"
    print com
    os.system(com)

