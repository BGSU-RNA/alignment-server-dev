from os import getenv

try:
    #if dbmsName in (DBMS.MSSQL, DBMS.SYBASE)
    #import pymssql # not sure if these routines will also be useful
    import _mssql # stored procedure support
except ImportError:
    pass # or better to die, since none of the other functions will work?

#
#   METACODE for a single procedure run (TBD if open/close steps should be included)
#
#   (OPEN connection:  rcad.connect())
#   INITIALIZE the procedure:  conn.init_procedure(name)
#   BIND parameters:  proc.bind(value,dbtype,name=None,output=False,null=False,max_length=-1)
#       Note:  if proc.bind behaves like PHP mssql_bind(), max_length only applies to char/varchar values.
#   EXECUTE procedure:  proc.execute()
#   OBTAIN results:
#       for row in conn:
#           print "Firstname: %s, LastName: %s" % (row['firstname'],row['lastname'])
#   (CLOSE connection:  conn.close())
#


def rcad_connect():
    """
    Open connection to rCAD @ UT for data retrieval.
    """
    #   Credentials:  hostname, username, password
    #   Refactor this so that the credentials are not hardcoded within the web infrastructure.
    #       Environment variables should be a viable option.  Others?
    hostname = getenv("RCAD_HOSTNAME") if getenv("RCAD_HOSTNAME") else "crw-rcad.austin.utexas.edu:1433"
    username = getenv("RCAD_USERNAME") if getenv("RCAD_USERNAME") else "BGSU"
    password = getenv("RCAD_PASSWORD") if getenv("RCAD_PASSWORD") else "b1g4s3uDHRuNbA$"

    return _mssql.connect(server=hostname, user=username, password=password,
                          database="crwdb")
    #   option:  add 'tds_version="8.0"'
    #   option:  add 'appname="BGSU_Alignment_Server"'
    #   possible:  tinker with conn_properties.  Default looks reasonable.
    #   consider:  refactor all of these outside the web infrastructure?  (except for any local overrides?)

#def exception_handling_example():
#   try:
#       conn.execute_non_query('CREATE TABLE munge(id INT, name VARCHAR(50))')
#   except:
#       raise
#   finally:
#       conn.close()


def message_handler(message_state, severity, servername, procname, line,
                    message_text):
    """
    Prints message to stdout; assembled from information sent by the server.
    """
    print("message_handler: message_state = %d, severity = %d, procname = '%s', ",
          "line = %d, message_text = '%s'" % (message_state, severity, procname,
                                              line, message_text))


def connection_test():
    #   Sample run
    conn = rcad_connect()
    try:
        connection_info(conn)

        # conn.set_msghandler(message_handler) # Install custom handler.  Necessary?  Useful?

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
    Output information about the current Microsoft SQL Server database connection.

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
#       SQLBINARY, SQLBIT (bit), SQLBITN, SQLCHAR (char), SQLDATETIME, SQLDATETIM4, SQLDATETIMN, SQLDECIMAL,
#       SQLFLT4, SQLFLT8 (bigint?), SQLFLTN, SQLIMAGE, SQLINT1 (tinyint), SQLINT2 (smallint), SQLINT4 (int),
#       SQLINT8, SQLINTN, SQLMONEY, SQLMONEY4, SQLMONEYN, SQLNUMERIC, SQLREAL, SQLTEXT (text),
#       SQLVARBINARY, SQLVARCHAR (varchar), SQLUUID
#   see http://msdn.microsoft.com/en-us/library/cc296193.aspx for additional guidelines
#

#
#   Other (2014-10-01) stored procedures, parameters, and defaults:
#       BGSU.SeqVar_Range2 (in transition to using Unit IDs as input)
#


def seqvar_range_1(conn, pdbid, modnum, chainid, range1, range2):
    """
    Run stored procedure to collect sequence variants for a single range of positions, defined
    via the PDB sequence numbering system (using Unit IDs).

    BGSU.SeqVar_Range1
        @PDBID      char(4) # PDB identifier   (default = 2AW7)
        @ModNum     tinyint # model number     (default = 1)
        @ChainID    char(1) # chain identifier (default = A)
        @range1     int     # lower boundary of range, in PDB numbering (default = 887)
        @range2     int     # upper boundary of range, in PDB numbering (default = 894)
    """
    proc = conn.init_procedure('SeqVar_Range1')

    proc.bind(pdbid, 'SQLCHAR', '@PDBID', null=False, output=False,
              max_length=4)
    proc.bind(modnum, 'SQLINT1', '@ModNum', null=False, output=False)
    proc.bind(chainid, 'SQLCHAR', '@ChainID', null=False, output=False,
              max_length=1)
    proc.bind(range1, 'SQLINT4', '@range1', null=False, output=False)
    proc.bind(range2, 'SQLINT4', '@range2', null=False, output=False)

    proc.execute()


def results_svr1(conn):
    """
    Output results from stored procedure BGSU.SeqVar_Range1 (test).

    Currently (2014-10-01) has two output sets:  the second contains four additional columns
    The proc does not yet have logic for selecting between the two output sets
    How best to turn this into JSON?  Is that conversion necessary?
    COMMON:  0) SeqID; 1) SeqVersion; 2) CompleteFragment;
    ADDITIONAL:  3) AccessionID; 4) TaxID; 5) ScientificName; 6) LineageName.
    """

    res1 = [row for row in conn]  # first result set (three common columns)
    res2 = [row for row in conn]  # second result set (all seven columns)

    for row in res1:
        #   the three key items
        print("SeqID.SeqVersion: {}.{}, Sequence: {}".format(
            row['SeqID'], row['SeqVersion'], row['CompleteFragment']))

    for row in res2:
        #   all seven items
        print("SeqID.SeqVersion: {}.{}, Sequence: {}, Accession: {}, TaxID: {}, Scientific Name: {}, ",
              "Taxonomic Lineage: {}".format(row['SeqID'], row['SeqVersion'],
                                             row['CompleteFragment'],
                                             row['AccessionID'], row['TaxID'],
                                             row['ScientificName'],
                                             row['LineageName']))
