# GHI Entity Mapping

This repo is used to create cleaned relational models and entity maps for disease treatment regimens in different regions, given disease (Trachoma, Malaria, HepC, NTDs, TB, HIV) models with basic demographic, treatment regimen, and impact information. These models and entity maps are used for GHI's forecasting tool.

To do this, we run {disease}_map.py, which takes raw_models/{disease}_model_{year}.csv and creates cleaned_models/{disease}_cleaned_model_{year}.csv and finished_maps/{disease}_entity_map_{year}.csv. We assume that each disease has a unique structure (columns, rows, etc) that is followed for each year's model.

Sometimes, models are incomplete, and we manually need to patch that information, and those programs can be found in helper/. 

## Files

### cleaned_models/

hold the disease regimen to country relational models

### entity_maps/
 hold the finish entity maps

### helper/
For example, original NTD models are missing Schist efficacy data, or, more specifically, PZQ efficacy data. Inside helper/, schist_eff.py opens helper/eff_data/schist_eff.csv, and parses through the available PZQ efficacy data by country, using the first instance of efficacy data for each country, and taking averages for each region. Then, the raw_models/NTD_model_{year}.csv files are opened and each country will be assigned their average efficacy, if available, else, will use their WHO regions average. Additionally, the impact score for PZQ in the original file is also missing, as that depends on missing data. Thus, we recalculate the impact score of PZQ using this new data.


This looks through a spreadsheet of studies for different countries of different sample sizes, and we look at the egg reduction rate, as that is the standard the WHO uses.

CHANGE finished_maps into entity_maps

change schist_eff rel links