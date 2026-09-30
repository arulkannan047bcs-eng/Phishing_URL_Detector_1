import pandas as pd

# Load dataset
df = pd.read_csv("dataset.csv")

# Display dataset
print(df)

# Display number of rows and columns
print("\nDataset Shape:")
print(df.shape)

# Display column names
print("\nColumn Names:")
print(df.columns)