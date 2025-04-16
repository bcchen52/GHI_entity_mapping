import pandas as pd
import math
import sys

def createCleanModel(input, output, year):
    model = []
    #I want Country, Pop, DALY, Year, Strain, avail_drug_list, avail_drug_col_list, drug_mapping, prevalence, for each drug, efficacy, for each drug, impact, total impact.
    #impact = (DALYS * efficacy * coverage) / 1 - (efficacy*coverage)
    df = pd.read_csv(input)
    
    #starts at row 2, ends 219
    for i in range(2, 219):
        temp_row = {}
        #in the model, you have dont have avail_drug_list and avail_drug_col_list, that's the point of the cleaned model

        #each column is for each strain in each country
        #print(df.iloc[i,3]) #row, DALYS
        temp_row['Country'] = df.iloc[i,0]
        #pop in form x,xxx,xxx
        population = float("".join(str(df.iloc[i,2]).split(",")))
        temp_row['Population'] = population

        daly = float("".join(str(df.iloc[i,5]).split(",")))
        temp_row['DALY'] = daly 
        temp_row['Year'] = year
        #no strains? add col to maintain consistency w Malaria, not important 
        temp_row['strain'] = 'Trachoma'

        #only using one treatment, static, if multiple should loop through and only add if impact nonzero
        temp_row['avail_drug_list'] = ['AZM']
        temp_row['avail_drug_col_list'] = ['AZM']
        temp_row['drug_mapping'] = {'AZM': 'AZM'}
        temp_row['strain_prevalence'] = float("".join(str(df.iloc[i,6]).split(",")))
        temp_row['strain_pct'] = 1

        #coverage in form x.xx%
        cov = float(df.iloc[i,9][0:-1])/100
        temp_row['strain_treat_covg_pct'] = cov

        #if there's multiple treatments, loop through options, give efficacy
        #efficacy in form x.xx%
        eff = float(df.iloc[i,14][0:-1])/100
        temp_row['AZM'] = eff

        #if there's multiple, do same for impact
        #it seems as if impact = 0 when not endemic
        
        #impact for NTDs = (DALYs * coverage * efficacy) / 1 - (coverage*efficacy)
        #this is to test that the impact is correct/matches, because eff and cov are rounded in the .csv
        #impact = int(df.iloc[i,15]) * (daly * cov * eff) / (1 - cov * eff)
        #if you want the exact, use this
        impact = float(df.iloc[i,16])

        temp_row['Impact_AZM'] = impact

        #irl you can loop through ur temp_row but we have impact
        temp_row['Total_impact'] = impact

        model.append(temp_row)

        #again, this is not how u would do it for disease w complex treatment regimens but this is for proof of concept
    cleaned_df = pd.DataFrame(model)
    cleaned_df.to_csv(output, index=False)

def createEntityMap(input, output, year):
    model = []
    df = pd.read_csv(input)

    #i think Pfizer is company?

    for i in range(0, 217):
        temp_row = {}
        #entity map is for each treatment regimen
        #instead of this, we can just use 'AZM'

        if len(df.iloc[i, 5]) > 2:
            temp_row['disease'] = "Trachoma"
            temp_row['year'] = year
            temp_row['country'] = df.iloc[i,0]

            #prob not necessary, but for consistency w malaria why not
            temp_row['state'] = "Trachoma"

            #empty should be "[]"
            regimen_list = df.iloc[i, 5][1:-1].split(", ") #remove "[" and "]", split entries
            #regimen_list is in form XX+XX+... for regimen name
            #regimen_search_list is in form XX_XX which is the same form as col name for impact, Impact_XX_XX_...
            regimen_search_list = df.iloc[i, 6][1:-1].split(", ")
            for k in range(0, len(regimen_search_list)):
                search_name = f"Impact_{regimen_search_list[k][1:-1]}"
                if search_name in df.columns:
                    if df[search_name][i] != 0:
                        temp_row['regimen'] = regimen_list[k][1:-1]
                    
                        #if multiple, map acronym to name
                        temp_row['drug'] = "Azithromycin"

                        #i think this is correct company
                        temp_row['company'] = "Pfizer"

                        #idk what these do, copying malaria entity map
                        temp_row['group1'] = ""
                        temp_row['group2'] = ""
                        temp_row['group3'] = ""

                        #not relevant for this data, all 1
                        temp_row['drug_weight'] = 1
                        temp_row['regimen_weight'] = 1

                        temp_row['drug_impact'] = round(float(str(df[search_name][i]).replace(",","")),3)
                        model.append(temp_row)
                else:
                    print(f"{search_name} doesn't exist")
                    return

    e_map = pd.DataFrame(model)
    e_map.to_csv(output, columns=['disease', 'year', 'country', 'state', 'regimen', 'drug', 'company', 'group1', 'group2', 'group3', 'drug_weight', 'regimen_weight', 'drug_impact'], index=False)

def main():
    years = [2010, 2013, 2015, 2017]
    if len(sys.argv) < 2:
        year = "ALL"
    else:
        year = int(sys.argv[1])

    if year == "ALL":
        for i in years:
            createCleanModel(f"raw_models/trachoma_model_{i}.csv", f"cleaned_models/trachoma_cleaned_model_{i}.csv", i)
            createEntityMap(f"cleaned_models/trachoma_cleaned_model_{i}.csv", f"entity_maps/trachoma_entity_map_{i}.csv", i)
            print(f"{i} created.")
        print("Complete")
        return 0
    elif year in years:
        createCleanModel(f"raw_models/trachoma_model_{year}.csv", f"cleaned_models/trachoma_cleaned_model_{year}.csv", year)
        createEntityMap(f"cleaned_models/trachoma_cleaned_model_{year}.csv", f"entity_maps/trachoma_entity_map_{year}.csv", year)
        print(f"{year} created.")
        print("Complete")
        return 0
    else:
        print("Cannot find year.")
    return 1

if __name__ == "__main__":
    main()
        