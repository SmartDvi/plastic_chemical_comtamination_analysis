import pandas as pd
import dash_mantine_components as dmc
from dash import _dash_renderer, Dash, Input, Output, State, html, dcc, callback, Patch
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
import plotly.express as px
import plotly.io as pio
import numpy as np
from dash_iconify import DashIconify

from utils import (df, 
                   proces_values,
                   product_dropdown_time,
                   product_dropdown_Compostion,
                   product_dropdown_risk,
                   time_analysis,
                   process_chemical_values
                   )

dmc.add_figure_templates(default='mantine_dark')

_dash_renderer._set_react_version("18.2.0")

app = Dash(external_stylesheets=dmc.styles.ALL)


theme_toggle = dmc.ActionIcon(
    [
        dmc.Paper(DashIconify(icon="radix-icons:sun", width=25), darkHidden=True),
        dmc.Paper(DashIconify(icon="radix-icons:moon", width=25), lightHidden=True),
    ],
    variant="transparent",
    color="yellow",
    id="color-scheme-toggle",
    size="lg",
)

# developing the charts for the dashboard
# Group by month and calculate the average time for each stage
time_analysis = df.groupby('month')[['time_to_collect', 'time_to_ship', 'time_to_manufacture_to_ship', 'time_to_manufacture_to_collect']].mean().reset_index()
# Plotting with Plotly Express
time_trend_line = px.line(time_analysis, x='month', y=['time_to_collect', 'time_to_ship', 'time_to_manufacture_to_ship', 'time_to_manufacture_to_collect'],
              labels={'value': 'Average Days', 'month': 'Month'},
              title='Average Time Analysis for Product Stages')


# Handle cases where dates might be missing or invalid by filtering them out
df = df.dropna(subset=['expiration_date', 'manufacturing_date'])

# Calculate the difference in months
df['months_to_expiration'] = df.apply(
    lambda row: (relativedelta(row['expiration_date'], row['manufacturing_date']).years * 12) + relativedelta(
        row['expiration_date'], row['manufacturing_date']).months,
    axis=1
)

# Choose relevant chemicals for visualization
chemicals = ['DEHP_ng_g', 'BPA_ng_g', 'DBP_ng_g']

# Melt the dataframe to convert chemicals from wide to long format
df_long = df.melt(id_vars=['months_to_expiration'], value_vars=chemicals, 
                  var_name='Chemical', value_name='Concentration (ng/g)')

# Create the scatter plot
Concentration_by_month = px.scatter(df_long, x='months_to_expiration', y='Concentration (ng/g)', color='Chemical',
                 labels={'months_to_expiration': 'Months to Expiration', 'Concentration (ng/g)': 'Concentration (ng/g)', 'Chemical': 'Chemical'},
                 title='Chemical Concentration vs. Months to Expiration')

app.layout = dmc.MantineProvider(
    dmc.Container(
        
        [
        theme_toggle,
        dmc.Text('Food Chemical Analysis', fw=700, ta='center', size='lg', td="underline", tt="uppercase"),
        
        dmc.Button('Click fir Time Insight', id='time_insight', n_clicks=0),
        dmc.Collapse(
            dmc.Grid(
                [
                    dmc.GridCol(product_dropdown_time),
                    dmc.GridCol(dcc.Graph(id='graph-time', style={"height": "300px"}), span=6),  
                    dmc.GridCol(dcc.Graph(id='graph-concentration', style={"height": "300px"}), span=6),  
                ]
            ),
            id="collapse-ts",
            opened=False,
            transitionDuration=1000,
            transitionTimingFunction="linear",
        ),

        dmc.Space(),

        dmc.Button('Chemical Composition Insight', id='chm_comp_insight', n_clicks=0),
        dmc.Collapse(
            
                dmc.Grid([
                        dmc.GridCol(product_dropdown_Compostion),
                    dmc.Grid(
                        [
                            #dmc.GridCol(product_dropdown, span=12),
                            dmc.GridCol(dcc.Graph(id='chemical_level',style={"height": "300px"} ),span=4),
                            dmc.Grid(
                                dmc.Group([
                                    dmc.GridCol(dcc.Graph(id='precentile_comp_chem9',style={"height": "300px"} ),span=2),
                                    dmc.GridCol(dcc.Graph(id='chemical_level4',style={"height": "300px"} ),span=4)
                                ])
                            ),
                            
                        ]
                    ),
                    

                    dmc.Grid(
                                [
                                    
                                    dmc.GridCol(dcc.Graph(id='graph-time1', style={"height": "300px"}), span=4),  # Placeholder for time analysis chart
                                    dmc.GridCol(dcc.Graph(id='precentile_comp_chem', style={"height": "300px"}), span=8),  # Placeholder for concentration chart
                                ]
                            ),
                ]),
                    id='collapse_cci',
                    opened=False,
                    transitionDuration=1000,
                    transitionTimingFunction='linear', ),

                    dmc.Space(),

                    dmc.Button('Click for Risk assesment Insight', id='as_insight', n_clicks=0),
                    dmc.Collapse(
            
                        dmc.Grid([
                            dmc.GridCol(product_dropdown_risk),
                            dmc.GridCol(dcc.Graph(id='test_method', style={"height": "300px"}), span=6),  
                            dmc.GridCol(dcc.Graph(id='triplicate_1_sample', style={"height": "300px"}), span=12),  
                        
                        ]),
                            id='collapse_rs',
                            opened=False,
                            transitionDuration=1000,
                            transitionTimingFunction='linear', ) 



            
    ], 
    px="xs")   
)

