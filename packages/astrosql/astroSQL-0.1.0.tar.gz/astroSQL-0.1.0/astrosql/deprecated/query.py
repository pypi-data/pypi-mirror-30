import peeweedb
import astropy.units as u


def get_by_basename(db, table, basename):
    """Get data from SQL database by basename. Returns a list of dict"""
    if isinstance(table, str):
        assert table in db.get_tables(), "Sanity Check Failed: Table queried does not exist"
        table = peeweedb.tables[table]
    else:
        table = table

    query = table.select().where(table.basename == basename)
    print(query.sql())

    data = list(query.dicts())
    return data


def get_by_radec(db, table, ra, dec, radius):
    """
    Get data from SQL database within a square area of the sky determined by ra, dec, radius.
    Returns a list of dict
    """
    radius = radius*u.arcmin.to(u.deg)
    if isinstance(table, str):
        assert table in db.get_tables(), "Sanity Check Failed: Table queried does not exist"
        table = peeweedb.tables[table]
    else:
        table = table

    query = table.select().where(
        table.centerRa.between(ra - radius, ra + radius),
        table.centerDec.between(dec - radius, dec + radius)
    )
    print(query.sql())

    data = list(query.dicts())
    return data
