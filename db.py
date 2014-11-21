try:
    import _mssql  # stored procedure support
except ImportError:
    pass  # or better to die, since none of the other functions will work?


def rcad_connect(config):
    """
    Open connection to rCAD @ UT for data retrieval.
    """
    hostname = config.get("RCAD_HOSTNAME", "crw-rcad.austin.utexas.edu:1433")
    username = config.get("RCAD_USERNAME", "BGSU")
    username = config.get("RCAD_USERNAME", "BGSU")
    password = config.get("RCAD_PASSWORD", "b1g4s3uDHRuNbA$")

    return _mssql.connect(server=hostname, user=username, password=password,
                          database="crwdb")


def seqvar(db, pdb, model, ranges):
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

    proc.execute()

    # This copying is done because result dict also allows access by index, we
    # only want the entries with keys.
    res1 = [row for row in db]
    res2 = [row for row in db]
    res3 = [row for row in db]

    full = []
    for row in res1:
        print("SeqID.SeqVersion: {}.{}, Sequence: {}".format(
            row['SeqID'], row['SeqVersion'], row['CompleteFragment']))
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
            'CompleteFragment': row['CompleteFragment']
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
