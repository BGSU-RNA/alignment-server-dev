import logging

import _mssql


class ConnectionException(Exception):
    """Raised when we can't generate a good connection.
    """
    pass


class ProcessingException(Exception):
    """Raised when we can't process a range in the database.
    """
    pass


logger = logging.getLogger(__name__)


def connect(config):
    """
    Open connection to rCAD @ UT for data retrieval.
    """
    conf = config['rcad']['connection']
    hostname = conf.get("RCAD_HOSTNAME", "crw-rcad.austin.utexas.edu:1433")
    username = conf.get("RCAD_USERNAME", "BGSU")
    password = conf.get("RCAD_PASSWORD", "b1g4s3uDHRuNbA$")

    try:
        return _mssql.connect(server=hostname, user=username,
                              password=password, database="crwdb")
    except Exception as err:
        logger.error("Failed to connect with %s:%s@%s", username, password,
                     hostname)
        logger.exception(err)
        raise


def seqvar(db, pdb, model, ranges, m3daid):
    proc = db.init_procedure('BGSU.SeqVar')

    proc.bind(pdb, _mssql.SQLCHAR, '@PDBID', null=False, output=False,
              max_length=4)
    proc.bind(model, _mssql.SQLINT1, '@ModNum', null=False, output=False)

    # This copies the list of ranges to a new list and then appends as many
    # empty default valuse as needed.
    all_ranges = list(ranges)
    all_ranges.extend([({}, {})] * (5 - len(ranges)))

    for index, (start, stop) in enumerate(all_ranges):
        chain = start.get('chain', '')
        name = '@range%s' % (index + 1)

        chain_name = '@Chain%s' % (index + 1)

        proc.bind(chain, _mssql.SQLCHAR, chain_name, null=False, output=False,
                  max_length=1)
        proc.bind(start.get('number', False), _mssql.SQLINT4, name + 'a',
                  null=False, output=False)
        proc.bind(stop.get('number', False), _mssql.SQLINT4, name + 'b',
                  null=False, output=False)

    proc.bind(m3daid, _mssql.SQLINT1, '@M3DAID', null=False, output=False)

    try:
        proc.execute()
    except Exception as err:
        logging.error("Failed to process %s %s %s", pdb, ranges, m3daid)
        logging.exception(err)
        raise ProcessingException()

    # This copying is done because result dict also allows access by index, we
    # only want the entries with keys.
    res1 = [row for row in db]
    res2 = [row for row in db]
    res3 = [row for row in db]

    full = []
    for row in res1:
        full.append({
            'SeqID': row['SeqID'],
            'SeqVersion': row['SeqVersion'],
            'CompleteFragment': row['CompleteFragment'],
            'AccessionID': row['AccessionID'],
            'TaxID': row['TaxID'],
            'ScientificName': row['ScientificName'],
            'LineageName': row['LineageName'],
        })

    summ = []
    for row in res2:
        summ.append({
            'CompleteFragment': row['CompleteFragment'],
            'NumberOfAppearances': row['NumberOfAppearances']
        })

    reqs = []
    for row in res3:
        reqs.append({
            'SeqID': row['SeqID'],
            'SeqVersion': row['SeqVersion'],
            'CompleteFragment': row['CompleteFragment'],
            'TotalCount': row['TotalCount'],
            'NumColumns': row['NumColumns']
        })

    return full, summ, reqs


