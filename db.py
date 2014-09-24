from os import getenv
#import pymssql # not sure if these routines will also be useful
import _mssql # stored procedure support

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

#   Sample run
rcad_connect()
try:
    conn.set_msghandler(message_handler) # Install custom handler.
    conn.execute_non_query("USE crwss") # Gets called here; should fail.
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
#   proc.execute()

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
