from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.express as px
from django_plotly_dash import DjangoDash
import dash_bootstrap_components as dbc

app = DjangoDash('Simple',add_bootstrap_links=True)

style_text={
    'textAlign': 'center',
    'fontsize': 15,
    'font-weight': 'bold',
    'font-style': 'italic',
    }
    
style_left_container={
    'textAlign': 'center',
    'width': '95%',
    'display': 'inline-block'
    }

style_dropdown={
    'width': '50%',
    'margin': '0 auto',
    }
style_slider={
'position': 'fixed',
 'zIndex': '99', 
    }
    
style_container=style={
    'width': '100%'
    }
        
# function to count real cases
def cases(s):
    return sum(s>=1)

# function to count holes
def holes(s):
    return sum(s.isna())
    
def avg_der(s):
    try:
        return (sum(s)/sum(s>=1))-1
    except ZeroDivisionError:
        return 0

#aggregation columns,numeric.
agg_cols=['Issued','Refused','Refused221g','Ready','NVC','AP']  # Excluded and 'InTransit','Transfer',
#Shorter legend labels for viewing plots on mbobile devices
short_legend_lable=['Hole_C','Iss_C','Ref_C','221g_C','Rdy_C','NVC_C','AP_C']

# ISO country data
ISO_country_df=pd.read_pickle('ISO_ALPHA.pkl')

# Aggregation dictionary for area plot totals. Excluded ,'InTransit':[cases],'Transfer':[cases],
agg_dict = {'status':[holes],            
            'Issued':[cases],
            'Refused':[cases],
            'Refused221g':[cases],
            'Ready':[cases],
            'NVC':[cases],
            'AP':[cases],
           }
# Global variables availble to many callbacks with their placeholder values
#hold current ceac region and corresponding embassy list
emblist=""
reg_list=""
default_yr=2023

#load regional area chart data
regional_area_data=pd.read_pickle('ceac_pkl/regional_case_ranges_input.pkl')
#load historical chart data
historical_data=pd.read_pickle('ceac_pkl/historical_CEAC.pkl')
#regional holes bar chart data
regional_holes_data=pd.read_pickle('ceac_pkl/regional_holes_input.pkl')
# grouped regions bar chart data
regional_bar_data=pd.read_pickle('ceac_pkl/regional_grouped_bar_input.pkl')
# grouped consulate bar chart data
consulate_bar_data=pd.read_pickle('ceac_pkl/consulate_bar_input.pkl')  
# grouped consulate area chart data
consulate_area_data=pd.read_pickle('ceac_pkl/consulate_case_ranges_input.pkl')
# grouped consulate area chart data
consulate_global_data=pd.read_pickle('ceac_pkl/consulate_global_derivative_input.pkl')

# APP Layout
right_row_0=dbc.Row(
                html.Div([
                    dcc.Slider(
                        id='year-slider',
                        min=2013,
                        max=2024,
                        step=1,
                        value=default_yr,
                        marks={str(year): str(year) for year in range(2013, 2025)},
                        vertical=True
                    )
                ],style=style_slider)
            )
left_row_1=dbc.Row( html.H3(children="Performance by region",style=style_text),justify="center",class_name="mb-2 mt-2")
left_row_2=dbc.Row(dbc.Col(html.P(children="Select Region below (or year from the adjacent slider)",style=style_text) ))
left_row_3=dbc.Row(dbc.Col(dcc.RadioItems([],"",id="reg-dropdown",inline=True,style=style_text)))
left_row_4=dbc.Row([
                        dbc.Col(html.Div(dcc.Graph(id="area-graph")),lg=6),
                        dbc.Col(html.Div([dcc.Graph(id="historical-graph")]),lg=6)                          
                    ]
                    ,class_name="mt-3"
            )
left_row_5=dbc.Row( [
                        dbc.Col(html.Div([dcc.Graph(id="holes-graph")]),lg=6),
                        dbc.Col(html.Div(dcc.Graph(id="reg-graph")),lg=6)
                    ]
                ,class_name="mt-3"
            )

left_row_6=dbc.Row( html.H3(children="Performance by embassy",style=style_text),justify="center",class_name="mt-3")
            
