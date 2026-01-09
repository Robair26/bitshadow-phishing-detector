import os
import pandas as pd

# Folder with all the CSV files
DATA_FOLDER = 'data'

# Standard column names
TEXT_COL = 'text'
LABEL_COL = 'label'

# List to hold all dataframes
all_dfs = []

# Loop through each CSV file
for filename in os.listdir(DATA_FOLDER):
    if filename.endswith('.csv'):
        filepath = os.path.join(DATA_FOLDER, filename)
        try:
            df = pd.read_csv(filepath)
            print(f"🔍 Loaded: {filename} — {df.shape[0]} rows")

            # Try to standardize column names
            if 'text' in df.columns and 'label' in df.columns:
                clean_df = df[[TEXT_COL, LABEL_COL]]
            else:
                # Try to auto-detect possible text/label columns
                df.columns = [col.lower() for col in df.columns]
                text_col_guess = [col for col in df.columns if 'text' in col or 'content' in col or 'email' in col]
                label_col_guess = [col for col in df.columns if 'label' in col or 'spam' in col or 'phishing' in col]

                if text_col_guess and label_col_guess:
                    clean_df = df[[text_col_guess[0], label_col_guess[0]]]
                    clean_df.columns = [TEXT_COL, LABEL_COL]
                else:
                    print(f"⚠️ Could not auto-detect columns in {filename}. Skipped.")
                    continue

            # Drop missing values
            clean_df.dropna(inplace=True)

            # Make sure label is binary
            clean_df[LABEL_COL] = clean_df[LABEL_COL].apply(lambda x: 1 if str(x).lower() in ['1', 'phishing', 'spam'] else 0)

            all_dfs.append(clean_df)

        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")

# Combine all into one
if all_dfs:
    combined = pd.concat(all_dfs, ignore_index=True)
    combined.to_csv('cleaned_dataset.csv', index=False)
    print(f"\n✅ Combined and saved to cleaned_dataset.csv — Total rows: {combined.shape[0]}")
else:
    print("❌ No datasets cleaned.")
