import numpy as np
import pandas as pd
import random
import database_connection
import data_functions as load
import os
import git


def guarantee_0_1_trader_query():
    conn = database_connection.connection(database_connection.tfe_gms_db)
    cur = conn.cursor()
    cur.execute("SELECT MAX(sid) FROM dms.trader")
    n = 1
    row = cur.fetchone()
    if row is not None:
        max_sid = int(row[0])
        print('max sid number: ', max_sid)
    else:
        print("No rows returned from query")
    grn_type_0, grn_type_1 = np.array([], dtype=str), np.array([], dtype=str) #lister af grn oprettes

    for name_of_new_company, cvr_of_new_company in load.list_new_companies():
        cvr_of_new_company = load.make_CVR_EORI(cvr_of_new_company)
        print("\nCompany: ", name_of_new_company, ". CVR: ", cvr_of_new_company)
        cur.execute(f'''
        insert into trader    (sid, tin     , referenced,                 name, street_and_number, country_cl, post_code, city)
        values		          ({max_sid + n}, '{cvr_of_new_company}',          '0', '{name_of_new_company}', '', 'DK', '', '');''')

        grn_type_0 = execute_guarantee(0, max_sid+n, grn_type_0, cvr_of_new_company, name_of_new_company, cur)
        grn_type_1 = execute_guarantee(1, max_sid+n, grn_type_1, cvr_of_new_company, name_of_new_company, cur)
        n = n + 1


    update_excel(grn_type_0, os.getcwd() + "\data\Firma garantier til fletning med breve.xlsx", 'Sheet1','Type 0 GRN')
    update_excel(grn_type_1, os.getcwd() + "\data\Firma garantier til fletning med breve.xlsx", 'Sheet1','Type 1 GRN')
    push = input("Is the querry satisfactory? press y to commit: ")
    if push == "y":
        conn.commit()
        print("Commit created")
    else:
        print("No commit created")

def execute_guarantee(guarantee_type, trader_sid, grn_list, cvr_of_new_company, name_of_new_company, cur):
    while True:
        num = generate_random_grn()
        try:
            cur.execute(f'''insert into guarantee (grn     , type_cl, customs_office_cl, trader_sid   , status_cl, acceptance_dt, reference_amount, reference_amount_pct_cl,  access_code, monitor_type_cl, no_of_certificates, "version")
                            values		          ('{num}' , {guarantee_type} , 'DK005600'       , {trader_sid},'VALID'   , '2023-01-01' , 1000000         , 3                      , 1234        ,               3, 1                 , 0);''')
            print("sid: ", trader_sid, ". GRN type 1: ", num)
            grn_list = np.append(grn_list, num)
            break
        except:
            pass
    cur.execute(f'''insert into guarantor (grn    ,   tin                 , referenced,  name, country_cl, post_code, city, contact_person, phone, email, street_and_number)
                                          values                ('{num}', '{cvr_of_new_company}', false     , '{name_of_new_company}', 'DK'     , '1000'   , 'KBH', 'contact person', '12345678', 'mail', 'street 1');''')
    return grn_list


def generate_type_2(trader_sid, cvr, name, cur):
    num = generate_random_grn()
    cur.execute(f'''insert into guarantee (grn     , type_cl, customs_office_cl, trader_sid   , status_cl, acceptance_dt, reference_amount, guarantee_amount, currency_cl,  access_code, departure_customs_office_cl, departure_customs_office_cl, monitor_type_cl, no_of_certificates, "version")
                                values	  ('{num}' , 2      , 'DK005600'       , {trader_sid} ,'VALID'   , '2023-01-01' , 1000000         ,1000000          ,DKK         , 1234        , DK005600                   , DK03862                    ,2               , 1                 , 0);''')
    print("sid: ", trader_sid, ". GRN type 1: ", num)



def generate_random_grn() -> str:
    # Generate a random integer between 0 and 9999999 (inclusive)
    random_number = random.randint(0, 9999999)

    # Convert the integer to a 7-digit string with leading zeroes
    random_string = str(random_number).zfill(7)

    # Append the string to "22DK005600"
    result = "22DK005600" + random_string

    return result

def update_excel(array, excel_file_path, sheet_name, column_name):
    # Load the Excel file into a Pandas DataFrame
    df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
    df_test = df[column_name].dropna().values
    new_column_0 = np.concatenate((df_test, array), axis=None)
    new_column_0_pd = pd.Series(new_column_0)
    # Append the array to the end of the specified column
    df[column_name] = new_column_0_pd
    for cell, n in zip(df['EORI number'], range(len(df['EORI number']))):
        cell = int_to_string(cell)
        df.loc[n, 'EORI number'] = load.make_CVR_EORI(cell)
    # Save the updated DataFrame to the Excel file
    df['Master Access Code'].fillna(1234, inplace=True)
    with pd.ExcelWriter(excel_file_path) as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

def int_to_string(value):
    if isinstance(value, int):
        return str(value)
    else:
        return value

if __name__ == "__main__":
    guarantee_0_1_trader_query()