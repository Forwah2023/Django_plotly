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
#hold current ceac data
ceac=""
# hold ceac data grouped by regions, holes and consul
Grouped_regions=""
Grouped_holes=""
Grouped_consul=""
#hold current ceac region and corresponding embassy list
emblist=""
reg_list=""
default_yr=2023

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
left_row_1=dbc.Row(dbc.Col(html.P(children="Select Region below (or year from the adjacent slider)",style=style_text) ))
left_row_2=dbc.Row(dbc.Col(dcc.RadioItems([],"",id="reg-dropdown",inline=True,style=style_text)))
left_row_3=dbc.Row([
                        dbc.Col(html.Div(dcc.Graph(id="area-graph"), id='top_right_div1'),lg=6),
                        dbc.Col(html.Div(dcc.Graph(id="reg-graph"),id='top_right_div2'),lg=6)                 
                    ]
     
            )
left_row_4=dbc.Row(dbc.Col(html.Div([dcc.Graph(id="holes-graph")])))            
left_row_5=dbc.Row( html.P(children="Select embassy :",style=style_text),justify="center")

left_row_6=dbc.Row( dcc.Dropdown([],"",id="emb-dropdown",style=style_dropdown ))
left_row_7=dbc.Row([
                        dbc.Col(html.Div([dcc.Graph(id="emb-graph")]),lg=6),
                        dbc.Col(html.Div([dcc.Graph(id="emb-area-graph")]),lg=6)   
                    ]
            )
left_row_8=dbc.Row(dbc.Col(html.Div([dcc.Graph(id="global-deriv-graph")])))


