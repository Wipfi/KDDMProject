import pandas as pd
import os

input_file = "paul_wip/Undergrad.csv"
output_file = "paul_wip/Undergrad_filtered.csv"
required_features = ["Year", "State", "Length", "Value", "Type_1", "Type_2", "Expense_1", "Expense_2"]


def replace_missing_years(df):    
    for i in range(len(df["Year"])):        
        if df["Year"][i] == 9999.0:
            prev_year = find_previous_valid_year(df, i)
            next_year = find_next_valid_year(df, i, len(df))
            if prev_year is not None and next_year is not None and prev_year == next_year:
                df.loc[i, "Year"] = next_year
            else:
                # fix one value is between 2 years 2017 and 2018, set this to 2017 because other features looks good
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

# read csv
print(os.getcwd())
df = pd.read_csv(input_file)
print("----CSV-RAW-----")
print(df.info())

#replace 9999 if prev and next year are the same year, seems like an input error
df = replace_missing_years(df)

# replace abbreviations with whole names
df["State"] = df["State"].apply(replace_state_values)

#make feature length numeric
df["Length"] = df["Length"].str.replace("-year", "").astype(float)

#replace wrong input values
df["Value"] = df["Value"].replace(9999999.0, pd.NA)

df.loc[(df['Expense_1'].isnull()) & (df['Expense_2'] == 'Tuition'), 'Expense_1'] = 'Fees'
df.loc[(df['Expense_1'].isnull()) & (df['Expense_2'] == 'Board'), 'Expense_1'] = 'Room'

#calculate mean In-State
in_private_mean = df.loc[(df['Type_2'] == 'In-State') & (df['Type_1'] == 'Private'), 'Value'].mean(skipna=True)
out_private_mean = df.loc[(df['Type_2'] == 'Out-of-State') & (df['Type_1'] == 'Private'), 'Value'].mean(skipna=True)
in_public_mean = df.loc[(df['Type_2'] == 'In-State') & (df['Type_1'] == 'Public'), 'Value'].mean(skipna=True)
out_public_mean = df.loc[(df['Type_2'] == 'Out-of-State') & (df['Type_1'] == 'Public'), 'Value'].mean(skipna=True)

#private does not distinguish between in state and out state!
print(in_private_mean)
print(out_private_mean)
print(in_public_mean)
print(out_public_mean)


for index, row in df.iterrows():
        value = row['Value']        
        
        if pd.isnull(value):
            type_1 = row['Type_1']
            type_2 = row['Type_2']
            if type_1 == "Private" and type_2 == "In-State":
                    df.at[index, 'Value'] = in_private_mean
            elif type_1 == "Private" and type_2 == "Out-of-State":
                    df.at[index, 'Value'] = out_private_mean
            elif type_1 == "Public" and type_2 == "In-State":
                df.at[index, 'Value'] = in_public_mean
            elif type_1 == "Public" and type_2 == "Out-of-State":
                    df.at[index, 'Value'] = out_public_mean
                  
             

df = df.dropna(subset=required_features, how='all')

# save filtered csv
df.to_csv(output_file, index=False)

print("----CSV-Filtered-----")
print(df.info())
for feature in df.columns:
    unique_values = df[feature].unique()
    unique_counts = df[feature].value_counts()
    print("Feature:", feature)
    print("Unique Values:")
    print(unique_values)
    print("Value Counts:")
    print(unique_counts)
    