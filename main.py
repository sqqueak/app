import parse_csv 

import pandas as pd
import os

from flask import Flask, render_template, request, jsonify

from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import json


app = Flask(__name__)

@app.route('/')
def index():
    # Load data
    df = pd.DataFrame.from_dict(parse_csv.get_data_df())
    min_time, max_time = parse_csv.get_min_max_time_range(df)
    return render_template('index.html', min_time=min_time, max_time=max_time, columns=df.columns[3:])

@app.route('/plot', methods=['POST'])
def plot():
    # Getting values
    device_name = request.form.get('device_name')
    data_fields = request.form.getlist('data_fields')[0].split(",")
    time_range = request.form.get('time_range')
    uploaded_file = request.files.get('file')

    # Handling default values
    if not device_name == 0:
        device_name = "e00fce68c32982d6d24ba749"
    if len(data_fields) == 0:
        data_fields = ['air_temp']
    if not time_range or time_range == ",":
        time_range = (None, None)

    print(device_name, data_fields, time_range)

    try:
        df = pd.read_csv(uploaded_file, low_memory=False, usecols=[0, 1, 2])
        fig = time_series_plot(device_name, data_fields, time_range, df)
    except:
        fig = time_series_plot(device_name, data_fields, time_range)
    
    return jsonify(fig=fig.to_json())

def time_series_plot(device_name, data_fields, time_range, custom_data=None):
    if isinstance(custom_data, pd.DataFrame):
        data = parse_csv.get_data(custom_data)[device_name]
        min_time, max_time = parse_csv.get_min_max_time_range(custom_data)
    else:
        data = parse_csv.get_data()[device_name] 
        min_time, max_time = parse_csv.get_min_max_time_range(pd.DataFrame.from_dict(parse_csv.get_data_df()))
    fig = make_subplots(rows=max(len(data_fields), 1), cols=1)

    # Set time range
    if isinstance(time_range, str):
        start_time = max_time - pd.Timedelta(time_range)
        end_time = max_time
    elif not time_range[0] and not time_range[1]:
        start_time, end_time = min_time, max_time
    else:
        start_time, end_time = time_range

    # Make sure that every plot uses the same colors for a specific ID
    unique_ids = list(data.keys())
    colors = px.colors.qualitative.Plotly  # Use Plotly's color palette
    color_map = {unique_ids[i]: colors[i % len(colors)] for i in range(len(unique_ids))}

    # Plot each ID
    for _, id_value in enumerate(data.keys()):
        curr_data = pd.DataFrame.from_dict(data[id_value])
        curr_data = curr_data[(curr_data['Date and Time'] >= start_time) & (curr_data['Date and Time'] <= end_time)]

        # Plot each user-specified data field
        for j, field in enumerate(data_fields):
            fig.add_trace(
                go.Scatter(
                    x=curr_data["Date and Time"], 
                    y=curr_data[field],
                    mode="lines", 
                    name=f'ID: {id_value}',
                    line=dict(color=color_map[id_value]),
                    showlegend=(j == 0)
                ),
                row=j+1, 
                col=1
            )

        for j in range(len(data_fields)):
            fig.update_xaxes(title_text=f'Time', row=j+1, col=1)
            fig.update_yaxes(title_text=f'{data_fields[j]}', row=j+1, col=1)

    # Clean up plots visually
    fig.update_traces(connectgaps=True)
    fig.update_layout(
        plot_bgcolor="#f9f9f9", 
        paper_bgcolor="#f9f9f9", 
        height=400*len(data_fields)
    )
    return fig

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
