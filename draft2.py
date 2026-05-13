import requests
import pandas as pd
import json
import copy


"""  
========== Preparation =========== 
url = "https://api.sgu.se/oppnadata/mineralrattigheter/ogc/features/v1/collections"

response=requests.get(url)

# ---- successful? ---
print(response.status_code)
print(response.headers.get("Content-Type"))

if response.status_code == 200:
    print("Good to go!")

    data = response.json()

else:
    print("Problem!") 

"""

""" 
# --- Before doing anything, let's check the structure ---
# Transforms "data" into a str in JSON format
print(json.dumps(data, indent=2))

# note: no ID as INT but a str
"""

""" 
# --- Confirming IDs and titles as per above ---
# :40 does that the ID column has always up to 40 characters
for coll in data["collections"]:
    print(f"{coll['id']:40}  {coll['title']}")
"""


"""
========== The chosen collection ============

Since I chose the collection, I commented all the above preparation
"""

collection = "ut-metaller-industrimineral-beviljade"   
url = f"https://api.sgu.se/oppnadata/mineralrattigheter/ogc/features/v1/collections/{collection}/items"

query = {
    "limit": 827,
    "f": "json"    
}

response=requests.get(url, params=query, verify=False)

# ---- successful? ---
print(response.status_code)

if response.status_code == 200:
    print("OK!")

else:
    print("Problem!") 


# --- The raw data --- 
print("----- Raw data -----")
raw_data = response.json()
#print(f"{raw_data}")  *** uncomment to print data



# --- Backup ---
raw_data_backup = copy.deepcopy(raw_data)


# --- Creating Df, access to data ---
print("------ DataFrame -----")
df = pd.json_normalize(raw_data["features"])
#print(f"{df}") *** uncomment to see df

# --- Removing columns for simplicity ---
print("----- All columns ------")
print(f"{df.keys()}")

print("----- Removed columns -----")
removed_columns = ["type","geometry_name","geometry.type", "geometry.coordinates","properties.diarynr","properties.status",
"properties.export_date", "properties.geom_area", "properties.geom_length"]
print(removed_columns)

df_col_ok = df.drop(columns=removed_columns)
print("----- Kept columns ------")
print(f"Kept columns ({len(df_col_ok.columns)}): {list(df_col_ok.columns)}")



'''
========== Exploratory Data Analysis (EDA) ==========
'''

# --- Missing values ---
print("----- Missing values -----")
print(f"{df_col_ok.isna().sum()}")


# --- Questions ----
print("----- Counties with the most approvals -----")
print(df_col_ok["properties.county"].value_counts().head(10))


# --- The 1rst minerals ---
print("----- Top 5 -----")
print(df_col_ok["properties.mineral"].value_counts().head())

# --- Mineral count ---
print("----- Minerals count ----")
mineral_count = (
    df_col_ok["properties.mineral"]
    .str.split(",")     # str becomes a list as ["gold", "silver", etc..]
    .explode()          # separates in different rows --> 1 mineral per row
    .str.strip()        # remove white spaces
    .value_counts()     # count each mineral
)
print(mineral_count.head(13))


# --- Date conversion ---
date_cols = ["properties.appl_date", "properties.dec_date", "properties.validfrom", "properties.validto"]
df_col_ok[date_cols] = df_col_ok[date_cols].apply(pd.to_datetime)


# --- Permitting length  ---

# --- From application to decision ---
print("----- Application → decision (years) -----")
df_col_ok["appl_to_dec"] = (df_col_ok["properties.dec_date"] - df_col_ok["properties.appl_date"]).dt.days / 365.25
print(df_col_ok["appl_to_dec"].describe().round(2))

# --- Permit duration (from to to) & stats ---
print("----- Permit duration (years) -----")
df_col_ok["permit_duration"] = (df_col_ok["properties.validto"] - df_col_ok["properties.validfrom"]).dt.days / 365.25
print(df_col_ok["permit_duration"].describe().round(2))


# --- Permit duration by county ---
print("----- Avg permit duration by county (years) -----")
print(df_col_ok.groupby("properties.county")["permit_duration"].mean().round(2).sort_values(ascending=False))


# --- Counties Vs Minerals ---
print("----- Minerals by county -----")
mineral_by_county = (
    df_col_ok[["properties.mineral", "properties.county"]]
    .assign(mineral=df_col_ok["properties.mineral"].str.split(", "))
    .explode("mineral")
    .assign(mineral=lambda x: x["mineral"].str.strip())
    .groupby(["properties.county", "mineral"])
    .size()
    .reset_index(name="count")
    .sort_values("count", ascending=False)
)
print(mineral_by_county.head(20))

