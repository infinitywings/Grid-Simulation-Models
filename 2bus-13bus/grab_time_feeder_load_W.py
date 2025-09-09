import pandas as pd

# Path to your CSV file
file_path = "1c_EV_Outputs.csv"

# Read the file and skip empty unnamed columns
df = pd.read_csv(file_path)

# Extract only 'time' and 'feeder_load_W' columns
#df_extracted = df[['time', 'feeder_load_W']]
#df_extracted = df[['time', 'feeder_load_W']]
df_extracted = df[['feeder_load_W']]

# Print the result
print(df_extracted)

# Optionally save to a new CSV
df_extracted.to_csv("extracted_feeder_load.csv", index=False)
