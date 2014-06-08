from addons.redis2s import rds

for i in rds.keys("cache_*"):
    rds.delete(i)
    print i