@callback(
    [Output("collapse-ts", "opened"),
     Output("time_insight", "children"),
     Output('graph-time', 'figure'),
     Output('graph-concentration', 'figure'),
      
     ],
    [Input("time_insight", "n_clicks"),
     Input("time_dropdown", "value")],
)
def update_charts(n_clicks_time, selected_product):
    # Collapse behavior
    
    if n_clicks_time % 2 == 0:
        collapse_opened = False
        button_text = 'Time Insight Button'
    else:
        collapse_opened = True
        button_text = 'Hide Time Insight'

    

    # Handle selected_product being None or invalid
    
    # Filter data based on the selected product
    filtered_df = df if not selected_product else df[df['product'] == selected_product]

    # Time Analysis chart (filtered data by selected product)
    time_analysis_filtered = filtered_df.groupby('month')[['time_to_collect', 'time_to_ship', 
                                                          'time_to_manufacture_to_ship', 'time_to_manufacture_to_collect']].mean().reset_index()
    time_trend_line_filtered = px.line(time_analysis_filtered, x='month', y=['time_to_collect', 'time_to_ship', 
                                                                                'time_to_manufacture_to_ship', 'time_to_manufacture_to_collect'],
                                       labels={'value': 'Average Days', 'month': 'Month'},
                                       title=f'Average Time Analysis for {selected_product}')

    # Chemical Concentration chart (filtered data by selected product)

    chemicals = ['BBP_ng_g', 'DINP_ng_g', 'DIDP_ng_g', 'DEP_ng_g', 'DMP_ng_g', 'DIBP_ng_g', 'DNHP_ng_g', 'DCHP_ng_g', 'DNOP_ng_g', 'BPS_ng_g', 'BPF_ng_g', 'DEHT_ng_g', 'DEHA_ng_g', 'DINCH_ng_g', 'DIDA_ng_g']
    for chemical in chemicals:
        filtered_df[chemical] = filtered_df[chemical].apply(proces_values)
    df_filtered_long = filtered_df.melt(id_vars=['months_to_expiration'], value_vars=chemicals, 
                                        var_name='Chemical', value_name='Concentration (ng/g)')
    concentration_by_month_filtered = px.scatter(df_filtered_long, x='months_to_expiration', y='Concentration (ng/g)', 
                                                 color='Chemical',
                                                 labels={'months_to_expiration': 'Months to Expiration', 
                                                         'Concentration (ng/g)': 'Concentration (ng/g)', 
                                                         'Chemical': 'Chemical'},
                                                 #title=f'Chemical Concentration vs. Months to Expiration for {selected_product}'
                                                 )

    

    


    return collapse_opened, button_text, time_trend_line_filtered, concentration_by_month_filtered


@callback(
    [
        Output('collapse_cci', 'opened'),
        Output('chm_comp_insight', 'children'),
        Output('precentile_comp_chem', 'figure'),
    ],
    [
        Input("chm_comp_insight", "n_clicks"),
        Input("comp_dropdown", "value"),
    ]
)

