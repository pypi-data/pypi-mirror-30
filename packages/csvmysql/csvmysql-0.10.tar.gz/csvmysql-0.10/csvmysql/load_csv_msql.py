import pymysql
import pandas as pd
import numpy as np


# this method convert the encoding for an input list
def generate_insert_values(input_list):

    for index, element in enumerate(input_list):
        #the element could be float, int, or str. date is converted into str

        #for float, check np.nan, and convert nan to None
        if isinstance(element, float):

            if np.isnan(element):
                input_list[index]=None

    return input_list

#load_table_encoding() take care of NaN issues of pandas, so we don't have to update by column after inserting all the data into database table
def load_table_encoding(host, port, user, passwrod, database, insert_statement, pd_dataset):
    cnn = pymysql.connect(host=host, port=port, user=user,
                          passwd=passwrod, db=database, charset='utf8')

    cur = cnn.cursor()

    # insert into database
    rows = pd_dataset.values.tolist()

    for index, row in enumerate(rows):

        rows[index]=generate_insert_values(row)

    cur.executemany(insert_statement, rows)
    cnn.commit()

    cur.close()
    cnn.close()

    return

def drop_table(table_name, host, port, user, password, database):
    cnn=pymysql.connect(host=host,port=port, user=user, passwd=password, db=database)

    cur=cnn.cursor()

    statement='''drop table if exists '''+table_name

    cur.execute(statement)

    cur.close()
    cnn.close()

    return

def delete_data_from_table(table_name, host,port, user, password, database):
    cnn=pymysql.connect(host=host,port=port, user=user, passwd=password, db=database)

    cur=cnn.cursor()

    statement='''delete from '''+table_name+';'+'commit;'

    cur.execute(statement)

    cur.close()
    cnn.close()

    return



#create new table in database from csv file
#version 1, only support int, double, and varchar types
def create_table_generic(table_name, table_data, host,port, user, password, database):
    cnn=pymysql.connect(host=host,port=port, user=user, passwd=password, db=database)

    cur=cnn.cursor()

    df=table_data

    file_name=table_name

    field_names=df.dtypes.index
    field_types=df.dtypes.values
    field_number=len(df.dtypes)


    statement_prefix='''
    create table if not exists 
    ''' + file_name + '''( SYSTEM_ID int NOT NULL AUTO_INCREMENT UNIQUE, '''

    statement_middle=''

    for index in range(0, field_number):

        attr_name='`'+field_names[index]+'`'

        if field_types[index] == 'int64':

            statement_middle=statement_middle+attr_name+' int,'

        elif field_types[index] == 'object':
            max_length_column=max(df[df.columns[index]].fillna('0').str.len())
            if max_length_column <= 255:
                print (field_names[index], max_length_column)
                statement_middle=statement_middle+attr_name+' varchar(255),'
            else:
                print (field_names[index], max_length_column)
                statement_middle = statement_middle + attr_name + ' TEXT,'
        else:

            statement_middle=statement_middle+attr_name+' double,'

    statement_suffix='''
    primary key(SYSTEM_ID))
    '''

    statement_full=statement_prefix+statement_middle+statement_suffix

    cur.execute(statement_full)

    cur.close()
    cnn.close()

    return

def import_data(table_name, table_data, host, port, user, password, database):

    print ('loading the data...')

    df=table_data

    field_names=df.dtypes.index
    # field_types=df.dtypes.values
    field_number=len(df.dtypes)

    statement_prefix='''insert into '''+ table_name +''' ('''

    statement_middle_1=''

    for index in range(0,field_number):
        statement_middle_1=statement_middle_1+ '`' + field_names[index] + '`'+','

    #get rid of the last ','
    statement_middle_1=statement_middle_1[:-1]

    statement_middle_2=''') value ('''

    statement_middle_3=''

    for index in range(0, field_number):
        statement_middle_3=statement_middle_3+'%s,'

    statement_middle_3=statement_middle_3[:-1]

    statement_suffix=''')'''

    insert_statement=statement_prefix+statement_middle_1+statement_middle_2+statement_middle_3+statement_suffix

    print (insert_statement)

    load_table_encoding(host, port, user, password, database, insert_statement, df)

    print ('data is successfully loaded')

    return



def load_into_mysql_dataframe(table_name, df, target_db, host, port, user, password):

    drop_table(table_name, host, port, user, password, target_db)

    create_table_generic(table_name, df, host, port, user, password, target_db)

    import_data(table_name, df, host, port, user, password, target_db)

    return
