"""Load text-based data onto MySQL database.

Example:
    $ python data_to_mysql.py data.sum foo_db bar_table -u user -p
"""
import argparse
import getpass
import pandas as pd
from astrosql.sqlconnector import connect

# Alias #



def main(args):
    if args.password: args.password = getpass.getpass("Password: ")
    con = connect(args.database, user=args.user, password=args.password, host=args.host)

    table_exists = con.dialect.has_table(con, args.table)

    df = pd.read_csv(args.file, header=None, sep="\s+", comment='#')
    df = df.drop(int(args.skipcols), axis=1)
    df.columns = args.column_header
    print("\nFirst few rows of data (", args.file, "):to be loaded: \n")
    print("{}\n".format(df.head()))
    print("Last few rows of data (", args.file, "):to be loaded: \n")
    print("{}\n".format(df.tail()))

    print("Writing to database.")
    print("\nThis may take a while...")
    df.to_sql(args.table, con, if_exists="append",
                index=False, chunksize=1000)

    if (not table_exists):
        con.execute("ALTER TABLE `{}` ADD CONSTRAINT id PRIMARY KEY (`RA`, `DEC`);".format(args.table)) 
        rows = con.execute(
            "SELECT COUNT(*) from {table};".format(table=args.table)).fetchone()[0]
    else:
        rows = con.execute("SELECT COUNT(*) from {table};".format(table=args.table)).fetchone()[0] - rows
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