def update_chm_comp_insight(n_clicks_product, selected_product):
    # Toggle collapse state and button text
    opened = n_clicks_product % 2 != 0
    button_text = 'Hide Product Insight' if opened else 'Product Insight Button'

    # Filter data by product
    filtered_df = df if not selected_product else df[df['product'] == selected_product]
    
    # Aggregate chemical concentrations
    grouped_df = filtered_df.groupby(['collected_at', 'product', 'shipped_in'])[['BBP_ng_g', 'DINP_ng_g', 'DIDP_ng_g',
                                                                                  'DEP_ng_g', 'DMP_ng_g', 'DIBP_ng_g', 'DNHP_ng_g', 
                                                                                  'DCHP_ng_g', 'DNOP_ng_g', 'BPS_ng_g', 'BPF_ng_g', 
                                                                                  'DEHT_ng_g', 'DEHA_ng_g', 'DINCH_ng_g', 'DIDA_ng_g']].sum()

    # Process values for all chemicals
    chemicals = ['BBP_ng_g', 'DINP_ng_g', 'DIDP_ng_g', 'DEP_ng_g', 'DMP_ng_g',
                  'DIBP_ng_g', 'DNHP_ng_g', 'DCHP_ng_g', 'DNOP_ng_g', 'BPS_ng_g',
                    'BPF_ng_g', 'DEHT_ng_g', 'DEHA_ng_g', 'DINCH_ng_g', 'DIDA_ng_g']
    for chemical in chemicals:
        grouped_df[chemical] = grouped_df[chemical].apply(proces_values)

    # Create boxplot visualization
    percentilr_comp_chem = px.box(
        grouped_df.reset_index().melt(id_vars='shipped_in', value_vars=chemicals),
        x='shipped_in',
        y='value',
        color='variable',
        title='Comparison of Chemical Exposure Levels Across Products',
        
    )

    # Customize layout
    percentilr_comp_chem.update_layout(
        yaxis_title='Chemical Concentration (ng/g)',
        xaxis_title='Collection Date',
        title={
            'text': "Comparison of Key Chemicals Across Products<br><sup>Percentile distribution of concentrations for DEHP, DBP, and BPA</sup>",
            'x': 0.5
        },
        legend_title_text="Chemical",
        font=dict(size=12),
    )


    # Customize hover information
    percentilr_comp_chem.update_traces(
        hovertemplate="Chemical Name: %{y}<br>Collection Date: %{x}<br>Concentration: %{y}<extra></extra>"
    )

    return opened, button_text, percentilr_comp_chem


@callback(
    [Output('collapse_rs', 'opened'),
     Output('as_insight', 'children'),
     Output('test_method', 'figure'),
     Output('triplicate_1_sample', 'figure'),],
    [Input("as_insight", "n_clicks"),
     Input("risk_dropdown", "value")],
)
def update_risk_analysis(n_clicks_risk, selected_product):
    """opened = n_clicks_risk % 2 != 0
    button_text = 'Hide Risk assement Insight' if opened else 'Risk acessment Insight '
"""
    if n_clicks_risk % 2 == 0:
        collapse_opened = False
        button_text = 'Risk acessment Insight '
    else:
        collapse_opened = True
        button_text = 'Hide Risk assement Insight'

    
    # Filter dataset based on product selection
    filtered_df = df if not selected_product else df[df['product'] == selected_product]

    chemicals = [
        'BBP_ng_g', 'DINP_ng_g', 'DIDP_ng_g', 'DEP_ng_g', 'DMP_ng_g',
        'DIBP_ng_g', 'DNHP_ng_g', 'DCHP_ng_g', 'DNOP_ng_g', 'BPS_ng_g',
        'BPF_ng_g', 'DEHT_ng_g', 'DEHA_ng_g', 'DINCH_ng_g', 'DIDA_ng_g',
        'DEHP_ng_g', 'BPA_ng_g'  # Include DEHP and BPA for TDI analysis
    ]

    # Process chemical values
    filtered_df = process_chemical_values(filtered_df, chemicals)
    print(filtered_df['DIDP_ng_g'])
    # Define TDi value standard for chemicals
    TDI_vstd = {'DEHP_ng_g': 1.5, 'BPA_ng_g': 0.2}

    # Assess exceedance of TDI for each chemical
    filtered_df['DEHP_exceed_TDI'] = filtered_df['DEHP_ng_g'] > TDI_vstd['DEHP_ng_g']
    filtered_df['BPA_exceed_TDI'] = filtered_df['BPA_ng_g'] > TDI_vstd['BPA_ng_g']

    # Count how many products exceed the TDI for each chemical
    dehp_exceed_count = filtered_df['DEHP_exceed_TDI'].sum()
    bpa_exceed_count = filtered_df['BPA_exceed_TDI'].sum()

    # Create a summary DataFrame
    data = {
        'Chemical': ['DEHP', 'BPA'],
        'Exceed_TDI_Count': [dehp_exceed_count, bpa_exceed_count],
        'Total_Products': [len(filtered_df), len(filtered_df)],
    }
    exceedance_df = pd.DataFrame(data)

    # Plot the exceedance data
    TDI_indication = px.bar(
        exceedance_df,
        x='Chemical',
        y='Exceed_TDI_Count',
        text='Exceed_TDI_Count',
        labels={'Exceed_TDI_Count': 'Number of Products Exceeding TDI'},
        title="Exceedance of TDI Values by Chemical",
    )
    TDI_indication.update_traces(texttemplate='%{text}', textposition='outside')


    # Create a scatter plot for triplicate samples
    fig_triplicate_samples = px.scatter(
        filtered_df, x='triplicate_1_sample_id', y='triplicate_2_sample_id', color='product',
        title="Triplicate Sample Comparison"
    )
    fig_triplicate_samples.update_layout(
        xaxis_title='Triplicate 1 Sample ID',
        yaxis_title='Triplicate 2 Sample ID'
    )


    return TDI_indication, button_text, collapse_opened,  fig_triplicate_samples


if __name__=="__main__":
    app.run(debug = True, port=6030)
