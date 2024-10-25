from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc


pd.set_option('display.float_format', lambda x: f'{x:,.3f}') 

# Load and clean your dataset
market_df = pd.read_csv('Market_Data.csv')
market_df = market_df.rename(columns={'TICKERS': 'Ticker'})

# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])


# Define the layout with dropdowns and graphs
app.layout = dbc.Container([
    dbc.Row([
        # Title
        dbc.Col(html.H1('Stock Valuation Finder', className='text-center mb-2', style={'padding-top': '20px'}), width=12),
        
        # Subtitle (Author)
        dbc.Col(html.H6('By Daniel De La Hormaza', className='text-center', style={'font-size': '20px', 'color': 'white'}), width=12, className='mb-4'),
        
        # Notes Box
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.P("Version 1. Data as of Oct 23, 2024", style={'margin-bottom': '5px'}, className='mb-4'),
                    html.P("Select a Sector and an Industry. Explore stocks to find valuation targets.", style={'margin-bottom': '5px'}, className='mb-4'),
                    html.P("Data obtained from Yahoo Finance using yfinance API.", style={'margin-bottom': '5px'}),
                    html.P("Upcoming Improvements:", style={'margin-bottom': '5px'}),
                    html.Ol([
                        html.Li("Correct for Missing Data"),
                        html.Li("Improve Presentation of a number of data points"),
                        html.Li("Performance Improvements")
                    ], style={'padding-left': '20px'}),
                ]),
                style={'background-color': '#A1AEB1', 'border': '1px solid #444', 'color': 'black'}
            ), 
            width=12, className='mb-4'
        )
    ]),
    
   # Dropdowns Row
dbc.Row([
    dbc.Col(dcc.Dropdown(
        market_df.Sector.unique(), 
        'Consumer Cyclical', 
        id='dropdown-sector', 
        multi=False, 
        style={
            'backgroundColor': '#A1AEB1',  # Dark background
            'color': 'black'  # Ensure white text for selected value
        }, 
        className='text-black'  # Add Bootstrap text-white class for consistency
    ), width=6),
    
    dbc.Col(dcc.Dropdown(
        id='dropdown-industry', 
        value=['Restaurants'], 
        multi=True, 
        style={
            'backgroundColor': '#A1AEB1',  # Dark background
            'color': 'black'  # Ensure white text for selected value
        }, 
        className='text-black'  # Bootstrap class for white text
    ), width=6),
], className='mb-4'),
   
    # Treemap Column with loading
    dbc.Row([
        dbc.Col(
            dcc.Loading(
                id="loading-treemap",
                type="default",  
                children=dcc.Graph(id='graph-content', style={'height': '500px'})
            ), width=12
        )
        
    ], className='mb-4'),
    
    
     # Data Table Column with loading
    dbc.Row([
        dbc.Col(
            dcc.Loading(
                id="loading-table",
                type="circle",  
                children=dash_table.DataTable(
                    id='table-content', 
                    columns=[
                        {"name": i, "id": i} for i in [
                            "Ticker", "Name", "Beta", "Sector", "Industry", 
                            "P/E_Ratio", "FWD_P/E_Ratio", "PEG_Ratio", 
                            "P/B_Ratio", "P/S_Ratio_TTM", "EV/EBITDA", 
                            "Dividend_Yield", "Profit_Margin", "Operating_Margin"
                        ]
                    ],
                    style_table={'height': '500px', 'overflowY': 'auto'},  
                    style_cell={'textAlign': 'left', 'backgroundColor': '#1e1e1e', 'color': 'white'},  
                    style_header={
                        'whiteSpace': 'normal',
                        'height': 'auto',
                        'backgroundColor': '#343a40',  
                        'color': 'white'
                    },
                    style_cell_conditional=[
                        {'if': {'column_id': 'Ticker'}, 'width': '60px', 'position': 'sticky', 'left': 0, 'backgroundColor': '#1e1e1e'},  
                    ],
                    fixed_rows={'headers': True}  
                )
            ), width=12
        )

    ], className='mb-4'),

    # Scatter Plot Row (P/E Ratio, P/B Ratio)
    dbc.Row([
        dbc.Col(dcc.Loading(id='loading-pe', children=dcc.Graph(id='pe-scatter-plot')), width=6),
        dbc.Col(dcc.Loading(id='loading-pb', children=dcc.Graph(id='pb-scatter-plot')), width=6),
    ], className='mb-4'),

    # Scatter Plot Row (P/S Ratio, EV/EBITDA)
    dbc.Row([
        dbc.Col(dcc.Loading(id='loading-ps', children=dcc.Graph(id='ps-scatter-plot')), width=6),
        dbc.Col(dcc.Loading(id='loading-ev', children=dcc.Graph(id='ev-ebitda-scatter-plot')), width=6),
    ], className='mb-4'),
], fluid=True)

