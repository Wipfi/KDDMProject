import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import matplotlib.pyplot as plt

input_file = "Undergrad.csv"
output_file = "Undergrad_filtered.csv"
required_features = ["Year", "State", "Length", "Value", "Type_1", "Type_2", "Expense_1", "Expense_2"]


def replace_missing_years(df):    
    for i in range(len(df["Year"])):        
        if df["Year"][i] == 9999.0:
            prev_year = find_previous_valid_year(df, i)
            next_year = find_next_valid_year(df, i, len(df))
            if prev_year is not None and next_year is not None and prev_year == next_year:
                df.loc[i, "Year"] = next_year
            else:
                # fix one value is between 2 years 2017 and 2018, set this to 2017 because this State is missing 1 value in 2017
                df.loc[i, "Year"] = 2017.0
          
    return df


def find_previous_valid_year(df, index):
    for i in range(index-1, -1, -1):
        if not pd.isnull(df["Year"][i]) and df["Year"][i] != 9999.0:
            return df["Year"][i]
    return None


def find_next_valid_year(df, index, length):
    for i in range(index+1, length):
        if not pd.isnull(df["Year"][i]) and df["Year"][i] != 9999.0:
            return df["Year"][i]
    return None

# function to replace the values in the "State" column
def replace_state_values(state):
    state_mapping = {
        "AR": "Arkansas",
        "SC": "South Carolina",
        "UT": "Utah",
        "VT": "Vermont",
        "WA": "Washington"
    }
    return state_mapping.get(state, state)

def fixValueMean(df):
    years = df['Year'].unique()
    print(years)
    in_private_mean = []
    out_private_mean = []
    in_public_mean = []
    out_public_mean = []
    for year in years:
        #calculate mean In-State
        filtered_year_data = df[df['Year'] == year]
        in_private_mean.append(filtered_year_data.loc[(filtered_year_data['Type_2'] == 'In-State') & (filtered_year_data['Type_1'] == 'Private'), 'Value'].mean(skipna=True))
        out_private_mean.append(filtered_year_data.loc[(filtered_year_data['Type_2'] == 'Out-of-State') & (filtered_year_data['Type_1'] == 'Private'), 'Value'].mean(skipna=True))
        in_public_mean.append(filtered_year_data.loc[(filtered_year_data['Type_2'] == 'In-State') & (filtered_year_data['Type_1'] == 'Public'), 'Value'].mean(skipna=True))
        out_public_mean.append(filtered_year_data.loc[(filtered_year_data['Type_2'] == 'Out-of-State') & (filtered_year_data['Type_1'] == 'Public'), 'Value'].mean(skipna=True))

        #private does not distinguish between in state and out state! 
        #print(in_private_mean[-1])
        #print(out_private_mean[-1])
        #print(in_public_mean[-1])

        #print(out_public_mean[-1])
        
        #checkwhere alabama has a missing year value
        #print("------------------")
        #unique_counts = filtered_year_data['State'].value_counts()
        #print("Feature:", year)
        #print("Value Counts:")
        #print(unique_counts)


    for index, row in df.iterrows():
            value = row['Value']        
            
            if pd.isnull(value):
                type_1 = row['Type_1']
                type_2 = row['Type_2']
                year =  row['Year']
                index_year = np.where(years == year)[0][0]            
                if type_1 == "Private" and type_2 == "In-State":
                        df.at[index, 'Value'] = in_private_mean[index_year]                   
                elif type_1 == "Private" and type_2 == "Out-of-State":
                        df.at[index, 'Value'] = out_private_mean[index_year]                     
                elif type_1 == "Public" and type_2 == "In-State":
                    df.at[index, 'Value'] = in_public_mean[index_year]                  
                elif type_1 == "Public" and type_2 == "Out-of-State":
                        df.at[index, 'Value'] = out_public_mean[index_year]     
     
def fixValueInterpolation(df):
    missing_values_list = []
    missing_values_df = df[df['Value'].isnull()].copy()
    for index, row in missing_values_df.iterrows():
        if pd.isnull(row['Value']):
            filtered_df = 0
            if(missing_values_df.at[index, 'Type_1'] == "Private"):
                filtered_df = df[
                (df['State'] ==  missing_values_df.at[index, 'State']) &
                (df['Length'] ==  missing_values_df.at[index, 'Length']) &
                (df['Expense_1'] ==  missing_values_df.at[index, 'Expense_1']) &
                (df['Expense_2'] ==  missing_values_df.at[index, 'Expense_2'])
                ]
            else:
                filtered_df = df[
                (df['State'] ==  missing_values_df.at[index, 'State']) &
                (df['Length'] ==  missing_values_df.at[index, 'Length']) &
                (df['Type_1'] ==  missing_values_df.at[index, 'Type_1']) &
                (df['Type_2'] ==  missing_values_df.at[index, 'Type_2']) &
                (df['Expense_1'] ==  missing_values_df.at[index, 'Expense_1']) &
                (df['Expense_2'] ==  missing_values_df.at[index, 'Expense_2'])
                ]
                      
            filtered_df_nan =  filtered_df.dropna(subset=['Value'])
            values_array =  filtered_df_nan['Value'].astype(float).values
            years_array = filtered_df_nan['Year'].astype(float).values

            x = np.array(years_array)
            y = np.array(values_array)
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

           
            missing_years = filtered_df[filtered_df['Value'].isna()]['Year'].astype(float).values
            missing_values = slope * missing_years + intercept
            for i in missing_values:
                missing_values_list.append(i)

           
            filtered_df.loc[filtered_df['Value'].isna(), 'Value'] = missing_values

            # create a scatter plot 
            plt.scatter(x, y, label='Valid Points')

            #plot linear function
            x_line = np.linspace(0, 2025, 100)
            y_line = slope * x_line + intercept
            plt.plot(x_line, y_line, color='green', label='Linear Function')
            plt.scatter(missing_years, missing_values, color='red', label='Missing Values')
            plt.xlabel('Year')
            plt.ylabel('Value')
            plt.xlim(2012, 2024)
            plt.ylim(y.min(), y.max())
            plt.title('Linear Function Estimation')
            plt.legend()

            # Show the plot
            #plt.show()
    #fill in missing values        
    for index, row in df.iterrows():
        if pd.isnull(row['Value']):
            df.at[index, 'Value'] = missing_values_list.pop(0)
            

    
    
     
# read csv
print(os.getcwd())
df = pd.read_csv(input_file)
print("----CSV-RAW-----")
print(df.info())

#replace 9999 if prev and next year are the same year, seems like an input error
df = replace_missing_years(df)
df = df.dropna(subset=required_features, how='all')

# replace abbreviations with whole names
df["State"] = df["State"].apply(replace_state_values)

#make feature length numeric
df["Length"] = df["Length"].str.replace("-year", "").astype(float)

#replace wrong input values
df["Value"] = df["Value"].replace(9999999.0, pd.NA)

df.loc[(df['Expense_1'].isnull()) & (df['Expense_2'] == 'Tuition'), 'Expense_1'] = 'Fees'
df.loc[(df['Expense_1'].isnull()) & (df['Expense_2'] == 'Board'), 'Expense_1'] = 'Room'

#fixValueMean(df)
fixValueInterpolation(df)
         
# save filtered csv
df.to_csv(output_file, index=False)

#print("----CSV-Filtered-----")
#print(df.info())
for feature in df.columns:
    unique_values = df[feature].unique()
    unique_counts = df[feature].value_counts()
    print("Feature:", feature)
    print("Unique Values:")
    print(unique_values)
    print("Value Counts:")
    print(unique_counts)
    