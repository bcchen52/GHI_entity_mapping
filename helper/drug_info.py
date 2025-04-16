import pandas as pd
from pathlib import Path
base_dir = Path(__file__).resolve().parent
DRUG = 0
COMPANY = 1
TYPE_TO_ROW = {DRUG: 6, COMPANY: 2}
INPUT = f"{base_dir}/drug_data.csv"

#we are given "X+Y+Z"

def get_drug_info(drugs, TYPE):
    df = pd.read_csv(INPUT)
    #6 is drug name
    d = {}

    for i in drugs:
        name_i = i 
        cleaned_i = i
        if "+" in i:
            #we want {"X+...+Z" : "XNAME + ZNAME"} We need spaces for our company and drug names, but not regimen
            if " + " in i:
                name_i = i.replace(" + ", "+")
            else:
                cleaned_i = i.replace("+", " + ")
        drug = find_drug_from_abbrev(df, cleaned_i, TYPE)
        #this will return the name if i exists in row 6 of the table in the form of "i", "X + ... + i + ... + Y" or "i or j"
        #for example, "PQ" only exists in a combination, such as "AS + PQ"; "INH" exists in "H or INH"; "IVM" exists alone
        if drug:
            d[name_i] = drug
        else:
            #this means that the specific combo i = "X + ... + Z" does not exist, so, we find each individual X, Y, Z
            #for example, "IVM + ALB" only exist individually as "IVM" and "ALB", so we find individual and build company name + drug name combo
            individual = cleaned_i.split(" + ")
            names = set()
            for k in individual:
                names.add(find_drug_from_abbrev(df, k, TYPE))
            #print(individual)
            d[name_i] = (" + ").join((names))
    #print(d)
    return d

def find_drug_from_abbrev(df, abbrev, TYPE):
    columns_matching = df.columns[df.loc[8]==abbrev].tolist()
    if columns_matching:
        #columns_matching will have multiple entries for each disease/regimen combo, with the last being the most recent
        #columns_matching is a list in the form ["unnamed: col1", ..., "unnamed: col2"] where col1 < col2 < ... etc
        #we want the most recent col#, which we get with int((columns_matching[-1].split(' '))[1])
        #then, we use that column and get the TYPE_TO_ROW[TYPE] row for the information that we want
        return str(df.iloc[TYPE_TO_ROW[TYPE], int((columns_matching[-1].split(' '))[1])])
    else:
        #in the case that the entry has "H or INH" or the specific combination of "IVM + ALB" does not exist or the standalone "PQ" does not exist
        columns_matching = df.columns[df.loc[8].str.contains(abbrev, na=False)].tolist()
        #this checks that our disease abbreviation exists somewhere in the table
        if columns_matching:
            if "or" in df.iloc[8, int((columns_matching[-1].split(' '))[1])]:
                #this means disease abbreviation is in the form "H or INH" in the table, and we've found our column
                return str(df.iloc[TYPE_TO_ROW[TYPE], int((columns_matching[-1].split(" "))[1])])
            else:
                #this means that our standalone "X" is EITHER part of a combo "X + ... + Y" or in another abbrev "yXz", such as "PQ" existing in "PPQ"
                found = False
                k = 0
                while not found and k < len(columns_matching):
                    #we only care if X is part of a combo "X + ... + Y" and not some "yXz"
                    #first, an easy way to weed out potential "yXz" is making sure this is a combo of some "X + ... + Y"
                    if " + " in df.iloc[8, int(columns_matching[-(1+k)].split(" ")[1])]:
                        individual = df.iloc[8, int(columns_matching[-(1+k)].split(" ")[1])].split(" + ")
                        #at this point, we can have either "X + ... + Y" or some "yXz + ... + Y", this step ensures that we have "X"
                        if abbrev in individual:
                            found = True
                            if TYPE == DRUG:
                                #there are discrepancies in how drug names are formatted from "X/ Y", "X/Y", "X + Y"
                                #however, order is preserved, so we can use the index of the abbreviation to find the location of drug name
                                index = individual.index(abbrev)
                                #remove white space
                                names = "".join(df.iloc[TYPE_TO_ROW[TYPE], int(columns_matching[-(1+k)].split(" ")[1])].split(" "))
                                name_list = [0] * len(individual)
                                if "/" in names:
                                    name_list = names.split("/")
                                else:
                                    name_list = names.split("+")
                                return name_list[index]
                            
                            #for company name, just take the whole thing, lack of uniformity/order when multiple, so just use entire thing
                            names = df.iloc[TYPE_TO_ROW[TYPE], int(columns_matching[-(1+k)].split(" ")[1])]
                            return names
                    k += 1
                #we might also need a case to handle if "X + ... + Y" is part of a larger "X + ... + Y + ... + Z" but we have not come across that yet
        return None

k = get_drug_info(["AL + PQ", "PQ", "DHA-PPQ + PQ", "AS + MQ"], 0)
k1 = get_drug_info(["AL + PQ", "PQ", "DHA-PPQ + PQ", "AS + MQ"], 1)
#ART-NQ does not exist
#ANY QN don't exist
print(k)
print(k1)