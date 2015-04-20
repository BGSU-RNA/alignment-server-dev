import re

from sqlalchemy import MetaData
from sqlalchemy.ext.automap import automap_base


metadata = MetaData()
Base = automap_base(metadata=metadata)


def camelize_classname(base, tablename, table):
    return str(tablename[0].upper() +
               re.sub(r'_(\w)', lambda m: m.group(1).upper(), tablename[1:]))


def reflect(engine):
    if 'PdbCoordinates' in globals():
        return
    metadata.bind = engine
    metadata.reflect(views=True)
    Base.prepare(classname_for_table=camelize_classname)
    for klass in Base.classes:
        globals()[klass.__name__] = klass
