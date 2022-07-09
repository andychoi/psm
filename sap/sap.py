# common/sap.py
from django.conf import settings
from pyrfc import Connection
from time import time

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


def get_sap_emp_data():

    table = 'ZSUSRMT0010'
    fields = ['USER_ID', 'CREATE_DATE', 'TERMINATE_DATE', 'USER_NAME', 'EMAIL', 'COSTCENTER', 'DEPT_CODE', 'DEPT_NAME', 'CHARGE_JOB', 'POS_LEVEL', 'SUPERVISORID', 'DUTY_CODE' ]
    where  = []    # "USER_ID = 'xxx'"    # "TERMINATE_DATE = '00000000'" ] -> terminated -> delete from current emp table  
    maxrows = 10000
    # starting row to return
    fromrow = 0

    with Connection(**settings.SAP_CONN) as conn:
        # query SAP
        results, headers = sap_qry(conn, table, fields, where, maxrows, fromrow)

    # get latest per emp_id, create_date, sort first / better to select latest... 
    sorted_results = sorted( results, key=lambda x:( x[0], x[1] ) )

    # remove all left/right spaces
    for r in sorted_results:
        r[:] = [info.strip() for info in r]

    return sorted_results

# ABAP debug: Put external break point into the RFC fm and enter the Tcode SRDEBUG
def get_opex_summary(Where = ''):

    sap_connection = settings.SAP_CONFIG['servers']['IDE']

    # the WHERE part of the query is called "options"
    Where = {} # 'AND GJAHR EQ 2022' }
    options = [{'TEXT': x} for x in Where] # again, notice the format
    tables = []
    with Connection(**sap_connection) as conn:
        try:
            result = conn.call('ZPS_ANNUAL_ORDER', ET_TAB=[]) #, OPTIONS=options)
        except Exception as e:
            pass

    # for item in tables['ET_TAB']:
        # if item['ZZLARGE'] == 'S':
        # tObj = {}
        #     tObj['PSPID'] = item['PSPID']
            # data[ tObj['PSPID'] ] = tObj


def rfc_func_desc(dict_sap_con, func_name):
    '''consult the RFC description and needed input fields
    
    Parameters
    ----------
    dict_sap_con : dict
        key to create connection with SAP, must contain: user, passwd, ashost, sysnr, client
    func_name : str
        name of the function that you want to verify
        
    Returns
    -------
    funct_desc : pyrfc.pyrfc.FunctionDescription
        RFC functional description object
    '''
    print(f'{time.ctime()}, Start getting function description from RFC')
    print(f'{time.ctime()}, Start SAP connection')
    # create connection with SAP based on data inside the dict
    with Connection(**dict_sap_con) as conn:
        print(f'{time.ctime()}, SAP connection stablished')
        # get data from the desired RFC function
        funct_desc = conn.get_function_description(func_name)
        # display the information about the RFC to user
        # display(funct_desc.parameters[0],funct_desc.parameters[0]['type_description'].fields)
        # return it as a variable
        return funct_desc
    # how the whole command is inside the 'with' when it ends the connection with SAP is closed
    # print(f'{time.ctime()}, SAP connection closed')
    # print(f'{time.ctime()}, End getting function description from RFC')


def df_to_sap_rfc(df, dict_sap_con, func_name, rfc_table):
    '''ingest data that is in a data frame in SAP using a defined RFC, checking if the dataframe has 
    the same size, column names and data types
    
    Parameters
    ----------
    df : pandas.DataFrame
        dataframe that is going to be used to insert data to SAP
    dict_sap_con : dict
        dictionary with SAP logon credentials (user, passwd, ashost, sysnr, client)
    func_name : string
        name of the RFC function
    rfc_table : string
        name of the rfc table you are going to populate
        
    Returns
    -------
    None
    '''
    pass
    # # get needed parameters from RFC
    # lst_param = get_rfc_parameters(dict_sap_con, func_name)
    # # check dataframe input
    # check_input_format(df, lst_param)
    # # insert data
    # lst_res = insert_df_in_sap_rfc(
    #     df, dict_sap_con, func_name, rfc_table)

def insert_df_in_sap_rfc(df, dict_sap_con, func_name, rfc_table):
    '''Ingest data that is in a data frame in SAP using a defined RFC
    
    Parameters
    ----------
    df : pandas.DataFrame
        dataframe that is going to be used to insert data to SAP
    dict_sap_con : dict
        dictionary with SAP logon credentials (user, passwd, ashost, sysnr, client)
    func_name : string
        name of the function that you want to remotelly call
    rfc_table : string
        name of the table which your RFC populates
        
    Returns
    -------
    lst_res : list
        list of dictionaries with field names and data types used in RFC
    '''
    print(f'{time.ctime()}, Start data ingestion to SAP process')
    # create an empty list that is going to recive the result
    lst_res = []
    # get the quantity of rows of the dataframe
    rows_qty = len(df)
    # define the number of execution, getting the entire part of the division and 
    # adding 1 to it, to execute the last rows that don't achieve the quantity of 
    # an extra execution
    iter_qty = (rows_qty // c.rows_per_exec) + 1
    print(f'{time.ctime()}, Start SAP connection')
    # create connection with SAP based on data inside the dict
    with Connection(**dict_sap_con) as conn:
        print(f'{time.ctime()}, SAP connection stablished')
        # for each iteration
        for i in range(iter_qty):
            # define the first and last row for this execution
            f_r = i*c.rows_per_exec
            l_r = min((i+1)*c.rows_per_exec, rows_qty)
            # define an auxiliar dataframe with only the rows of this iteration
            df_aux = df.iloc[f_r:l_r]
            print(f'{time.ctime()}, Rows defined')
            # convert this dataframe to a json format, oriented by records
            # this is the needed format to do a multirow input with a RFC
            # by last all the json data must be inside of a list
            lst_dicts_rows = eval(df_aux.to_json(orient='records'))
            # once we have the desired rows well formatted we must tell for
            # which table we are going to insert it
            dict_insert = {rfc_table: lst_dicts_rows}
            print(f'{time.ctime()}, RFC input format applied')
            print(f'{time.ctime()}, Start sending rows {f_r} to {l_r-1}')
            # with everything set just call the RFC by its name 
            # and pass the connection dict
            try:
                result = conn.call(func_name, **dict_insert)
                exec_ind = True
            except:
                result = None
                exec_ind = False
            print(f'{time.ctime()}, Rows {f_r} to {l_r-1} sent')
            # save the row's numbers, execution indicator and the result of the call in the list
            # as a dict
            lst_res.append({'row':f'{f_r}_{l_r-1}', 'exec_ind':exec_ind, 'rfc_result':result})
    # how the whole command is inside the 'with' when it ends the connection with SAP is closed
    print(f'{time.ctime()}, SAP connection closed')
    print(f'{time.ctime()}, End data ingestion to SAP process')
    return lst_res
