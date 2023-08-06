import pandas as pd
import re
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).absolute().parents[1]/'src'))
import peeweedb
from sqlconnector import connect
from astrosql import AstroSQL

connection = connect()
imagedb = AstroSQL(connection)

images = imagedb.get_table('images')

print("This may take a while ... ")
# get rows where objname update is needed
basenames = list(images.select(images.basename).where(images.objname.is_null(False).dicts())
df = pd.DataFrame(basenames)
df['objname'] = [re.findall('^[^_]+', d['basename'])[0] for d in basenames]

print("This may take a while")
with connection.atomic():
    for i,basename in enumerate(df['basename']):      
        if i % 10000 == 0:
            print(i)

        query = (images
                 .update(objname = df[df['basename'] == basename]['objname'].iloc[0])
                 .where(images.basename == basename)
                 )
        query.execute()