left_row_7=dbc.Row( html.P(children="Select embassy :",style=style_text),justify="center",class_name="mt-3")

left_row_8=dbc.Row( dcc.Dropdown([],"",id="emb-dropdown",style=style_dropdown ))
left_row_9=dbc.Row([
                        dbc.Col(html.Div([dcc.Graph(id="emb-graph")]),lg=6),
                        dbc.Col(html.Div([dcc.Graph(id="emb-area-graph")]),lg=6)   
                    ]
            ,class_name="mt-3 mb-3"
            )
left_row_10=dbc.Row(dbc.Col(html.Div([dcc.Graph(id="global-deriv-graph")])),class_name="mt-3")


about_tab=dbc.Row(dbc.Col(
        html.Div([
        html.H4("About this App "),
        html.P(["This Dash app was built to provide detailed and complementary information on the DV-lottery program run by the U.S governmwent.\
        It was inspired by a similar app from ",html.A('DV Lottery Charts', href='https://dvcharts.xarthisius.xyz/ceacFY24.html'), ",and the data\
        is uses comes from that website. This app complements that website by providing more information on Holes (see glossary below), \
        Global derivative distribution, comparative performance across DV-years, and more comprehensive visualizations. This app was built using ",\
        html.A('Plotly Dash', href='https://dash.plotly.com/')," , ",html.A('django-plotly-dash', href='https://django-plotly-dash.readthedocs.io/'),\
        " , ",html.A('Dash Bootstrap Components', href='https://dash-bootstrap-components.opensource.faculty.ai/') ," , "," Python and Django.",
        
               ]
        ),
        html.H4("About the DV-Lottery process and data"),
        html.P("The Diversity Immigrant Visa (DV) Program, also known as the Green Card Lottery, awards up to 50,000 immigrant visas each year. \
        It's designed to diversify U.S. immigration by making immigrant visas available to citizens of countries with low immigration rates."),
        html.P("Here's how it works:"),
        html.Ul([
        html.Li([html.B("Eligibility : "), " Citizens of eligible countries can apply during the designated period. The application process is straightforward \
        and free."]),
        html.Li([html.B("Random Selection : "), " Applicants enter the lottery online between early October and early November. A computer randomly selects\
        winners from the pool of applicants."]),
        html.Li([html.B("Winners and Green Cards : "), " If selected, winners and their immediate families receive green cards, granting them permanent residency\
        in the U.S. Less than 1% of applications win, so it's a chance-based opportunity."]),
        html.Li([html.B("CEAC data: ")," CEAC data for the DV-Lottery contains information about all the cases selected (including selected and disqualified) for a given\
        fiscal year, obtained from the Consular Electronic Application Center of the U.S. Department of State.\
        It provides relevant details about interviews conducted in the current DV Program, including visa issuance, administrative processing,\
        and refusals."]),
                ]
        ),
        html.P(["Learn more at ",html.A('travel.state.gov', href='https://travel.state.gov/content/travel/en/us-visas/immigrate/diversity-visa-program-entry.html'), ]),
        html.H4("Glossary"),
        html.P(["The default scope for some of the variables below includes cases and derivatives, except when a",html.Strong(" ' _C '")," is appended to the variables \
        name, denoting cases only; without their derivatives."]),
        html.Ul([
            html.Li([html.B("Hole :"), " Applicants to the Dv-Lottery who got selected during the initial selection then got disqualified for undisclosed reasons."]),
            html.Li([html.B("Iss(Issued) : "), " Cases whose visas got approved."]),
            html.Li([html.B("AP(Administrative Processing):")," Cases that are undergoing additional review or clearance by a consular officer. It’s a temporary status while the case is pending further investigation."]),
            html.Li([html.B("221g( Refused ) : "), " Refusals under section 221(g) of the Immigration and Nationality Act. These cases require additional documentation or processing before a final decision can be made."]),
            html.Li([html.B("Ref (Refused) : "), "Cases that got denied visas."]),
            html.Li([html.B("Rdy( Ready): "), " Cases that are ready for visa issuance pending administrative processing or other final steps."]),
            html.Li([html.B("NVC (National Visa Center) : "), " Cases pending initial processing, post selection. "]),
            html.Li([html.B("der( Derivative) : "), " Dependent on a DV-Lottery case."]),
            html.Li([html.B("Iss.Deriv.avg( Average derivative count) : "), " Average derivative per case."]),
            html.Li([html.B(" Sum : "), " The total number of cases in each category including derivatives."]),  
            html.Li([html.B(" ~max_CN : "), " The maximum case number for a given region or embassy."]), 
        ]),
                  ]
        ),class_name="description"               
                  )
           )
