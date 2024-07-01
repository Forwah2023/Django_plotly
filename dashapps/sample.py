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
    
def avg_derivative(s):
    try:
        return (sum(s)/sum(s>=1))-1
    except ZeroDivisionError:
        return 0

#aggregation cols
agg_cols=['Issued','Refused','Refused221g','Ready','NVC','InTransit','Transfer','AP']

# ISO country data
ISO_country_df=pd.read_pickle('ISO_ALPHA.pkl')

# Aggregation dictionary for area plot totals
agg_dict = {'status':[holes],
            'Issued':[cases],
            'Refused':[cases],
            'Refused221g':[cases],
            'Ready':[cases],
            'NVC':[cases],
            'InTransit':[cases],
            'Transfer':[cases],
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
left_row_1=dbc.Row(dbc.Col(html.P(children="Select Region:",style=style_text) ))
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

app.layout =dbc.Container(
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
    Grouped_regions.columns=level0 + '_' + level1
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
    prev_reg=session_state.get('last_reg',reg_list[0])
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
    fig_global = px.choropleth(Global_derivative, locations="iso_alpha",color="Issued avg_derivative",hover_name="country")
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
    Grouped_sub_ceac_reg.columns = level0 + '_' + level1
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
    Grouped_sub_ceac_emb.columns = level0 + '_' + level1
    Grouped_sub_ceac_emb.index=Grouped_sub_ceac_emb.index.astype('str')
    return Grouped_sub_ceac_emb    

def prepare_global_derivative():
    agg_cols=['Issued']
    Grouped_consul=ceac.groupby(['consulate'],observed=True)[agg_cols].agg([avg_derivative])
    Grouped_consul.columns=Grouped_consul.columns.get_level_values(0)+' '+Grouped_consul.columns.get_level_values(1)
    Grouped_consul=Grouped_consul.reset_index()
    Global_derivative=Grouped_consul.merge(ISO_country_df,how='left',on='consulate')
    return Global_derivative

  
if __name__ == "__main__":
    app.run_server(debug=True)
