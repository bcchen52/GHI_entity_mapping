import pandas as pd
import math
from helper.drug_info import get_drug_info

def createCleanModelandMap(input, out_model, out_map, year):
    e_map = []
    model = []
    #I want Country, Pop, DALY, Year, Strain, avail_drug_list, avail_drug_col_list, drug_mapping, prevalence, for each drug, efficacy, for each drug, impact, total impact.
    #impact = (DALYS * efficacy * coverage) / 1 - (efficacy*coverage)
    df = pd.read_csv(input)

    print(df.iloc[0,148])
    #cols 6 to 12 genotype distribution
    #13, 15, ... 25 is acute DALY
    #14, 16, ... 26 is chronic DALY
    #G1 efficacies 27 to 32(6) acute, 33 to 38(6) chronic
    #G2 eff 39 to 41(3) acute, 42 to 43(2) chronic
    #G3 eff 44 to 46(3) acute, 47 to 48(2) chronic
    #G4 eff 49 to 54(5) acute, 55 to 60(5) chronic
    #G5 eff 61 to 63(3) acute, 64 to 66(3) chronic
    #G6 eff 67 to 69(3) acute, 70 to 72(3) chronic
    #Other eff 73 to 80(8) acute, 81 to 87(7) chronic
    #G1 impact 88-93; 94-99
    #G2 impact 100-102; 103-104
    #G3 impact 105-107; 108-109
    #G4 impact 110-115; 116-121
    #G5 impact 122-124; 125-127
    #G6 impact 128-130; 131-133
    #Other impact 134-141; 142-148

    impact_diseases = {}
    #this is for 2015, we need an offset for 2019 as columns are different
    diseases_impact_col = {
        "G1 Acute": [88,93],
        "G1 Chronic": [94,99],
        "G2 Acute": [100,102],
        "G2 Chronic": [103,104],
        "G3 Acute": [105,107],
        "G3 Chronic": [108,109],
        "G4 Acute": [110,115],
        "G4 Chronic": [116,121],
        "G5 Acute": [122,124],
        "G5 Chronic": [125,127],
        "G6 Acute": [128,130],
        "G6 Chronic": [131,133],
        "Other Acute": [134,141],
        "Other Chronic": [142,148],
    }

    #putting ranges is faster than manually doing each for 50 entries
    for i in diseases_impact_col:
        for k in range(diseases_impact_col[i][0], diseases_impact_col[i][1]+1):
            impact_diseases[k] = i 
    
    print(impact_diseases)

    drugs = set()
    for i in range(27, 87):
        drug = df.iloc[0,i]
        if drug not in drugs:
            drugs.add(drug)
    
    print(drugs)
    drug_name = get_drug_info(drugs, 0)
    company_name = get_drug_info(drugs, 1)

    for i in range(2, 219):

        disease_and_drugs = { "G1 Acute": [], "G1 Chronic": [], "G2 Acute": [], "G2 Chronic": [], "G3 Acute": [], "G3 Chronic": [], "G4 Acute": [], "G4 Chronic": [], "G5 Acute": [], "G5 Chronic": [], "G6 Acute": [], "G6 Chronic": [], "Other Acute": [], "Other Chronic": [],}

        for k in range(88, 148):
            if pd.notna(df.iloc[i,k]) and float(df.iloc[i,k]) > 0:
                disease_and_drugs[impact_diseases[k]].append(k)

        for k in disease_and_drugs:
            if len(disease_and_drugs[k]) > 0:
                for j in disease_and_drugs[k]:
                    temp_row = {}
                    temp_row['disease'] = "HepC"
                    temp_row['state'] = k
                    temp_row['regimen_weight'] = round(1/len(disease_and_drugs[k]), 3)
                    regimen = df.iloc[0,j]
                    if " + " in regimen:
                        regimen = regimen.replace(" + ", "+")
                    temp_row['regimen'] = regimen
                    temp_row['drug'] = drug_name[regimen]
                    temp_row['company'] = company_name[regimen]
                    temp_row['year'] = year
                    temp_row['country'] = df.iloc[i,0]
                    temp_row['group1'] = ""
                    temp_row['group2'] = ""
                    temp_row['group3'] = ""
                    temp_row['drug_weight'] = 1
                    temp_row['drug_impact'] = round(float(df.iloc[i,j].replace(",","")), 3)
                    e_map.append(temp_row)
    
    entity_map = pd.DataFrame(e_map)
    entity_map.to_csv(out_map, columns=['disease', 'year', 'country', 'state', 'regimen', 'drug', 'company', 'group1', 'group2', 'group3', 'drug_weight', 'regimen_weight', 'drug_impact'], index=False)

createCleanModelandMap("raw_models/hepC_model_2015.csv", "cleaned_models/hepC_cleaned_model_2015.csv", "entity_maps/hepC_entity_map_2015.csv", 2015)
#createCleanModelandMap("raw_models/hepC_model_2019.csv", "cleaned_models/hepC_cleaned_model_2019.csv", "entity_maps/hepC_entity_map_2019.csv", 2019)
