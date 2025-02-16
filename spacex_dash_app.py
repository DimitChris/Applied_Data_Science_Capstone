import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Load dataset
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Get min and max payload values
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server

# Create list of launch sites for dropdown
unique_launch_sites = spacex_df['Launch Site'].unique().tolist()
dropdown_options = [{'label': 'All Sites', 'value': 'All Sites'}] + [
    {'label': site, 'value': site} for site in unique_launch_sites
]

# App layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # Launch Site Dropdown
    dcc.Dropdown(
        id='site_dropdown',
        options=dropdown_options,
        placeholder='Select a Launch Site here',
        searchable=True,
        value='All Sites'
    ),
    html.Br(),

    # Pie Chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # Payload Range Slider
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload_slider',
        min=0, max=10000, step=1000,
        marks={0: '0')
                100: '100'},
        value=[min_payload, max_payload]
    ),

    # Scatter Plot
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for Pie Chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site_dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'All Sites':
        fig = px.pie(spacex_df, names='Launch Site', values='class',
                     hole=.3, title='Total Success Launches by Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(filtered_df, names='class',
                     hole=.3, title=f'Total Success/Failure for {selected_site}')
    return fig

# Callback for Scatter Plot
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site_dropdown', 'value'),
     Input('payload_slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if selected_site != 'All Sites':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    fig = px.scatter(filtered_df, x="Payload Mass (kg)", y="class",
                     color="Booster Version", size='Payload Mass (kg)',
                     hover_data=['Payload Mass (kg)'])
    return fig

# Run app
if __name__ == '__main__':
    app.run_server(debug=True)