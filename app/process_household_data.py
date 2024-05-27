import pandas as pd

# Mapping dictionary for renaming appliances
appliance_mapping = {
    'Appliance1': 'Refrigerator',
    'Appliance2': 'Washing machine',
    'Appliance3': 'Dryer',
    'Appliance4': 'Dish washer',
    'Appliance5': 'Toaster',
    'Appliance6': 'Kettle',
    'Appliance7': 'Microwave',
    'Appliance8': 'Oven',
    'Appliance9': 'Iron'
}

def process_data(data):
    processed_data = []
    for item in data:
        row = item['data']
        row['sensor'] = item['sensor']
        processed_data.append(row)
    
    df = pd.DataFrame(processed_data)
    
    # Rename appliance columns based on appliance_mapping
    df.rename(columns=appliance_mapping, inplace=True)
    
    # Ensure 'Time' column is datetime type for correct sorting
    df['Time'] = pd.to_datetime(df['Time'])
    
    # Sort DataFrame by 'Time' in ascending order
    df.sort_values(by='Time', inplace=True)
    
    return df

def get_available_sensors(df):
    # Extract unique sensors from the DataFrame
    return df['sensor'].unique().tolist()

def get_available_dates(df):
    # Extract unique dates from the Time column
    return df['Time'].dt.date.unique().tolist()