explore_tab=dbc.Container(
                dbc.Row([              
                        dbc.Col([
                                left_row_1,
                                left_row_2,
                                left_row_3,
                                left_row_4,
                                left_row_5,
                                left_row_6,
                                left_row_7,
                                left_row_8,
                                left_row_9,
                                left_row_10
                                ],xs={"size":11,"order":2,"offset":0},lg={"size":11,"order":1,"offset":0}
                               ),
                        dbc.Col(right_row_0,xs={"size":1,"order":1,"offset":10},lg={"size":1,"order":2,"offset":0}
                               )                                
                        ]
                ),fluid=True
            )
            
sources_tab=dbc.Row(dbc.Col(
                        html.Ul([
                                html.Li([dbc.Button("Website source code", href='https://github.com/Forwah2023', color="primary", target="_blank")]),
                                html.Li([dbc.Button("Data processing code", href='https://github.com/Forwah2023', color="primary", target="_blank",class_name="mt-3")])
                                 ]
                        ),
                        width={"size": 6, "offset": 0}, class_name="mt-5"
                    ),
                    
            )

app.layout=dbc.Tabs(
    [
        dbc.Tab(about_tab, label="About",label_style=style_text),
        dbc.Tab(explore_tab, label="Explore",label_style=style_text),
        dbc.Tab(sources_tab, label="Code",label_style=style_text),
    ],
    id="tabs",
    active_tab="tab-1",
)


# set embassy list
def set_emb_list(year,**kwargs):
    global  emblist,reg_list,consulate_global_data
    #List of available regions embassies
    in_year=consulate_global_data['year']==str(year)
    sub_ceac_yr=consulate_global_data[in_year]
    reg_list=sub_ceac_yr['region'].cat.categories.tolist()
    if kwargs:
        in_region=sub_ceac_yr['region']==kwargs.get('region',"AF")
        sub_ceac_reg=sub_ceac_yr[ in_region]
        emblist=sorted(sub_ceac_reg['cap_cons'].dropna().unique().tolist())
    return

@app.callback(
    Output("reg-dropdown","options"),
    Output("reg-dropdown","value"),
    Input("year-slider", "value"),
    )
def on_year_change(year,session_state=None):
    global reg_list
    set_emb_list(year)
    #Save year
    session_state['curr_year']=year
    #previous region. Necessary to trigger a refresh of the page
    prev_reg=session_state.get('last_reg', None)
    # Two return to cover cases where the previous region is not in the current year allowed regions
    if prev_reg and prev_reg in reg_list:
        return reg_list,prev_reg
    else:
        return reg_list,reg_list[0]


@app.callback(
    Output("emb-dropdown", "options"),
    Output("emb-dropdown", "value"),
    Input("reg-dropdown","value")
    )
def on_region_change(region,session_state=None):
    global emblist
    set_emb_list(session_state['curr_year'],region=region)
    #register current region
    session_state['last_reg']=region
    #get previous embassy
    last_emb=session_state.get('last_emb',None)
    if last_emb and last_emb in emblist:
        return emblist,last_emb
    else:
        return emblist,emblist[0]     

@app.callback(
    Output("area-graph", "figure"),
    Output("reg-graph", "figure"),
    Output("holes-graph", "figure"),
    Output("historical-graph", "figure"),
    Input("reg-dropdown", "value"),
    )
