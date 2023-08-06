# -*- coding:utf-8 -*-
from __future__ import unicode_literals
# from builtins import str

import warnings
import requests
from astropy.table import Table
from astropy.io import ascii
from astrosql.sqlconnector import connect
from io import StringIO


def query(ra, dec, radius, outfile=None, limit=None, user=None, password=None, database="photometry_cal"):
    """Retrieve APASS data

    Parameters
    ----------
    ra :
        Right Ascension in decimal degrees
    dec :
        Declination in decimal degrees
    radius :
        Radius in in decimal degrees
    outfile :
        File to save text data to (Default: None)
    user :
        MySQL username (Default: None)
    password :
        MySQL password (Default: None)
    database :
        MySQL database where APASS is stored (Default: "photometry_cal")
    """
    con = connect(database, user, password)
    ra_min = ra - radius
    dec_min = dec - radius
    ra_max = ra + radius
    dec_max = dec + radius
    if limit:
        query_str = "SELECT `RA`, `DEC`, `V`, `Verr`, `B`, `Berr`, `g`, `gerr`, `r`, `rerr`, `i`, `ierr` FROM APASS WHERE `RA` BETWEEN {0} AND {1} AND `DEC` BETWEEN {2} AND {3} LIMIT {4}".format(
            ra_min, ra_max, dec_min, dec_max, limit)
        print(query_str)
        resultproxy = con.execute(query_str)
    else:
        query_str = "SELECT `RA`, `DEC`, `V`, `Verr`, `B`, `Berr`, `g`, `gerr`, `r`, `rerr`, `i`, `ierr` FROM APASS WHERE `RA` BETWEEN {0} AND {1} AND `DEC` BETWEEN {2} AND {3}".format(
            ra_min, ra_max, dec_min, dec_max)
        print(query_str)
        resultproxy = con.execute(query_str)
    colnames = resultproxy.keys()
    data = resultproxy.fetchall()
    if len(data) > 0:
        table = Table(names=colnames)
        for i in range(len(data)):
            table.add_row(list(data[i]))
        if outfile:
            formats = {colname: '%8.3f' for colname in table.columns}
            ascii.write(table, output=outfile, delimiter='\t',
                        overwrite=True, formats=formats)
            print('Write to {}: Success'.format(outfile))
        return table
    else:
        print("No data found")
        return None


class Client(object):
    """FLIPP Python client for accessing and querying the APASS database.

    Example
    -------

    .. code-block::

        from flipp.libs.apass import Client as APASS

        print(APASS.query(5, 5, 1.))
    """

    host = "https://www.aavso.org/"
    endpoint = "cgi-bin/apass_download.pl"
    # __cache = {}
    agent = "UC Berkeley Filippenko Group's Photometry Pipeline"

    @classmethod
    def _build_url(cls, **kwargs):
        url = "{host}/{endpoint}"
        url = url.format(host=cls.host, endpoint=cls.endpoint)
        if kwargs:
            url += "?"
            url += "&".join(["{0}={1}".format(k, v)
                             for k, v in kwargs.items()])
        return url

    @classmethod
    def _get(cls, ra, dec, radius, outtype=1):
        # cachekey = (ra, dec, radius)
        # if cachekey in cls.__cache:
        #     return cls.__cache[cachekey]
        url = cls._build_url(ra=ra, dec=dec, radius=radius, outtype=outtype)
        r = requests.get(url, headers={'User-Agent': cls.agent})
        # cls.__cache[cachekey] = r
        return r

    @classmethod
    def query(cls, ra, dec, radius, outfile=None, outtype='1'):
        """Queries the APASS database.

        Notes
        -----
        Original download and AAVSO documentation can be found at
        https://www.aavso.org/download-apass-data

        Parameters
        ----------
        ra : str, float, int
            Right Ascension in sexagesmial (HH:MM:SS, DD:MM:SS) or
            decimal degrees (##.#)
        dec : float
            Declination in sexagesmial (HH:MM:SS, DD:MM:SS) or
            decimal degrees (##.#)
        radius : float
            Radius to search around in decimal degrees (#.#)
        outtype : int, optional (Default : 1)
            This determines the datatype of the actual request to AAVSO
            Currently, only handling for csv is available, so changing this
            will break -- 0 for HTML, 1 for CSV

        Returns
        -------
        astropy.table.Table
            astropy Table of APASS search results.
        """
        r = cls._get(ra, dec, radius, outtype)
        assert r.status_code == 200, "Invalid query"
        # replace all values labeled 'NA' with NaN, so numpy can handle it
        text = r.text.replace('NA', 'NaN')
        with warnings.catch_warnings():
           warnings.simplefilter('ignore')
           table = Table.read(text, format="ascii.csv")
        if outfile:
            formats = {colname: '%8.3f' for colname in table.columns}
            ascii.write(table, output=outfile, delimiter='\t',
                        overwrite=True, formats=formats)
            print('Write to {}: Success'.format(outfile))
        return table

def main(args):
    if args.web:
        apass.query(args.ra, args.dec, args.radius, outfile=args.outfile,
                    user=args.user, password=args.password, limit=args.limit)
    else:
        apass.Client.query(
            args.ra, args.dec, args.radius, outfile=args.outfile)
