import pandas as pd
import dash_mantine_components as dmc
from dash import _dash_renderer, Dash, Input, Output, State, html, dcc, callback, Patch
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
import plotly.express as px
import plotly.io as pio
from dash_iconify import DashIconify

from utils import df

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

product_dropdown = dmc.Select(
    id='product_dropdown',
    label='Select product for insight',
    data=[{'label': product, 'value': product} for product in df['product'].dropna().unique()],
    value=df['product'].dropna().iloc[0],
    clearable=True,
    style={'marginBottom': '20px'}
)



def Chart_layout(title, figure):
    return dmc.Paper(
        dmc.Stack(
            [
                dmc.Text(title, fw=700, ta='center', size='lg'),
                dmc.Box(
                    [
                        dmc.Grid(
                            [
                                dmc.GridCol(dcc.Graph(figure=figure),style={"height": "250px"})
                            ]
                        ),
                        dmc.GridCol([
                            dmc.Grid(dmc.Text('write-up')),
                            dmc.Grid([
                                dmc.GridCol(),
                                dmc.GridCol()
                            ])
                     ] )
                    ]
                )
            ]
        ),
         p="sm",
        shadow="sm",
        justify ='Center',
        Grow = True,
        radius="md",
        withBorder=True,
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
    dmc.Container([
        theme_toggle,
        dmc.Text('Food Plastic Chemical Analysis', fw=700, ta='center', size='lg', td="underline", tt="uppercase"),
        
        dmc.Button('Time Insight Button', id='time_insight', n_clicks=0),
        dmc.Collapse(
            dmc.Grid(
                [
                    dmc.GridCol(product_dropdown),
                    dmc.GridCol(dcc.Graph(id='graph-time', style={"height": "250px"}), span=6),  # Placeholder for time analysis chart
                    dmc.GridCol(dcc.Graph(id='graph-concentration', style={"height": "250px"}), span=6),  # Placeholder for concentration chart
                ]
            ),
            id="collapse-2",
            opened=False,
            transitionDuration=1000,
            transitionTimingFunction="linear",
        ),
       dmc.Button('Product Insight Button', id='product_insight', n_clicks=0),
        dmc.Collapse(
            [

                dmc.Grid(
                    [
                        dmc.GridCol(dcc.Graph(id='chemical_level',style={"height": "250px"} ),span=4),
                        dmc.Grid(
                            dmc.Stack([
                                dmc.GridCol(dcc.Graph(id='chemical_level2',style={"height": "250px"} ),span=4),
                                dmc.GridCol(dcc.Graph(id='chemical_level4',style={"height": "250px"} ),span=4)
                            ])
                        ),
                        
                    ]
                ),
                dmc.Grid(
                            [
                                
                                dmc.GridCol(dcc.Graph(id='graph-time1', style={"height": "250px"}), span=4),  # Placeholder for time analysis chart
                                dmc.GridCol(dcc.Graph(id='graph-concentration3', style={"height": "250px"}), span=8),  # Placeholder for concentration chart
                            ]
                        )

            ]
        )
    ])
)

@callback(
    [Output("collapse-2", "opened"),
     Output("time_insight", "children"),
     Output('graph-time', 'figure'),
     Output('graph-concentration', 'figure')],
    [Input("time_insight", "n_clicks"),
     Input("product_dropdown", "value")],
)
def update_charts(n, selected_product):
    # Collapse behavior
    if n % 2 == 0:
        collapse_opened = False
        button_text = 'Time Insight Button'
    else:
        collapse_opened = True
        button_text = 'Hide Time Insight'

    # Filter data based on the selected product
    filtered_df = df[df['product'] == selected_product]

    # Time Analysis chart (filtered data by selected product)
    time_analysis_filtered = filtered_df.groupby('month')[['time_to_collect', 'time_to_ship', 
                                                          'time_to_manufacture_to_ship', 'time_to_manufacture_to_collect']].mean().reset_index()
    time_trend_line_filtered = px.line(time_analysis_filtered, x='month', y=['time_to_collect', 'time_to_ship', 
                                                                                'time_to_manufacture_to_ship', 'time_to_manufacture_to_collect'],
                                       labels={'value': 'Average Days', 'month': 'Month'},
                                       title=f'Average Time Analysis for {selected_product}')

    # Chemical Concentration chart (filtered data by selected product)
    df_filtered_long = filtered_df.melt(id_vars=['months_to_expiration'], value_vars=chemicals, 
                                        var_name='Chemical', value_name='Concentration (ng/g)')
    concentration_by_month_filtered = px.scatter(df_filtered_long, x='months_to_expiration', y='Concentration (ng/g)', 
                                                 color='Chemical',
                                                 labels={'months_to_expiration': 'Months to Expiration', 
                                                         'Concentration (ng/g)': 'Concentration (ng/g)', 
                                                         'Chemical': 'Chemical'},
                                                 title=f'Chemical Concentration vs. Months to Expiration for {selected_product}')

    return collapse_opened, button_text, time_trend_line_filtered, concentration_by_month_filtered





    


if __name__=="__main__":
    app.run(debug = True, port=6030)