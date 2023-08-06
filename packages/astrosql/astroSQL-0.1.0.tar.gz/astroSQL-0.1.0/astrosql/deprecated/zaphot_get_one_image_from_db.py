import astropy
import argparse
import pandas as pd
import warnings
from sqlconnector import connect

def zaphot_get_one_image_from_db(query, con=None):
    if con == None:
        con = connect()
    sql_clauses = ["SELECT", "FROM", "WHERE"]

    if any([clause in query for clause in sql_clauses]):
        # Attempt to do an SQL Query
        sql_query = query
    elif len(list(query)) > 1:
        sql_query = "SELECT * FROM photometry_cal.results WHERE '{}'".format(query)
    else:
        sql_query = "SELECT * FROM photometry_cal.results WHERE basename = '{}'".format(query)
    print(sql_query)
    resultproxy = con.execute(sql_query)
    colnames = resultproxy.keys()
    if resultproxy.rowcount == None:
        warnings.warn("Query returned nothing")
        return None
    else:
        data = []
        for rows in resultproxy.fetchall():
            data.append(dict(zip(colnames, rows)))
    if len(data) == 1:
        print(data[0])
    else:
        print(data)
    df = pd.DataFrame(data=data, columns=resultproxy.keys())
    return df

def main(args):
    query = ' '.join(args.query)
    zaphot_get_one_image_from_db(query)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        usage="Query the photometry_cal.results database")
    parser.add_argument(
        'query', nargs='+', help="""
        given a SQL-like query, the program will attempt to parse the query.\n
        Given a WHERE clause like 'colA == value' queries 'SELECT * FROM results WHERE colA == value'
        """)
    args = parser.parse_args()
    df = main(args)
