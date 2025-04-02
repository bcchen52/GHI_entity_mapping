import pandas as pd
import math

def createCleanModel(input, output, year):
    model = []
    #I want Country, Pop, DALY, Year, Strain, avail_drug_list, avail_drug_col_list, drug_mapping, prevalence, for each drug, efficacy, for each drug, impact, total impact.
    #impact = (DALYS * efficacy * coverage) / 1 - (efficacy*coverage)
    df = pd.read_csv(input)

    impact_diseases = {74: "LF", 75:"LF",
    76: "Schist", 
    77: "Whipworm", 
    78: "Whipworm", 
    79: "Whipworm", 
    80: "Hookworm", 
    81: "Hookworm", 
    82: "Roundworm", 
    83: "Roundworm", 
    84: "Roundworm", 
    85: "Onch", 
    }

    #manual from company tab in spreadsheet

    drug_name = {
        "PZQ" : "Praziquantel",
        "DEC" : "Diethylcarbamazine",
        "ALB" : "Albendazole",
        "IVM" : "Ivermectin",
        "MBD" : "Mebendazole",
    }

    company_name = {
        "PZQ" : "Bayer Healthcare",
        "DEC" : "Pfizer",
        "ALB" : "GlaxoSmithKline",
        "IVM" : "Merck",
        "MBD" : "Johnson and Johnson",
    }
    
    #starts at row 2, ends 219
    for i in range(2, 219):
        
        
        #74 to 85 impact
        disease_and_drugs = {"LF": [], "Schist": [], "Whipworm": [], "Hookworm": [], "Roundworm": [], "Onch": []}

        for k in range(74, 85):
            if pd.notna(df.iloc[i,k]) and float(df.iloc[i,k].replace(",","")) > 0:
                #print(df.iloc[i,0] + " has "+ df.iloc[0,k] + " for " + impact_diseases[k])
                #temp_row['disease'] = impact_diseases[k]
                #temp_row['year'] = '2015'
                #temp_row['country'] = df.iloc[i,0]
                disease_and_drugs[impact_diseases[k]].append(k)

        for k in disease_and_drugs.keys():
            if len(disease_and_drugs[k]) > 0:
                for j in disease_and_drugs[k]:
                    temp_row = {}
                    temp_row['disease'] = k
                    temp_row['state'] = k
                    temp_row['regimen_weight'] = 1/len(disease_and_drugs[k])

                    drugs = df.iloc[0,j].split("+")
                    drug_str = ""
                    for w in range(0, len(drugs)):
                        drug_str += drug_name[drugs[w]]
                        if w < len(drugs) - 1:
                            drug_str += " + "
                    temp_row['drug'] = drug_str

                    comp_str = ""
                    for w in range(0, len(drugs)):
                        comp_str += company_name[drugs[w]]
                        if w < len(drugs) - 1:
                            comp_str += " + "
                    temp_row['company'] = comp_str

                    temp_row['year'] = year
                    temp_row['country'] = df.iloc[i,0]
                    temp_row['group1'] = ""
                    temp_row['group2'] = ""
                    temp_row['group3'] = ""
                    temp_row['drug_weight'] = 1
                    #print(impact_diseases[j])
                    temp_row['regimen'] = df.iloc[0,j]
                    temp_row['drug_impact'] = round(float(df.iloc[i,j].replace(",","")), 3)
                    model.append(temp_row)

    e_map = pd.DataFrame(model)
    e_map.to_csv(output, columns=['disease', 'year', 'country', 'state', 'regimen', 'drug', 'company', 'group1', 'group2', 'group3', 'drug_weight', 'regimen_weight', 'drug_impact'], index=False)

        #model.append[temp_row]

        #e_map.to_csv(output, columns=['disease', 'year', 'country', 'state', 'regimen', 'drug', 'company', 'group1', 'group2', 'group3', 'drug_weight', 'regimen_weight', 'drug_impact'], index=False)

createCleanModel("raw_models/NTD_model_2015.csv", "finished_maps/NTD_entity_map_2015.csv", 2015)
createCleanModel("raw_models/NTD_model_2017.csv", "finished_maps/NTD_entity_map_2017.csv", 2017)
