import pandas as pd
from collections import defaultdict

CSV_PATH = '7_25_24 Deployment Data - e00fce68c32982d6d24ba749.csv'


def parse_sensor_data(sensor_data):
    """
    Parse the sensor data for grouping them by ids
    """
    sensor_data = sensor_data.strip('{}').split(', ')
    sensor_data_dict = {}
    for item in sensor_data:
        key, value = item.split('=')
        if key == "id" or key == "moisture":
            sensor_data_dict[key] = int(float(value))
        elif key == "lid_status":
            sensor_data_dict[key] = True if value == '1.0' else False
        else:
            sensor_data_dict[key] = (value)
    return sensor_data_dict


def get_data(custom_data=None):
    if not isinstance(custom_data, pd.DataFrame):
        df = pd.read_csv(CSV_PATH, low_memory=False, usecols=[0, 1, 2])
    else:
        df = custom_data
    
    df['Date and Time'] = pd.to_datetime(df['Date and Time'])
    df = df.dropna()
    df = df.reset_index(drop=True)

    # Spread the sensor data to different columns (each data field corresponds to one column)
    df['Sensor Data'] = df['Sensor Data'].apply(parse_sensor_data)
    df_sensor_data = pd.json_normalize(df['Sensor Data'])
    df_sensor_data = df_sensor_data.apply(pd.to_numeric)
    df = pd.concat([df.drop(columns=['Sensor Data']), df_sensor_data], axis=1)

    data = defaultdict(lambda:defaultdict(list))

    for _, row in df.iterrows():
        data[row["Device "]][row["id"]].append(row.to_dict())

    return data


def get_data_df():
    df = pd.read_csv(CSV_PATH, low_memory=False, usecols=[0, 1, 2])
    df['Date and Time'] = pd.to_datetime(df['Date and Time'])
    df = df.dropna()
    df = df.reset_index(drop=True)

    # Spread the sensor data to different columns (each data field corresponds to one column)
    df['Sensor Data'] = df['Sensor Data'].apply(parse_sensor_data)
    df_sensor_data = pd.json_normalize(df['Sensor Data'])
    df_sensor_data = df_sensor_data.apply(pd.to_numeric)
    df = pd.concat([df.drop(columns=['Sensor Data']), df_sensor_data], axis=1)

    return df


def get_min_max_time_range(df):
   return [df['Date and Time'].min(), df['Date and Time'].max()]