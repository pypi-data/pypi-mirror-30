"""Load text-based data onto MySQL database.

Example:
    $ python data_to_mysql.py data.sum foo_db bar_table -u user -p
"""
import sys
import sqlconnector
import pandas as pd
import peeweedb


def dict2sql(db, table, data):
    """
    Write a (1, n) dictionary (single row dictionary) to mySQL.

    Parameters:
    ----------
    db  : A peewee.Database
    table : str or peewee.Model
        SQL table name or peewee.Model object to be created or appended
    data : dict
        Data to be inserted. Values cannot be array-like
    """
    if isinstance(table, str):
        assert table in db.get_tables(), "Sanity Check Failed: Table queried does not exist"
        table = peeweedb.tables[table]
    else:
        table = table
    table.create(**data)

# def dict2sql(con, table, data):
#     """
#     Write a (1, n) dictionary (single row dictionary) to mySQL.
#
#     Parameters:
#     ----------
#     con : sqlalchemy.engine.Connection or any SQL connection-like
#         SQL connection
#     table : str
#         name of SQL table to be created or appended
#     data : dict
#         Data to be inserted. Values cannot be array-like
#     """
#
#     df = pd.DataFrame(data, columns=data.keys())
#     print("Writing to database.\nThis may take a while...")
#     df.to_sql(table, con, if_exists='append', index=False)


def text2sql(con, table, file):
    # TODO: Fix column header which is not yet parseable
    df = pd.read_csv(file, header=None, sep="\s+", comment='#')

    print("\nFirst few rows of data (", args.file,
          "):to be loaded: \n{}\n".format(df.head()))
    print("\nLast few rows of data (", args.file,
          "):to be loaded: \n{}\n".format(df.tail()))
    print("Writing to database.\nThis may take a while...")

    df.to_sql(args.table, con, if_exists="append",
              index=False, chunksize=1000)


def main(args):
    con = connect(database=args.database, user=args.user,
                  password=args.password, host=args.host)

    table_exists = con.dialect.has_table(con, args.table)
    if table_exists:
        rows = con.execute(
            "SELECT COUNT(*) from {table};".format(table=args.table)).fetchone()[0]

    if args.file:
        text2sql(con, args.table, args.file)

    if not table_exists:
        con.execute(
            "ALTER TABLE `{}` ADD CONSTRAINT id PRIMARY KEY (`RA`, `DEC`);".format(args.table))
        rows = con.execute(
            "SELECT COUNT(*) from {table};".format(table=args.table)).fetchone()[0]
    else:
        rows = con.execute(
            "SELECT COUNT(*) from {table};".format(table=args.table)).fetchone()[0] - rows
    print("Finished with {} rows written/appended to MySQL:{}/{}. The last few data stored were:".format(rows, args.database, args.table))
    # print(con.execute("SELECT * from {table} ORDER BY id DESC LIMIT 5;".format(table=args.table)).fetchall())

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter) #description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter
#     parser.add_argument("file", help="absolute or relative path to file")
#     parser.add_argument("database", help="MySQL database to write")
#     parser.add_argument("table", help="MySQL table to create or append")
#     parser.add_argument("-u", "--user", default=getpass.getuser(), help="MySQL username (default: $USER)")
#     parser.add_argument("-p", "--password", nargs='?', const=1, help="enable MySQL password to be entered later '-p' or set it '-p myPassword'. (default: disable password)")
#     parser.add_argument("--host", default="localhost", help="hostname where MySQL is hosted (default: 'localhost')")
#     parser.add_argument(
#         "-c", "--column_header",
#         default=['Name', 'RA', 'raerr', 'DEC', 'decerr', 'nobs', 'mobs', 'V', '(B-V)', 'B', "g'", "r'", "i'", "Verr", "(B-V)err", 'Berr', "g'err", "r'err", "i'err"],
#         help="Specify column header names for the table as a list of python strings [\"col1\", \"col2\", ...] default:['Name', 'RA', 'raerr', 'DEC', 'decerr', 'nobs', 'mobs', 'V', '(B-V)', 'B', \"g'\", \"r'\", \"i'\", \"Verr\", \"(B-V)err\", 'Berr', \"g'err\", \"r'err\", \"i'err\"]")
#     args = parser.parse_args()
#     main(args)