# Callback to update the Industry dropdown based on the selected Sector
@callback(
    Output('dropdown-industry', 'options'),
    Input('dropdown-sector', 'value')
)
def set_industry_options(selected_sector):
    filtered_df = market_df[market_df.Sector == selected_sector]
    industry_options = [{'label': i, 'value': i} for i in filtered_df.Industry.unique()]
    return industry_options

# Separated Callbacks

# Callback for Treemap
@callback(
    Output('graph-content', 'figure'),
    [Input('dropdown-sector', 'value'), Input('dropdown-industry', 'value')]
)
def update_treemap(selected_sector, selected_industries):
    dff = filter_data(selected_sector, selected_industries)
    return generate_treemap(dff)

# Callback for P/E Scatter Plot
@callback(
    Output('pe-scatter-plot', 'figure'),
    [Input('dropdown-sector', 'value'), Input('dropdown-industry', 'value')]
)
def update_pe_scatter(selected_sector, selected_industries):
    dff = filter_data(selected_sector, selected_industries)
    return generate_scatter(dff, 'P/E_Ratio')

# Callback for P/B Scatter Plot
@callback(
    Output('pb-scatter-plot', 'figure'),
    [Input('dropdown-sector', 'value'), Input('dropdown-industry', 'value')]
)
def update_pb_scatter(selected_sector, selected_industries):
    dff = filter_data(selected_sector, selected_industries)
    return generate_scatter(dff, 'P/B_Ratio')

# Callback for P/S Scatter Plot
@callback(
    Output('ps-scatter-plot', 'figure'),
    [Input('dropdown-sector', 'value'), Input('dropdown-industry', 'value')]
)
def update_ps_scatter(selected_sector, selected_industries):
    dff = filter_data(selected_sector, selected_industries)
    return generate_scatter(dff, 'P/S_Ratio_TTM')

# Callback for EV/EBITDA Scatter Plot
@callback(
    Output('ev-ebitda-scatter-plot', 'figure'),
    [Input('dropdown-sector', 'value'), Input('dropdown-industry', 'value')]
)
def update_ev_ebitda_scatter(selected_sector, selected_industries):
    dff = filter_data(selected_sector, selected_industries)
    return generate_scatter(dff, 'EV/EBITDA')

# Callback for Table
@callback(
    Output('table-content', 'data'),
    [Input('dropdown-sector', 'value'), Input('dropdown-industry', 'value')]
)
def update_table(selected_sector, selected_industries):
    dff = filter_data(selected_sector, selected_industries)
    return dff.to_dict('records')

# Helper Functions
def filter_data(selected_sector, selected_industries):
    if not selected_industries:
        return market_df[market_df.Sector == selected_sector].copy()
    else:
        return market_df[(market_df.Sector == selected_sector) & 
                         (market_df.Industry.isin(selected_industries))].copy()

def generate_treemap(dff):
    dff['Market_Cap_Million'] = dff['Market_Cap'] / 1e6
    fig = px.treemap(dff, path=['Sector', 'Industry', 'Ticker'], values='Market_Cap',
                     color='Market_Cap', color_continuous_scale='Viridis',
                     custom_data=['Ticker', 'Name', 'Market_Cap_Million'])
    fig.update_traces(hovertemplate=
                      '<b>Ticker:</b> %{customdata[0]}<br>' +
                      '<b>Name:</b> %{customdata[1]}<br>' +
                      '<b>Market Cap:</b> %{customdata[2]:,.2f}M')
    fig.update_layout(
        title='Market Capitalization by Sector and Industry',
        title_font_size=20,
        title_x=0.5,
        title_xanchor='center'
    )
    return fig

def generate_scatter(dff, metric):
    median_metric = dff[metric].median()
    scatter = px.scatter(dff, x="Ticker", y=metric, color="Industry", hover_data=['Name'])
    scatter.add_hline(y=median_metric, line_dash="dash", 
                      annotation_text=f"Median {metric}: {median_metric:.2f}", 
                      annotation_position="top left")
    scatter.update_layout(
        title=f'{metric} Comparison',
        title_font_size=18,
        title_x=0.5,
        title_xanchor='center'
    )
    return scatter

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)