from os import getenv

try:
    #if dbmsName in (DBMS.MSSQL, DBMS.SYBASE)
    #import pymssql # not sure if these routines will also be useful
    import _mssql # stored procedure support
except ImportError:
    pass # or better to die, since none of the other functions will work?


#
#   METACODE for a single procedure run
#   (TBD if open/close steps should be included)
#
#   (OPEN connection:  rcad.connect())
#   INITIALIZE the procedure:  conn.init_procedure(name)
#   BIND parameters:  proc.bind(value,dbtype,name=None,output=False,null=False,
#       max_length=-1)
#       Note:  if proc.bind behaves like PHP mssql_bind(), max_length only
#       applies to char/varchar values.
#   EXECUTE procedure:  proc.execute()
#   OBTAIN results:
#       for row in conn:
#           print "Firstname: %s, LastName: %s" % (row['fname'],row['lname'])
#   (CLOSE connection:  conn.close())
#


def rcad_connect():
    """
    Open connection to rCAD @ UT for data retrieval.
    """
    #   Credentials:  hostname, username, password
    #   Refactor this so that the credentials are not hardcoded within the web
    #       infrastructure.  Environment variables should be a viable option.
    #       Others?
    hostname = getenv("RCAD_HOSTNAME") if getenv("RCAD_HOSTNAME") \
        else "crw-rcad.austin.utexas.edu:1433"
    username = getenv("RCAD_USERNAME") if getenv("RCAD_USERNAME") else "BGSU"
    password = getenv("RCAD_PASSWORD") if getenv("RCAD_PASSWORD") \
        else "b1g4s3uDHRuNbA$"

    return _mssql.connect(server=hostname, user=username, password=password,
                          database="crwdb")
    #   option:  add 'tds_version="8.0"'
    #   option:  add 'appname="BGSU_Alignment_Server"'
    #   possible:  tinker with conn_properties.  Default looks reasonable.
    #   consider:  refactor all of these outside the web infrastructure?
    #       (except for any local overrides?)


#
#   NOTES for Parameter Binding:
#
#   dbtype:  one of (dbtype in CAPS, MS SQL type in parens):
#       SQLBINARY, SQLBIT (bit), SQLBITN, SQLCHAR (char), SQLDATETIME,
#       SQLDATETIM4, SQLDATETIMN, SQLDECIMAL, SQLFLT4, SQLFLT8 (bigint?),
#       SQLFLTN, SQLIMAGE, SQLINT1 (tinyint), SQLINT2 (smallint),
#       SQLINT4 (int), SQLINT8, SQLINTN, SQLMONEY, SQLMONEY4, SQLMONEYN,
#       SQLNUMERIC, SQLREAL, SQLTEXT (text), SQLVARBINARY,
#       SQLVARCHAR (varchar), SQLUUID
#   additional info: http://msdn.microsoft.com/en-us/library/cc296193.aspx
#


#
#   TODO:  build against new stored procedure (BGSU.SeqVar)
#
#   Parameters (database type):
#       @PDBID (char(4))
#       @ModNum (tinyint)
#       (five sets of, where 1 <= N <= 5)
#           @ChainN (char(1))
#           @rangeNa (int)
#           @rangeNb (int)
#
#   Results (database type):
#       SeqID (int)
#       SeqVersion (tinyint)
#       CompleteFragment (varchar(2504))
#       AccessionID (varchar(50))
#       TaxID (int)
#       ScientificName (varchar(8000))
#       LineageName (varchar(8000))
#
#   For ranges 2-5, @ChainN defaults to NULL, and @rangeNa and @rangeNb default
#       to 0.  The procedure attempts to process multiple ranges only when
#       @ChainN is not NULL and both @rangeNa and @rangeNb are greater than 0.
#
#   Other defaults (which may need to change):
#       @PDBID:  '2AW7'
#       @ModNum:  1
#       @Chain1:  'A'
#       @range1a:  887
#       @range1b:  894
#
#   TODO:  for each range (rangeNa:rangeNb), ensure that rangeNa <= rangeNb.
#       Swap values if reversed.  Proc fails if range1 > range2 (BETWEEN
#       keyword).
#
#   TODO:  ensure that ranges are filled in order.  If range 2 is empty and
#       range 3 is occupied, only range 1 will be displayed.
#
#   N.B.  Ranges do not need to occur in order; i.e., range 1 may be 235-240
#       while range 2 is 115-135.  (Gives the user some flexibility in how
#       their selections will be displayed.)
#


