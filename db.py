from os import getenv

try:
    #if dbmsName in (DBMS.MSSQL, DBMS.SYBASE)
    #import pymssql # not sure if these routines will also be useful
    import _mssql # stored procedure support
except ImportError:
    pass

def rcad_connect():
    """Open connection to rCAD @ UT for data retrieval.
    """
    #   Credentials:  hostname, username, password
    hostname = getenv("RCAD_HOSTNAME") if getenv("RCAD_HOSTNAME") else "crw-rcad.austin.utexas.edu:1433"
    username = getenv("RCAD_USERNAME") if getenv("RCAD_USERNAME") else "BGSU"
    password = getenv("RCAD_PASSWORD") if getenv("RCAD_PASSWORD") else "b1g4s3uDHRuNbA$"

    conn = _mssql.connect(server='hostname',user='username',password='password',database="crwdb")

#def exception_handling_example():
#   try:
#       conn.execute_non_query('CREATE TABLE munge(id INT, name VARCHAR(50))')
#   except:
#       raise
#   finally:
#       conn.close()

def message_handler(message_state, severity, servername, procname, line, message_text):
    """
    Prints message to stdout; assembled from information sent by the server.
    """
    print("message_handler: message_state = %d, severity = %d, procname = '%s', "
            "line = %d, message_text = '%s'" % (message_state, severity, procname,
                                                line, message_text))

def connection_test():
    #   Sample run
    rcad_connect()
    try:
        conn.set_msghandler(message_handler) # Install custom handler.
        conn.execute_non_query("USE crwss") # Gets called here; should fail and produce error.

        proc = conn.init_procedure(BGSU.SeqVar_Range1)

        #   Skipping binding values for initial test.  Procedure has defaults set.

        proc.execute()

        for row in conn:
            print "SeqID.SeqVersion: {}.{}, Sequence: {}".format(row['SeqID'],row['SeqVersion'],row['CompleteFragment'])
            #   enough for testing -- if this works, we add more
    finally:
        conn.close()

def connection_info():
    print("Connected: %s\nCharset: %s\nTDS: %s" % (conn.connected(), conn.charset(), conn.tds_version()))

#
#   the key functions are poorly documented as of September 2014
#   will take some trial and error, but fortunately these functions resemble
#       the PHP PEAR stored procedure functions, which helps A LOT
#
#   Currently missing:  a good example of how to parse the results from
#       a stored procedure
#
#   conn.init_procedure(name)
#   proc.bind(value,dbtype,name=None,output=False,null=False,max_length=-1)
#   #   if proc.bind behaves like PHP mssql_bind(), max_length only applies
#   #   to char/varchar values.
#   proc.execute()
#   ??? exactly how to get results?
#   for row in conn:
#       print # something appropriate to results
#       e.g., print "Firstname: %s, LastName: %s" % (row['firstname'],row['lastname'])
#   conn.close()
#

#
#   dbtype:  one of (dbtype in CAPS, MS SQL type in parens):
#       SQLBINARY, SQLBIT (bit), SQLBITN, SQLCHAR (char), SQLDATETIME, SQLDATETIM4, 
#       SQLDATETIMN, SQLDECIMAL, SQLFLT4, SQLFLT8 (bigint?), SQLFLTN, SQLIMAGE, 
#       SQLINT1 (tinyint), SQLINT2 (smallint), SQLINT4 (int), SQLINT8, SQLINTN, 
#       SQLMONEY, SQLMONEY4, SQLMONEYN, SQLNUMERIC, SQLREAL, SQLTEXT (text), 
#       SQLVARBINARY, SQLVARCHAR (varchar), SQLUUID
#
#   see http://msdn.microsoft.com/en-us/library/cc296193.aspx for additional guidelines
#

#
#   Current (2014-09-24) stored procedures and parameters:
#       BGSU.SeqVar_Range1
#           @PDBID      char(4) # PDB identifier   (default = 2AW7)
#           @ModNum     tinyint # model number     (default = 1)
#           @ChainID    char(1) # chain identifier (default = A)
#           @range1     int     # lower boundary of range, in PDB numbering
#           @range2     int     # upper boundary of range, in PDB numbering
#       BGSU.SeqVar_Range2
#           (in transition to using Unit IDs as input)
#

def seqvar_range_1(conn):
    """
    Run stored procedure to collect sequence variants for a single range of positions, defined
    via the PDB sequence numbering system (using Unit IDs).
    """
    conn.init_procedure(seqvar_r1)
    seqvar_r1.bind(pdbid,'SQLCHAR','PDBID','False','False',4)
    seqvar_r1.bind(modnum,'SQLINT1','ModNum','False','False')
    seqvar_r1.bind(chainid,'SQLCHAR','ChainID','False','False',1)
    seqvar_r1.bind(range1,'SQLCHAR','range1','False','False')
    seqvar_r1.bind(range2,'SQLCHAR','range2','False','False')
    seqvar_r1.execute()

#
#   Output from BGSU.SeqVar_Range1 (29 September 2014):
#   #   Currently has two output sets:  the second contains four additional columns
#   #   The proc does not yet have logic for selecting between the two output sets
#   #   How best to turn this into JSON?  Is that conversion necessary?
#   COMMON:  0) SeqID; 1) SeqVersion; 2) CompleteFragment;
#   ADDITIONAL:  3) AccessionID; 4) TaxID; 5) ScientificName; 6) LineageName.
#

def results_svr1(conn):
    """
    Output results from stored procedure BGSU.SeqVar_Range1 (test).
    """
    for row in conn:
        print "SeqID.SeqVersion: %d.%d, Sequence: %s" % (row['SeqID'],row['SeqVersion'],row['CompleteFragment'])
        print "SeqID.SeqVersion: {}.{}, Sequence: {}".format(row['SeqID'],row['SeqVersion'],row['CompleteFragment'])




