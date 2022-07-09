# common/sap.py
# SAP query with RFC_READ_TABLE

"""A function to query SAP with RFC_READ_TABLE
"""
def sap_qry(conn, SQLTable,  Fields, Where = '', MaxRows=50, FromRow=0):
    
    # By default, if you send a blank value for fields, you get all of them
    # Therefore, we add a select all option, to better mimic SQL.
    if Fields[0] == '*':
        Fields = ''
    else:
        Fields = [{'FIELDNAME':x} for x in Fields] # Notice the format
        # pass

    # the WHERE part of the query is called "options"
    options = [{'TEXT': x} for x in Where] # again, notice the format

    # we set a maximum number of rows to return, because it's easy to do and
    # greatly speeds up testing queries.
    rowcount = MaxRows

    # Here is the call to SAP's RFC_READ_TABLE
    tables = conn.call("RFC_READ_TABLE", QUERY_TABLE=SQLTable, DELIMITER='|', FIELDS = Fields, \
                        OPTIONS=options, ROWCOUNT = MaxRows, ROWSKIPS=FromRow)

    # We split out fields and fields_name to hold the data and the column names
    fields = []
    fields_name = []

    data_fields = tables["DATA"] # pull the data part of the result set
    data_names = tables["FIELDS"] # pull the field name part of the result set

    headers = [x['FIELDNAME'] for x in data_names] # headers extraction
    long_fields = len(data_fields) # data extraction
    long_names = len(data_names) # full headers extraction if you want it

    # now parse the data fields into a list
    for line in range(0, long_fields):
        fields.append(data_fields[line]["WA"].strip())

    # for each line, split the list by the '|' separator
    fields = [x.strip().split('|') for x in fields ]

    # return the 2D list and the headers
    return fields, headers

