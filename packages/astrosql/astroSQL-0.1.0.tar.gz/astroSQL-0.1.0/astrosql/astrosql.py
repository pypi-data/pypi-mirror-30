import peewee
import pandas as pd
import astropy.units as u
from pathlib import Path
from pwiz import Introspector


class AstroSQL:

    def __init__(self, db):
        """

        Parameters
        ----------
        db : peewee.MySQLDatabase
             A MySQL peewee database see [documentation](http://docs.peewee-orm.com/en/latest/peewee/database.html#using-mysql)
        """
        if isinstance(db, peewee.MySQLDatabase):
            self.db = db
        elif isinstance(str, db):
            raise NotImplementedError
        else:
            raise ValueError('argument [db] is neither a peewee.MySQLDatabase, nor a string')

        self.tables = Introspector.from_database(db).generate_models(literal_column_names=True)

    def get_table(self, table):
        """

        Parameters
        ----------
        table : str, peewee.BaseModel, peewee.Model
                Table queried in the database

        Returns
        -------
        list
            A list of rows as dict

        """
        if issubclass(type(table), peewee.BaseModel) or issubclass(type(table), peewee.Model):
            table = table
        elif isinstance(table, str):
            assert table in self.tables, "Sanity Check Failed: Table queried does not exist"
            table = self.tables[table]
        else:
            raise ValueError("argument [table] is neither a string or peewee.Model or peewee.BaseModel")
        return table

    def dict2sql(self, table, data):
        """
        Write a (1, n) dictionary (single row dictionary) to mySQL.

        Parameters
        ----------
        table : str, peewee.BaseModel, peewee.Model
                Table to be written to
        data : dict
                Data to be written, must match the columns of `table`

        """
        assert isinstance(data, dict), "argument [data] is not a Python dictionary"
        table = self.get_table(table)

        table.create(**data)

    def text2sql(self, table, file):
        """

        Parameters
        ----------
        table : str
        file : file, str, or pathlib.Path
        """
        # TODO: Fix column header which is not yet parseable

        if isinstance(file, str):
            assert Path(str).exists(), "{} is not a valid file path or does not exit".format(file)
        table = self.get_table(table)

        df = pd.read_csv(file, header=None, sep="\s+", comment='#')

        print("\nFirst few rows of data (", args.file,
              "):to be loaded: \n{}\n".format(df.head()))
        print("\nLast few rows of data (", args.file,
              "):to be loaded: \n{}\n".format(df.tail()))
        print("Writing to database.\nThis may take a while...")

        data = df.to_dict('records')
        table.insert_many(data)

    def get_by_basename(self, table, basename):
        """
        Get data from SQL database by the unique key basename.

        Parameters
        ----------
        table : str, peewee.BaseModel, peewee.Model
                Table queried in the database
        basename : str
                The base name queried from the unique key `basename` of the database

        Returns
        -------
        list
            A list of rows as dict

        """
        table = self.get_table(table)

        query = table.select().where(table.basename == basename)
        print(query.sql())

        data = list(query.dicts())
        return data

    def get_by_object(self, table, objname):
        """
        Get data from SQL database by the column `objname`

        Parameters
        ----------
        table : str, peewee.BaseModel, peewee.Model
                Table queried in the database
        objname : str
                Object name queried from the `objname` column of the database

        Returns
        -------
        list
            A list of rows as dict

        """
        table = self.get_table(table)

        query = table.select().where(table.objname == objname)
        print(query.sql())

        data = list(query.dicts())
        return data

    def get_by_radec(self, table, ra, dec, radius):
        """
        Get data from SQL database within a square area of the sky determined by ra, dec, radius.

        Parameters
        ----------
        table : str, peewee.BaseModel, peewee.Model
             Table queried in the database
        ra : float
             The right ascension in degrees corresponding to the center of the queried box
        dec : float
             The declination in degrees corresponding to the center of the queried box
        radius : float
             The radius in arc minutes which is the square radius of the queried box.

        Returns
        -------
        list
            A list of rows as dict

        """
        table = self.get_table(table)

        radius = radius * u.arcmin.to(u.deg)

        try:
            query = table.select().where(
                table.RA.between(ra - radius, ra + radius),
                table.DEC.between(dec - radius, dec + radius)
            )
        except AttributeError:
            query = table.select().where(
                table.centerRa.between(ra - radius, ra + radius),
                table.centerDec.between(dec - radius, dec + radius)
            )

        print(query.sql())

        data = list(query.dicts())
        return data

