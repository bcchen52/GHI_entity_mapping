import pandas as pd
import math
from helper.drug_info import get_drug_info
import sys

def createCleanModelandMap(input, out_model, out_map, year):
    e_map = []
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

    #loop through an area to get all available/possible drug regimens used
    drugs = set()
    drugs_alt_name = {}
    impact_headers = {}
    
    #we run into a unique problem with NTDs where the same regimens will be used for different diseases
    #this is an issue because the cleaned model will list the efficacy and impact for every regimen, with a 0 for irrelevant categories
    #in reality, only the relevant regimen is used, and we also cannot have multiple of the same data in our columns headers
    #so, to resolve both these issues, we can use disease specific regimen data, so no relevant information is lost
    disease_to_impact_col = {
        "LF": {"DEC+ALB": 74, "IVM+ALB": 75},
        "Schist": {"PZQ": 76},
        "Whipworm": {"IVM+ALB": 79, "ALB": 77, "MBD": 78},
        "Hookworm": {"ALB": 80, "MBD": 81},
        "Roundworm": {"IVM+ALB": 84, "ALB": 82, "MBD": 83},
        "Onch": {'IVM': 85},
    }

    disease_to_efficacy_col = {
        "LF": {"DEC+ALB": 42, "IVM+ALB": 44, "PZQ": 46, "ALB": 48, "MBD": 50, 'IVM': 64},
        "Schist": {"DEC+ALB": 42, "IVM+ALB": 44, "PZQ": 46, "ALB": 48, "MBD": 50, 'IVM': 64},
        "Whipworm": {"DEC+ALB": 42, "IVM+ALB": 52, "PZQ": 46, "ALB": 48, "MBD": 50, 'IVM': 64},
        "Hookworm": {"DEC+ALB": 42, "IVM+ALB": 44, "PZQ": 46, "ALB": 54, "MBD": 56, 'IVM': 64},
        "Roundworm": {"DEC+ALB": 42, "IVM+ALB": 62, "PZQ": 46, "ALB": 58, "MBD": 60, 'IVM': 64},
        "Onch": {"DEC+ALB": 42, "IVM+ALB": 44, "PZQ": 46, "ALB": 48, "MBD": 50, 'IVM': 64},
    }

    ordered_treatments = ["DEC+ALB", "IVM+ALB", "PZQ", "ALB", "MBD", "IVM"]

    disease_to_DALY_col = {
        "LF": 3,
        "Schist": 4,
        "Whipworm": 7,
        "Hookworm": 10,
        "Roundworm": 13,
        "Onch": 14,
    }

    #need to fix this
    disease_to_prev_col = {
        "LF": 29,
        "Schist": 30,
        "Whipworm": 33,
        "Hookworm": 35,
        "Roundworm": 37,
        "Onch": 38,
    }

    #for worms use STH and SAC data

    disease_to_cov_col = {
        "LF": 18,
        "Schist": 20,
        "Whipworm": 24,
        "Hookworm": 24,
        "Roundworm": 24,
        "Onch": 28,
    }

    for i in range(74, 86):
        drug = df.iloc[0, i]
        if drug not in drugs:
            drugs.add(drug)
            alt_name = drug
            if "+" in drug:
                alt_name = drug.replace("+", "_")
            drugs_alt_name[drug] = alt_name
            impact_headers[drug] = f"Impact_{drugs_alt_name[drug]}"
    
    drug_name = get_drug_info(drugs, 0)
    company_name = get_drug_info(drugs, 1)
    
    #starts at row 2, ends 219
    for i in range(2, 219):
        #each country
        #42, 44, 46, 48, 50, 52, 54, 56, 58, 60, 62, 64 ONCH
        #74 to 85 impact
        disease_and_drugs = {"LF": [], "Schist": [], "Whipworm": [], "Hookworm": [], "Roundworm": [], "Onch": []}

        for k in range(74, 86):
            if pd.notna(df.iloc[i,k]) and float(df.iloc[i,k].replace(",","")) > 0:
                #print(df.iloc[i,0] + " has "+ df.iloc[0,k] + " for " + impact_diseases[k])
                #temp_row['disease'] = impact_diseases[k]
                #temp_row['year'] = '2015'
                #temp_row['country'] = df.iloc[i,0]
                disease_and_drugs[impact_diseases[k]].append(k)

        #i need efficacy, and impact

        for k in disease_and_drugs.keys():
            #each disease, this is each cleaned model line
            temp_model_row = {}
            temp_model_row["Country"] = df.iloc[i,0]
            population = 0
            if pd.notna(df.iloc[i,2]):
                population = str(df.iloc[i,2]).replace(",", "")
            temp_model_row["Population"] = population
            temp_model_row["Year"] = year
            temp_model_row["DALY"] = df.iloc[i, disease_to_DALY_col[k]]
            temp_model_row["strain"] = k

            prev = df.iloc[i, disease_to_prev_col[k]]
            if "%" in str(prev):
                prev = float(str(prev)[:-1])/100
            temp_model_row["strain_prevalence"] = prev

            temp_model_row["strain_pct"] = 1

            treat_cov = df.iloc[i, disease_to_cov_col[k]]
            if "%" in str(treat_cov):
                treat_cov = float(str(treat_cov)[:-1])/100
            temp_model_row["strain_treat_covg_pct"] = treat_cov

            avail_drug_list = []
            avail_drug_col_list = []
            drug_mapping = {}
            total_impact = 0
           
            #temp_model_row
            #we need efficacy data for everything
            for j in drugs:
                temp_model_row[impact_headers[j]] = 0
                efficacy = round(float(df.iloc[i, disease_to_efficacy_col[k][j]][:-1])/100, 5)
                if efficacy == 1:
                    efficacy = 0.9999
                temp_model_row[drugs_alt_name[j]] = efficacy
                if j in disease_to_impact_col[k] and pd.notna(df.iloc[i, disease_to_impact_col[k][j]]):
                    impact = df.iloc[i, disease_to_impact_col[k][j]].replace(",", "")
                    temp_model_row[impact_headers[j]] = round(float(impact), 5)
            #IVM unique to ONCH
            #ALB, MDB shared by worms
            #IVM+ALB shared by LF, whip, round
            if len(disease_and_drugs[k]) > 0:
                #each regimen
                for j in disease_and_drugs[k]:
                    temp_row = {}
                    temp_row['disease'] = k
                    temp_row['state'] = k
                    temp_row['regimen_weight'] = 1/len(disease_and_drugs[k])

                    temp_row['drug'] = drug_name[df.iloc[0,j]]

                    temp_row['company'] = company_name[df.iloc[0,j]]

                    temp_row['year'] = year
                    temp_row['country'] = df.iloc[i,0]
                    temp_row['group1'] = ""
                    temp_row['group2'] = ""
                    temp_row['group3'] = ""
                    temp_row['drug_weight'] = 1
                    #print(impact_diseases[j])
                    regimen = df.iloc[0,j]
                    temp_row['regimen'] = regimen
                    temp_row['drug_impact'] = round(float(df.iloc[i,j].replace(",","")), 3)
                    total_impact += temp_row['drug_impact'] 
                    e_map.append(temp_row)
                    avail_drug_list.append(regimen)
                    avail_drug_col_list.append(drugs_alt_name[regimen])

                    #drug mapping is in a different format
                    cleaned_regimen = regimen.replace("+", " + ")
                    drug_mapping[drugs_alt_name[regimen]] = cleaned_regimen

            temp_model_row["avail_drug_list"] = avail_drug_list
            temp_model_row["avail_drug_col_list"] = avail_drug_col_list
            temp_model_row["drug_mapping"] = drug_mapping
            temp_model_row["Total_impact"] = total_impact

            model.append(temp_model_row)

    entity_map = pd.DataFrame(e_map)
    entity_map.to_csv(out_map, columns=['disease', 'year', 'country', 'state', 'regimen', 'drug', 'company', 'group1', 'group2', 'group3', 'drug_weight', 'regimen_weight', 'drug_impact'], index=False)
    cleaned_model = pd.DataFrame(model)
    cleaned_model.to_csv(out_model, columns=['Country', 'Population', 'DALY', 'Year', 'strain', 'avail_drug_list', 'avail_drug_col_list', 'drug_mapping', 'strain_prevalence', 'strain_pct', 'strain_treat_covg_pct', drugs_alt_name[ordered_treatments[0]], drugs_alt_name[ordered_treatments[1]], drugs_alt_name[ordered_treatments[2]], drugs_alt_name[ordered_treatments[3]], drugs_alt_name[ordered_treatments[4]], drugs_alt_name[ordered_treatments[5]], impact_headers[ordered_treatments[0]], impact_headers[ordered_treatments[1]], impact_headers[ordered_treatments[2]], impact_headers[ordered_treatments[3]], impact_headers[ordered_treatments[4]], impact_headers[ordered_treatments[5]], "Total_impact"], index=False)
        #model.append[temp_row]

        #e_map.to_csv(output, columns=['disease', 'year', 'country', 'state', 'regimen', 'drug', 'company', 'group1', 'group2', 'group3', 'drug_weight', 'regimen_weight', 'drug_impact'], index=False)

def main():
    years = [2013, 2015, 2017]
    if len(sys.argv) < 2:
        year = "ALL"
    else:
        year = int(sys.argv[1])

    if year == "ALL":
        for i in years:
            createCleanModelandMap(f"raw_models/NTD_model_{i}.csv", f"cleaned_models/NTD_cleaned_model_{i}.csv", f"entity_maps/NTD_entity_map_{i}.csv", i)
            print(f"{i} created.")
        print("Complete")
        return 0
    elif year in years:
        createCleanModelandMap(f"raw_models/NTD_model_{year}.csv", f"cleaned_models/NTD_cleaned_model_{year}.csv", f"entity_maps/NTD_entity_map_{year}.csv", year)
        print(f"{year} created.")
        print("Complete")
        return 0
    else:
        print("Cannot find year.")
    return 1

if __name__ == "__main__":
    main()