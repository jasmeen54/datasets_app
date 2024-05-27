import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd

def init_dashboard(server):
    from app.process_household_data import get_available_sensors

    # Initialize Dash app
    dash_app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname='/dashboard_content/',
        external_stylesheets=['https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css']
    )

    dash_app.title = "Household Data Dashboard"

    # Access the global df from Flask
    from app import df

    # Get available sensors
    sensors = get_available_sensors(df)

    # Define Dash layout
    dash_app.layout = html.Div([
        html.H1("Household Data Dashboard", className="text-center"),
        dcc.Interval(
            id='interval-component',
            interval=300000,  # 300000 milliseconds = 5 minutes
            n_intervals=0
        ),
        html.Div([
            html.Label("Select Sensor:"),
            dcc.Dropdown(
                id='house-dropdown',
                options=[{'label': sensor, 'value': sensor} for sensor in sensors],
                value=None,
                clearable=False,
                className="mb-3"
            )
        ], className="mb-4"),
        html.Div([
            html.Label("Select Date:"),
            dcc.Dropdown(
                id='date-dropdown',
                clearable=False,
                className="mb-3"
            )
        ], className="mb-4"),
        html.Div([
            html.Label("Select Appliance:"),
            dcc.Dropdown(
                id='appliance-dropdown',
                clearable=False,
                className="mb-3"
            )
        ], className="mb-4"),
        html.Div(id='graphs-container')
    ], className="container")

    @dash_app.callback(
        Output('date-dropdown', 'options'),
        [Input('house-dropdown', 'value'), Input('interval-component', 'n_intervals')]
    )
    def set_date_options(selected_sensor, n_intervals):
        from app import df  # Import the updated df
        if selected_sensor:
            available_dates = df[df['sensor'] == selected_sensor]['Time'].dt.date.unique()
            return [{'label': str(date), 'value': str(date)} for date in available_dates]
        return []

    @dash_app.callback(
        Output('date-dropdown', 'value'),
        [Input('date-dropdown', 'options'), Input('interval-component', 'n_intervals')]
    )
    def set_date_value(date_options, n_intervals):
        return None

    @dash_app.callback(
        Output('appliance-dropdown', 'options'),
        [Input('house-dropdown', 'value'), Input('date-dropdown', 'value'), Input('interval-component', 'n_intervals')]
    )
    def set_appliance_options(selected_house, selected_date, n_intervals):
        from app import df  # Import the updated df
        if selected_house and selected_date:
            selected_date = pd.to_datetime(selected_date).date()
            filtered_data = df[(df['sensor'] == selected_house) & (df['Time'].dt.date == selected_date)]
            numeric_columns = [col for col in filtered_data.columns if col not in ['Time', 'sensor', 'Unix'] and pd.api.types.is_numeric_dtype(filtered_data[col])]
            return [{'label': col, 'value': col} for col in numeric_columns]
        return []

    @dash_app.callback(
        Output('appliance-dropdown', 'value'),
        [Input('appliance-dropdown', 'options'), Input('interval-component', 'n_intervals')]
    )
    def set_appliance_value(appliance_options, n_intervals):
        return None

    @dash_app.callback(
        Output('graphs-container', 'children'),
        [Input('house-dropdown', 'value'), Input('date-dropdown', 'value'), Input('appliance-dropdown', 'value'), Input('interval-component', 'n_intervals')]
    )
    def update_graphs(selected_house, selected_date, selected_appliance, n_intervals):
        if not selected_house or not selected_date or not selected_appliance:
            return html.Div("Please select a sensor, a date, and an appliance to display graphs.")

        # Access the global df from Flask
        from app import df  # Import the updated df

        # Filter data for the selected sensor and date
        selected_date = pd.to_datetime(selected_date).date()
        filtered_data = df[(df['sensor'] == selected_house) & (df['Time'].dt.date == selected_date)]

        if filtered_data.empty:
            return html.Div(f"No data available for {selected_house} on {selected_date}.")

        # Plot graph for the selected appliance
        fig = px.line(filtered_data, x='Time', y=selected_appliance, title=f"{selected_appliance} for {selected_house} on {selected_date}")
        graph = dcc.Graph(figure=fig)

        return html.Div(graph)

    return dash_app


































