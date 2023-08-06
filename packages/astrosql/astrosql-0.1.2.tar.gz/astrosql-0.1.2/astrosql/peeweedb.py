from astrosql.config import get_config
from peewee import *

config = get_config()
HOST = config['mysql'].get('host', 'localhost')
DATABASE = config['mysql'].get('database')
USER = config['mysql'].get('user')
PASSWORD = config['mysql'].get('password')
uri = 'mysql+mysqlconnector://{0}:{1}@{2}/{3}'.format(
    USER, PASSWORD, HOST, DATABASE)

db = MySQLDatabase(DATABASE, user=USER, password=PASSWORD, host='localhost')


class MySQLModel(Model):
    class Meta:
        database = db


class Images(MySQLModel):
    basename = CharField(unique=True)
    name = TextField(null=True)
    telescope = TextField(null=True)
    pixscale = DoubleField(null=True)
    day = TextField(null=True)
    month = TextField(null=True)
    year = TextField(null=True)
    hour = TextField(null=True)
    minute = TextField(null=True)
    second = TextField(null=True)
    mjd = DoubleField(null=True)
    jd = DoubleField(null=True)
    Xsize = BigIntegerField(null=True)
    Ysize = BigIntegerField(null=True)
    exptime = DoubleField(null=True)
    filter = TextField(null=True)
    uniformname = TextField(null=True)
    savepath = TextField(null=True)
    WCSED = TextField(null=True)
    centerRa = DoubleField(null=True)
    centerDec = DoubleField(null=True)
    corner1Ra = DoubleField(null=True)
    corner1Dec = DoubleField(null=True)
    corner2Ra = DoubleField(null=True)
    corner2Dec = DoubleField(null=True)
    corner3Ra = DoubleField(null=True)
    corner3Dec = DoubleField(null=True)
    corner4Ra = DoubleField(null=True)
    corner4Dec = DoubleField(null=True)
    fwhm = DoubleField(null=True)
    sky = DoubleField(null=True)
    zeromag = DoubleField(null=True)
    limitmag = DoubleField(null=True)

    class Meta:
        database = db
        primary_key = CompositeKey('centerRa', 'centerDec')
        db_table = 'images2'


class Test(MySQLModel):
    basename = CharField(unique=True)
    name = TextField(null=True)
    telescope = TextField(null=True)
    pixscale = DoubleField(null=True)
    day = TextField(null=True)
    month = TextField(null=True)
    year = TextField(null=True)
    hour = TextField(null=True)
    minute = TextField(null=True)
    second = TextField(null=True)
    mjd = DoubleField(null=True)
    jd = DoubleField(null=True)
    Xsize = BigIntegerField(null=True)
    Ysize = BigIntegerField(null=True)
    exptime = DoubleField(null=True)
    filter = TextField(null=True)
    uniformname = TextField(null=True)
    savepath = TextField(null=True)
    WCSED = TextField(null=True)
    centerRa = DoubleField(null=True)
    centerDec = DoubleField(null=True)
    corner1Ra = DoubleField(null=True)
    corner1Dec = DoubleField(null=True)
    corner2Ra = DoubleField(null=True)
    corner2Dec = DoubleField(null=True)
    corner3Ra = DoubleField(null=True)
    corner3Dec = DoubleField(null=True)
    corner4Ra = DoubleField(null=True)
    corner4Dec = DoubleField(null=True)
    fwhm = DoubleField(null=True)
    sky = DoubleField(null=True)
    zeromag = DoubleField(null=True)
    limitmag = DoubleField(null=True)

    class Meta:
        database = db
        primary_key = CompositeKey('centerRa', 'centerDec')
        db_table = 'test'

tables = {
    Images._meta.db_table: Images,
    Test._meta.db_table: Test,
}

# Use this to create the following table
# Images.create_table() #