def display_stats_reg(reg_choice,session_state=None):
    global regional_area_data,regional_bar_data,regional_holes_data,historical_data
    # get current year to display in title 
    curr_year=session_state['curr_year']
    #Area for regions
    in_year_and_region=(regional_area_data['year']==str(curr_year)) & (regional_area_data['region']==reg_choice)
    area_data=regional_area_data[in_year_and_region]    
    fig_area_reg = px.area(area_data, x=area_data.Case_ranges, y=area_data.columns[3:-1],title=f"Status per case-number group ({reg_choice})")
    fig_area_reg.update_layout(margin={"r":0,"t":50,"l":0,"b":50})
    # regional bar chart 
    in_region=regional_bar_data['year']==str(curr_year)
    reg_bar_data=regional_bar_data[in_region]
    fig_reg = px.bar(reg_bar_data, x=reg_bar_data.region, y=reg_bar_data.columns[2:-1], title="Status distribution per region ({})".format(curr_year), barmode='group')    
    fig_reg.update_layout(margin={"r":0,"t":50,"l":0,"b":50}) 
    # Holes chart
    in_year=regional_holes_data['year']==str(curr_year)
    holes_bar_data=regional_holes_data[in_year]
    fig_holes = px.bar(holes_bar_data, y='holes', x='region',text_auto='.2s',title="Holes per region ({})".format(curr_year))
    fig_holes.update_layout(margin={"r":0,"t":50,"l":0,"b":50})
    #load regional historical data
    in_reg=historical_data['region']==reg_choice
    fig_historical=px.line(historical_data[in_reg], x='year', y=historical_data.columns[2:],title="Trends across years ({})".format(reg_choice))
    fig_historical.update_layout(margin={"r":0,"t":50,"l":0,"b":50})
    #save current region
    session_state['last_reg'] = reg_choice
    return fig_area_reg,fig_reg,fig_holes,fig_historical

@app.callback(
    Output("emb-graph", "figure"),
    Output("emb-area-graph", "figure"),
    Output("global-deriv-graph", "figure"),
    Input("emb-dropdown", "value")
    )
def display_stats_emb(emb_choice,session_state=None):
    global consulate_bar_data,consulate_area_data,consulate_global_data
    
    emb_code,emb_choice=emb_choice.split(',')
    #Embassy bar plot
    #get current year and region 
    curr_year=session_state['curr_year']
    reg_choice=session_state['last_reg']
    in_year_and_emb=(consulate_bar_data['year']==str(curr_year)) & (consulate_bar_data['consulate']==emb_choice)
    emb_bar_data=consulate_bar_data[in_year_and_emb]
    emb_bar_data=emb_bar_data[agg_cols].iloc[0]
    emb_bar_data=emb_bar_data.to_frame(name='Count').reset_index()
    emb_bar_data.columns=['Status','Sub category','Count']
    fig_emb = px.bar(emb_bar_data, x="Status", y="Count", color="Sub category", title=f"Selectees at {emb_code}")
    fig_emb.update_layout(margin={"r":0,"t":50,"l":0,"b":50}) 
    #Embassy area plot
    in_year_and_region_and_emb=(consulate_area_data['year']==str(curr_year)) & (consulate_area_data['region']==reg_choice)& (consulate_area_data['consulate']==emb_choice)
    emb_area_data=consulate_area_data[in_year_and_region_and_emb]
    fig_area_emb=px.bar(emb_area_data, x=emb_area_data.Case_ranges, y=emb_area_data.columns[4:-1],title=f"Status per case-number group ({emb_choice})")
    fig_area_emb.update_layout(margin={"r":0,"t":50,"l":0,"b":50})     
    #Embassy  global plot
    in_year=(consulate_global_data['year']==str(curr_year))
    global_data=consulate_global_data[in_year]
    fig_global = px.choropleth(global_data, locations="iso_alpha",color="Iss.Deriv.avg",hover_name="country")
    fig_global.update_layout(margin={"r":0,"t":30,"l":0,"b":0}, title={'text':"Global derivatives distribution",'x': 0.5,})
    #save current embassy
    session_state["last_emb"]= emb_code+','+ emb_choice
    return fig_emb,fig_area_emb,fig_global
    
  
if __name__ == "__main__":
    app.run_server(debug=True)