def seqvar(db, pdb, model, ranges):
    if 2 <= len(ranges) <= 5:
        raise ValueError("Invalid range length")

    proc = db.init_procedure('BGSU.SeqVar')

    proc.bind(pdb, _mssql.SQLCHAR, '@PDBID', null=False, output=False,
              max_length=4)
    proc.bind(model, _mssql.SQLINT1, '@ModNum', null=False, output=False)

    all_ranges = list(ranges)
    all_ranges.extend([('', False, False)] * (5 - len(ranges)))

    for index, (chain, start, stop) in enumerate(all_ranges):
        name = '@range%s' % (index + 1)
        chain_name = '@Chain%s' % (index + 1)
        proc.bind(chain, _mssql.SQLCHAR, chain_name, null=False, output=False,
                  max_length=1)
        proc.bind(start, _mssql.SQLINT4, name + 'a', null=False, output=False)
        proc.bind(stop, _mssql.SQLINT4, name + 'b', null=False, output=False)

    proc.execute()

    # This copying is done because result dict also allows access by index, we
    # only want the entries with keys.
    data = []
    for row in db:
        data.append({
            'SeqID': row['SeqID'],
            'SeqVersion': row['SeqVersion'],
            'CompleteFragment': row['CompleteFragment'],
            'AccessionID': row['AccessionID'],
            'TaxID': row['TaxID'],
            'ScientificName': row['ScientificName'],
            'LineageName': row['LineageName'],
        })
    return data


def get_translation(conn, pdb, model, chain):
    """
    Contact rCAD for the translation table (to account for insertion codes in
    the PDB file) for a given PDBID, model, and chain.

    As presently written (2014-10-09), only operates on one chain at a time, so
    would need to be called multiple times if multiple chains are being queried.

    In current form (2014-10-09), returns the "chain number" (the sequence
    number used in PDB ATOM records), the "chain insertion code" (a single
    alphanumeric character; a dash is stored in rCAD for entries with no
    insertion code to enforce NOT NULL on the column and allow for key
    creation), and the "natural number" (the sequence numbering, from 1 to n,
    based upon the PDB SEQRES records).

    #   TODO:  consider merging chain number/insertion code (with NULL passed
    #   for positions with no insertion code)?
    #
    #   TODO:  consider revising to accept multiple (up to five, for
    #   consistency with BGSU.SeqVar) ChainID values.  Could require dynamic
    #   SQL approach (more involved, worth effort?).
    #
    """
    proc = conn.init_procedure('BGSU.GetPDBTranslation')
    proc.bind(pdb, _mssql.SQLCHAR, '@PDBID', null=False, output=False,
              max_length=4)
    proc.bind(model, _mssql.SQLINT1, '@ModNum', null=False, output=False)
    proc.bind(chain, _mssql.SQLCHAR, '@ChainID', null=False, output=False,
              max_length=1)
    proc.execute()

    return [row for row in conn]


def list_options(conn):
    """
    Contact rCAD for the list of available structure-alignment mappings and
    return the list.

    No input parameters required.

    Returns five columns per entry:  PDBID (char(4)), ModelNumber (tinyint),
    ChainID (char(1)), Requires_Translation (bit), Description (varchar(100)).
    """

    #   TODO:  identify any missing elements and add them.

    proc = conn.init_procedure('BGSU.ListAlnServerOptions')
    proc.execute()

    data = []
    for row in conn:
        data.append({
            'pdb': row['PDBID'],
            'model_number': row['ModelNumber'],
            'chain_id': row['ChainID'],
            'description': row['Description'],
            'requires_translation': row['Requires_Translation']
        })
    return data
