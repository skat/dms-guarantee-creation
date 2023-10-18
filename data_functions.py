import numpy as np
import pandas as pd
import math
import os


def list_new_companies():
    filename = os.getcwd() + "\data\Firma garantier til fletning med breve.xlsx"
    data = pd.read_excel(filename)
    names_of_new_companies = np.array([], dtype =str)
    CVR_of_new_companies = np.array([], dtype=str)

    for n in range(data.shape[0]):
        x = data['Master Access Code'][n] #se om den har en master access code
        if math.isnan(x):  # hvis der ikke er nogen master access code
            names_of_new_companies = np.append(names_of_new_companies, data['Firma'][n]) #hvis ikke, gem navnet på firmaet
            CVR_of_new_companies = np.append(CVR_of_new_companies, data['EORI number'][n])
    return zip(names_of_new_companies, CVR_of_new_companies)


def make_CVR_EORI(CVR):  # adds the 'DK' prefix if it's not already there
    if CVR[:2] == "DK":
        return CVR
    else:
        return "DK" + CVR