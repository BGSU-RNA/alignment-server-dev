from os import getenv
import itertools as it

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


def connection_test():
    """
    Sample run.  Test key components with default-ish values.
    """
    conn = rcad_connect()
    try:
        connection_info(conn)

        #   Manually binding the default values for initial test.
        pdbid   = "2AW7"
        modnum  = 1
        chainid = "A"
        range1  = 887
        range2  = 894

        seqvar_range_1(conn, pdbid, modnum, chainid, range1, range2)
        results_svr1(conn)
    finally:
        conn.close()


def connection_info(conn):
    """
    Output information about the current Microsoft SQL Server database 
    connection.

    Available fields:
        connected // charset // identity // query_timeout
        rows_affected // debug_queries // tds_version
    """
    print("Connected: {}\nCharset: {}\nTDS: {}".format(conn.connected,
                                                       conn.charset,
                                                       conn.tds_version))


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


def seqvar(db, pdb, model, chain, *ranges):
    if 2 <= len(ranges) <= 5:
        name = 'BGSU.SeqVar_Range%s' % (len(ranges) - 1)
    else:
        raise ValueError("Invalid range length")

    proc = db.init_procedure(name)

    proc.bind(pdb, _mssql.SQLCHAR, '@PDBID', null=False, output=False,
              max_length=4)
    proc.bind(model, _mssql.SQLINT1, '@ModNum', null=False, output=False)
    proc.bind(chain, _mssql.SQLCHAR, '@ChainID', null=False, output=False,
              max_length=1)
    for index, value in enumerate(ranges):
        name = '@range%s' % (index + 1)
        proc.bind(value, _mssql.SQLINT4, name, null=False, output=False)

    proc.execute()

    # Probably not needed to copy into a new dict
    return [dict(row) for row in db]


def seqvar_range_1(conn, pdbid, modnum, chainid, range1, range2):
    """
    Run stored procedure to collect sequence variants for a single range of 
    positions, defined via the PDB sequence numbering system (using Unit IDs).

    BGSU.SeqVar_Range1 (defaults)
        @PDBID      char(4) # PDB identifier (2AW7)
        @ModNum     tinyint # model number (1)
        @ChainID    char(1) # chain identifier (A)
        @range1     int     # lower boundary of range, in PDB numbering (887)
        @range2     int     # upper boundary of range, in PDB numbering (894)
    """
    proc = conn.init_procedure('BGSU.SeqVar_Range1')

    proc.bind(pdbid, _mssql.SQLCHAR, '@PDBID', null=False, output=False,
              max_length=4)
    proc.bind(modnum, _mssql.SQLINT1, '@ModNum', null=False, output=False)
    proc.bind(chainid, _mssql.SQLCHAR, '@ChainID', null=False, output=False,
              max_length=1)
    proc.bind(range1, _mssql.SQLINT4, '@range1', null=False, output=False)
    proc.bind(range2, _mssql.SQLINT4, '@range2', null=False, output=False)

    proc.execute()


def results_svr1(conn):
    """
    Output results from stored procedure BGSU.SeqVar_Range1.

    How best to turn this into JSON?  Is that conversion necessary?
    FIELDS:  0) SeqID; 1) SeqVersion; 2) CompleteFragment; 3) AccessionID; 
        4) TaxID; 5) ScientificName; 6) LineageName.
    """

    res = [row for row in conn]

    for row in res:
        print("SeqID.SeqVersion: {}.{}, Sequence: {}, Accession: {}, ",
              "TaxID: {}, Scientific Name: {}, ",
              "Taxonomic Lineage: {}".format(row['SeqID'], row['SeqVersion'],
                                             row['CompleteFragment'],
                                             row['AccessionID'], row['TaxID'],
                                             row['ScientificName'],
                                             row['LineageName']))
