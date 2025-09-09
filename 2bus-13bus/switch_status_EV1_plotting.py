import pandas as pd
import matplotlib.pyplot as plt

def load_switch_csv(filepath):
    """
    Load a switch status CSV with two columns: timestamp and status.
    Skips comment lines (starting with '#'), renames columns to 'timestamp' and 'status',
    parses the timestamp, and maps OPEN/CLOSED to 0/1.
    """
    # Read CSV, skipping commented lines beginning with '#'
    df = pd.read_csv(filepath, comment='#')
    # Print the columns found for debugging
    print(f"Loaded {filepath}, columns: {df.columns.tolist()}")
    
    # Identify timestamp and status columns
    ts_col, status_col = df.columns[:2]
    
    # Rename for consistency
    df = df.rename(columns={ts_col: 'timestamp', status_col: 'status'})
    
    # Parse timestamps (full datetime with timezone)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True, errors='coerce')
    
    # Map OPEN/CLOSED to 0/1
    df['status'] = df['status'].map({'OPEN': 0, 'CLOSED': 1})
    
    return df

if __name__ == "__main__":
    # Explicit paths to your CSV files:
    csv_l5_path   = 'sw_status_l5_EV1.csv'    # Path to your L5-EV1 switch CSV
    csv_stor_path = 'sw_status_stor_EV1.csv'  # Path to your storage-EV1 switch CSV

    # Load the CSVs
    df_l5   = load_switch_csv(csv_l5_path)
    df_stor = load_switch_csv(csv_stor_path)

    # Plot the switch statuses as step plots
    plt.figure(figsize=(12, 5))
    plt.step(df_l5['timestamp'],   df_l5['status'],   label='SW-l5-EV1',    where='post')
    plt.step(df_stor['timestamp'], df_stor['status'], label='SW-storage-EV1', where='post', linestyle='--')

    plt.ylim(-0.2, 1.2)
    plt.yticks([0, 1], ['OPEN', 'CLOSED'])
    plt.xlabel('Timestamp')
    plt.ylabel('Switch Status')
    plt.title('EV1 Switch Status Over Time')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
