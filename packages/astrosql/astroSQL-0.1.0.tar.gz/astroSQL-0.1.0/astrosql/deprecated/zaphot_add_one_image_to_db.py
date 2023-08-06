#!/usr/bin/env python3
import os
import argparse
from writer import dict2sql
from pyzaphot import PhotFitsImage
from sqlconnector import connect

storelocation = "/media/data12/imagedatabase/"

def update(data, table):
    con = connect()
    dict2sql(con, table, data)


def zaphot_add_one_image_to_db(args):
    print("dealing with", args.image)
    print("processing image : " + args.image)

    ##only do WCS if it is not WCSED
    if not args.skip and imagetmp.WCSED != 'T':
        print('doing wcs here ...')
        ##currently only works for KAIT images
        command = "Ssolve-field-kait ".format(args.image)
        print(command)
        #os.system(command)

    dbinf = imagetmp.extract_zeromagphotinfo()
    dbinf = imagetmp.get_databaseinfo()
    table = 'results'
    update(dbinf, table)

    # if args.delete:
    #     command = "mv {0} {1}".format(
    #         args.image, storelocation + imagetmp.savepath)
    #     print(command)
    #     #os.system(command)
    # else:
    #     command = "cp {0} {1}".format(
    #         args.image, storelocation + imagetmp.savepath)
    #     print(command)
    #     #os.system(command)
    # command = "gzip {0}".format(
    #     storelocation + imagetmp.savepath + imagetmp.uniformname)
    # print(command)
    #os.system(command)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('image')
    parser.add_argument('-s', '--skip', action='store_true',
                        help="skip WCS (default: False)")
    parser.add_argument('-u', '--update', action='store_true',
                        help="force update database")
    parser.add_argument('-d', '--delete', action='store_true',
                        help="delete original image")

    args = parser.parse_args()

    ##check image processed or not, if yes, return
    imagetmp = PhotFitsImage(args.image)
    processed = os.path.isfile(storelocation + imagetmp.savepath + imagetmp.uniformname) or os.path.isfile(
        storelocation + imagetmp.savepath + imagetmp.uniformname + '.gz')
    if (processed and not args.update):
        print("this image has already been processed")
        if args.delete:
            print("Deleting this image!!!")
            command = "rm -f {0}".format(args.image)
            print(command)
            #os.system(command)
    ##got to next step
    zaphot_add_one_image_to_db(args)
