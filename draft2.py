import requests
import pandas as pd
import json
import copy


"""  
# --- preparation ---
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
print(json.dumps(data, indent=2))

# note: no ID as INT but a str
"""



""" 
# Confirming IDs and titles as per above
for coll in data["collections"]:
    print(f"{coll['id']:40}  {coll['title']}")
"""

# Now that I have chosen the collection, I have commented with # all the above

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


# --- Convert to DataFrame ---
raw_data = response.json()
print(f"==={raw_data}===")


# --- data info ---
print(f"===raw_data.keys()===")


# --- backup ---
raw_data_backup = copy.deepcopy(raw_data)


# --- Access direct to the data ---
df = pd.json_normalize(raw_data["features"])
print(f"==={df}===")

# --- removing columns for simplicity ---
print(f"==={df.keys()}===")


removed_columns = ["type","geometry_name","geometry.type", "geometry.coordinates","properties.diarynr","properties.status",
                  "properties.export_date", "properties.geom_area", "properties.geom_length"]

df_col_ok = df.drop(columns=removed_columns)
print(f"==={df_col_ok}===")


# --- List of the columns ---
print(f"==={list(df_col_ok.columns)}===")


# --- missing values ---
print(f"==={df_col_ok.isna().sum()}===")


# --- QUESTIONS ----
# Top 5 counties to get their permits approved
print(df_col_ok["properties.county"].value_counts().head())


# --- The 1rst mineral ---
print("=== Top 5 ===")
print(df_col_ok["properties.mineral"].value_counts().head())


# --- Permitting length Vs Countied Vs Minerals ---


