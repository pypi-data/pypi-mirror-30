"""
Update Procedure:
1. Check if the entry exist by basename
2. Check if updated is needed by WCS
3. Write to database
"""

import os
import peeweedb
from config import config
from pyzaphot import PhotFitsImage
from sqlconnector import connect
from writer import dict2sql

config = config()
storepath = config['store']
TABLE = config['mysql']['images_table']


def updater(data, table):
    db = connect()
    table = peeweedb.tables[table]

    try:
        wcsed = table.get(table.basename == data['basename']).WCSED
        if not wcsed == 'T':
            dict2sql(db, table, data)
            return None

    except table.DoesNotExist as e:
        print(e)
        dict2sql(db, table, data)
        return None


def zaphot_add_one_image_to_db(image, skip=False, delete=False, update=False, table=TABLE):
    # check image processed or not, if yes, return
    print("dealing with", image)
    print("processing image : " + image)
    imagetmp = PhotFitsImage(image)
    processed = os.path.isfile(storepath + imagetmp.savepath + imagetmp.uniformname) or os.path.isfile(
        storepath + imagetmp.savepath + imagetmp.uniformname + '.gz')
    if processed and not update:
        print("this image has already been processed")
        if delete:
            print("Deleting this image!!!")
            command = "rm -f {0}".format(image)
            print(command)
            # os.system(command)

    # only do WCS if it is not WCSED
    if not skip and imagetmp.WCSED != 'T':
        print('doing wcs here ...')
        # currently only works for KAIT images
        command = "Ssolve-field-kait ".format(image)
        print(command)
        # os.system(command)

    imagetmp.extract_zeromagphotinfo()
    dbinf = imagetmp.get_databaseinfo()

    updater(dbinf, table)

    if delete:
        command = "mv {0} {1}".format(
            image, storepath + imagetmp.savepath)
        print(command)
        # os.system(command)
    else:
        command = "cp {0} {1}".format(
            image, storepath + imagetmp.savepath)
        print(command)
        # os.system(command)
    command = "gzip {0}".format(
        storepath + imagetmp.savepath + imagetmp.uniformname)
    print(command)
    # os.system(command)


def main(args):
    zaphot_add_one_image_to_db(args.image, skip=args.skip, delete=args.delete, update=args.update)