about_tab=dbc.Row(dbc.Col(
        html.Div([
        html.H4("About this App "),
        html.P(["This Dash app was built to provide detailed and complementary information on the DV-lottery program run by the U.S governmwent.\
        It was inspired by a similar app from ",html.A('DV Lottery Charts', href='https://dvcharts.xarthisius.xyz/ceacFY24.html'), ",and the data\
        is uses comes from that website. This app complements that website by providing more information on Holes (see glossary below), \
        Global derivative distribution, comparative performance across DV-years, and more comple visualizations. This app was built using ",\
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
            html.Li([html.B("avg_der( Average Derivative) : "), " Average derivative per case."]),
            html.Li([html.B(" Sum : "), " The total number of cases in each category including derivatives."]),         
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
                                left_row_8
                                ],xs={"size":11,"order":2,"offset":0},lg={"size":11,"order":1,"offset":0}
                               ),
                        dbc.Col(right_row_0,xs={"size":1,"order":1,"offset":10},lg={"size":1,"order":2,"offset":0}
                               )                                
                        ]
                ),fluid=True
            )
            
sources_tab=dbc.Row(dbc.Col(
                        html.Div([
                                dbc.Button("GitHub", href='', color="primary", target="_blank")
                                 ]
                        ),
                        width={"size": 6, "offset": 2}, class_name="mt-5"
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
def set_emb_list(region):
    # set emabssy dropdown options
    bool_select=ceac['region']==region
    emblist=sorted(ceac[bool_select]['consulate'].dropna().unique())
    return emblist
#Initialization
def initialization(year):
    global  ceac,Grouped_regions,Grouped_holes,Grouped_consul,emblist,reg_list
    ceac= pd.read_pickle(f'ceac_pkl/cleaned_Ceac_{str(year)}.pkl')
    # Region-specific stats
    Grouped_regions=ceac.groupby(['region'],observed=True)[agg_cols].agg(['sum',cases])
    Grouped_regions.dropna(inplace=True)
    level0 =Grouped_regions.columns.get_level_values(0)
    level1 =Grouped_regions.columns.get_level_values(1)
    Grouped_regions.columns=['Iss','Iss_C','Ref','Ref_C','221g','221g_C','Rdy','Rdy_C','NVC','NVC_C','AP','AP_C']  # Enable for full lables =level0 + '_' + level1
    # Holes count
    Grouped_holes=ceac.groupby(['region'],observed=True)['status'].agg([holes]).reset_index()
    #Embassy-specific stats
    Grouped_consul=ceac.groupby(['consulate'])[agg_cols].agg(['sum',cases])
    Grouped_consul.dropna(inplace=True)
    #List of available regions embassies
    reg_list=ceac['region'].dropna().unique()
    emblist=set_emb_list(reg_list[0])

@app.callback(
    Output("reg-dropdown","options"),
    Output("reg-dropdown","value"),
    Input("year-slider", "value"),
    )
def on_year_change(year,session_state=None):
    global reg_list
    initialization(year)
    #previous region. Necessary to trigger a refresh of the page
    prev_reg=session_state.get('last_reg',reg_list[0])################################change reg_list[0] to None
    # Two return to cover cases where the previous region is not in the current year allowed regions
    if prev_reg in reg_list:
        return reg_list,prev_reg
    else:
        return reg_list,reg_list[0]


@app.callback(
    Output("emb-dropdown", "options"),
    Output("emb-dropdown", "value"),
    Input("reg-dropdown","value")
    )
def on_region_change(region,session_state=None):
    emblist=set_emb_list(region)
    first_emb=emblist[0]
    return emblist,first_emb      

@app.callback(
    Output("area-graph", "figure"),
    Output("reg-graph", "figure"),
    Output("holes-graph", "figure"),
    Input("reg-dropdown", "value"),
    )
def display_stats_reg(reg_choice,session_state=None):
    #Area and bar chart for regions
    Grouped_area_df_reg=prepare_area_plot_data_reg(reg_choice)
    fig_area_reg = px.area(Grouped_area_df_reg, x=Grouped_area_df_reg.index, y=Grouped_area_df_reg.columns,title=f"Status distribution across case numbers ({reg_choice})")
    fig_area_reg.update_layout(margin={"r":0,"t":50,"l":0,"b":50}) 
    fig_reg = px.bar(Grouped_regions, x=Grouped_regions.index, y=Grouped_regions.columns, title="Regional statistics", barmode='group')    
    fig_reg.update_layout(margin={"r":0,"t":50,"l":0,"b":50}) 
    # Holes chart
    fig_holes = px.pie(Grouped_holes, values='holes', names='region',title="Holes distribution across regions")
    #save current region
    session_state['last_reg'] = reg_choice
    return fig_area_reg,fig_reg,fig_holes

@app.callback(
    Output("emb-graph", "figure"),
    Output("emb-area-graph", "figure"),
    Output("global-deriv-graph", "figure"),
    Input("emb-dropdown", "value")
    )
def display_stats_emb(emb_choice,session_state=None):
    Grouped_sub_ceac_emb=prepare_area_plot_data_emb(emb_choice)
    fig_area_emb=px.area(Grouped_sub_ceac_emb, x=Grouped_sub_ceac_emb.index, y=Grouped_sub_ceac_emb.columns,title=f"Status distribution across case numbers ({emb_choice})")
    fig_area_emb.update_layout(margin={"r":0,"t":50,"l":0,"b":50}) 
    #Embassy plots
    try:
        emb=Grouped_consul.loc[emb_choice]
    except KeyError:
        print('Embassy data not found')
        return
    emb=emb.to_frame(name='Count').reset_index()
    emb.columns=['Status','Sub category','Count']
    fig_emb = px.bar(emb, x="Status", y="Count", color="Sub category", title=f"Embassy statistics ({emb_choice})")
    fig_emb.update_layout(margin={"r":0,"t":50,"l":0,"b":50}) 
    Global_derivative=prepare_global_derivative()
    fig_global = px.choropleth(Global_derivative, locations="iso_alpha",color="Issued avg_der",hover_name="country")
    fig_global.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    #save current embassy
    session_state["last_emb"]=emb_choice
    return fig_emb,fig_area_emb,fig_global

def prepare_area_plot_data_reg(reg_choice):
    # select regional subset
    in_region=ceac['region']==reg_choice
    sub_ceac_reg=ceac[in_region]
    # select and cut case numbers into bins
    case_num=sub_ceac_reg['caseNumber'].astype(np.int64)
    maxcase_reg=round(case_num.max(),-3)
    num_bins_reg=round(maxcase_reg/1000)
    case_ranges_reg=pd.cut(case_num,num_bins_reg)
    sub_ceac_reg.insert(1,'Case_ranges',case_ranges_reg)
    # group by case ranges
    Grouped_sub_ceac_reg=sub_ceac_reg.groupby(['Case_ranges'],observed=True).agg(agg_dict)
    level0 =Grouped_sub_ceac_reg.columns.get_level_values(0)
    level1 =Grouped_sub_ceac_reg.columns.get_level_values(1)
    Grouped_sub_ceac_reg.columns =short_legend_lable  # Enable for full lables =level0 + '_' + level1 
    Grouped_sub_ceac_reg.index=Grouped_sub_ceac_reg.index.astype('str') 
    
    
    return Grouped_sub_ceac_reg

def prepare_area_plot_data_emb(emb_choice):
    # select embassy subset
    in_emb=ceac['consulate']==emb_choice
    sub_ceac_emb=ceac[in_emb]
    # select and cut case numbers into bins
    case_num_emb=sub_ceac_emb['caseNumber'].astype(np.int64)
    maxcase_emb=round( case_num_emb.max(),-3)
    num_bins=round(maxcase_emb/1000)
    case_ranges_emb=pd.cut(case_num_emb,num_bins)
    sub_ceac_emb.insert(1,'Case_ranges',case_ranges_emb)
    
    Grouped_sub_ceac_emb=sub_ceac_emb.groupby(['Case_ranges'],observed=True).agg(agg_dict)
    level0 =Grouped_sub_ceac_emb.columns.get_level_values(0)
    level1 =Grouped_sub_ceac_emb.columns.get_level_values(1)
    Grouped_sub_ceac_emb.columns =short_legend_lable # Enable for full legend lables =level0 + '_' + level1  
    Grouped_sub_ceac_emb.index=Grouped_sub_ceac_emb.index.astype('str')
    return Grouped_sub_ceac_emb    

def prepare_global_derivative():
    agg_cols=['Issued']
    Grouped_consul=ceac.groupby(['consulate'],observed=True)[agg_cols].agg([avg_der])
    Grouped_consul.columns=Grouped_consul.columns.get_level_values(0)+' '+Grouped_consul.columns.get_level_values(1)
    Grouped_consul=Grouped_consul.reset_index()
    Global_derivative=Grouped_consul.merge(ISO_country_df,how='left',on='consulate')
    return Global_derivative

  
if __name__ == "__main__":
    app.run_server(debug=True)
