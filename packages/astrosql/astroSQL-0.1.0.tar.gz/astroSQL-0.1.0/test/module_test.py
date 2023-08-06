import sys
import os
os.chdir("..")
sys.path.append('src')

from peeweedb import *

table = Images
query = table.select().where(table.centerRa.between(0.3,0.4))

cursor = db.execute(query)
d = cursor.fetchone()
print(d)