def seqvarM3A(db, pdb, model, ranges, m3daid):
    proc = db.init_procedure('BGSU.SeqVar_TEST_Map3DAlnID')

    proc.bind(pdb, _mssql.SQLCHAR, '@PDBID', null=False, output=False,
              max_length=4)
    proc.bind(model, _mssql.SQLINT1, '@ModNum', null=False, output=False)

    # This copies the list of ranges to a new list and then appends as many
    # empty default values as needed.
    all_ranges = list(ranges)
    all_ranges.extend([({}, {})] * (5 - len(ranges)))

    for index, (start, stop) in enumerate(all_ranges):
        chain = start.get('chain', '')
        name = '@range%s' % (index + 1)

        chain_name = '@Chain%s' % (index + 1)

        proc.bind(chain, _mssql.SQLCHAR, chain_name, null=False, output=False,
                  max_length=1)
        proc.bind(start.get('number', False), _mssql.SQLINT4, name + 'a',
                  null=False, output=False)
        proc.bind(stop.get('number', False), _mssql.SQLINT4, name + 'b',
                  null=False, output=False)

    proc.bind(m3daid, _mssql.SQLINT1, '@M3DAID', null=False, output=False)

    try:
        proc.execute()
    except Exception as err:
        logging.error("Failed to process %s %s %s", pdb, ranges, m3daid)
        logging.exception(err)
        raise ProcessingException()

    # This copying is done because result dict also allows access by index, we
    # only want the entries with keys.
    res1 = [row for row in db]
    res2 = [row for row in db]
    res3 = [row for row in db]

    full = []
    for row in res1:
        full.append({
            'SeqID': row['SeqID'],
            'SeqVersion': row['SeqVersion'],
            'CompleteFragment': row['CompleteFragment'],
            'AccessionID': row['AccessionID'],
            'TaxID': row['TaxID'],
            'ScientificName': row['ScientificName'],
            'LineageName': row['LineageName'],
        })

    summ = []
    for row in res2:
        summ.append({
            'CompleteFragment': row['CompleteFragment'],
            'NumberOfAppearances': row['NumberOfAppearances']
        })

    reqs = []
    for row in res3:
        reqs.append({
            'SeqID': row['SeqID'],
            'SeqVersion': row['SeqVersion'],
            'CompleteFragment': row['CompleteFragment'],
            'TotalCount': row['TotalCount'],
            'NumColumns': row['NumColumns']
        })

    return full, summ, reqs


def get_translation(conn, pdb, model, chain):
    """
    Contact rCAD for the translation table (to account for insertion codes in
    the PDB file) for a given PDBID, model, and chain.

    As presently written (2014-10-09), only operates on one chain at a time, so
    would need to be called multiple times if multiple chains are being
    queried.

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

    translation = {}
    for row in conn:
        ins_code = row['ChainNumberIC']
        if ins_code == '-':
            ins_code = None
        translation[(row['ChainNumber'], ins_code)] = row['NaturalNumber']
    return translation


def list_options(conn):
    """
    Contact rCAD for the list of available structure-alignment mappings and
    return the list.

    No input parameters required (beyond connection).

    Returns six columns per entry:  PDBID (char(4)), ModelNumber (tinyint),
    ChainID (char(1)), Map3DAlnID (tinyint), Requires_Translation (bit),
    Description (varchar(100)).
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
            'option': row['Map3DAlnID'],
            'description': row['Description'],
            'requires_translation': row['Requires_Translation']
        })
    return data


def list_structures(conn):
    """
    Contact rCAD for the list of available structures (PDB + model).

    Necessary to split like this to handle queries between chains within
    a model.

    No input parameters required (beyond connection).
    """

    proc = conn.init_procedure('BGSU.ListAlnServerStructures')
    proc.execute()

    data = []
    for row in conn:
        data.append({
            'pdb': row['PDBID'],
            'model_number': row['ModelNumber'],
            'organism': row['Description_Organism'],
            'taxonomy': row['Description_Taxonomy'],
            'contents': row['Description_Contents']
        })
    return data


def all_options(conn):
    """
    Basically, the 'One Ring' of rCAD configuration.

    Replaces ListAlnServerStructures, ListAlnServerOptions, and
    GetPDBTranslation.  In testing, returns all three data sets in
    approximately two seconds while eliminating two round-trips from BGSU to
    rCAD.

    No input parameters required (beyond connection).
    """

    proc = conn.init_procedure('BGSU.AlnServerOptions')
    proc.execute()

    res1 = [row for row in conn]
    res2 = [row for row in conn]
    res3 = [row for row in conn]

    pdbs = []
    for row in res1:
        pdbs.append({
            'pdb': row['PDBID'],
            'model_number': row['ModelNumber'],
            'organism': row['Description_Organism'],
            'taxonomy': row['Description_Taxonomy'],
            'contents': row['Description_Contents']
        })

    opts = []
    for row in res2:
        opts.append({
            'pdb': row['PDBID'],
            'model_number': row['ModelNumber'],
            'chain_id': row['ChainID'],
            'option': row['Map3DAlnID'],
            'description': row['Description'],
            'requires_translation': row['Requires_Translation'],
            'crw_diagram': row['CRWSiteDiagramLink'],
            'crw_aln_dir': row['CRWSiteAlnDirectory'],
            'crw_aln_fil': row['CRWSiteAlnFilenameRoot']
        })

    tran = []
    for row in res3:
        tran.append({
            'pdb': row['PDBID'],
            'model_number': row['ModelNumber'],
            'chain_id': row['ChainID'],
            'chain_number': row['ChainNumber'],
            'chain_number_ic': row['ChainNumberIC'],
            'natural_number': row['NaturalNumber']
        })

    return pdbs, opts, tran
