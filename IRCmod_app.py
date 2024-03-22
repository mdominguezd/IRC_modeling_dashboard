import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import dash
from dash import Dash, dcc, html, callback, callback_context
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.figure_factory as ff
import dash_daq as daq
from dash.exceptions import PreventUpdate
from dash import dash_table
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import geopandas as gpd
from shapely.geometry import Polygon
from os import path, remove, listdir
import re
import warnings
import sys
from statsmodels.stats.outliers_influence import variance_inflation_factor
import statsmodels.api as sm
from sklearn.ensemble import RandomForestRegressor as RFR
import base64
import io
from Functions import RnProcessing_Functions as RP
from Functions import Visualization_Functions as VIS
from App import Layout
warnings.filterwarnings('ignore')

app = Dash(__name__, external_stylesheets=[dbc.themes.MORPH, dbc.icons.BOOTSTRAP])
server = app.server
load_figure_template(["morph"])

app.title = 'IRC modeling app'

app.layout = Layout.layout

@app.callback([Output('uploaded1', 'children')],
              [Input('upload-data-f', 'contents')])
def update_uploaded_data(list_of_contents):
    if list_of_contents is not None:
        return [[html.I(className="bi-bookmark-check"), html.B('Data uploaded.')]]
    else:
        return [['Drag and Drop or ', html.B('Select Files for fitting the model (in-situ measurements)')]]
    
@app.callback([Output('uploaded2', 'children')],
              [Input('upload-data-r', 'contents')])
def update_uploaded_data(list_of_contents):
    if list_of_contents is not None:
        return [[html.I(className="bi-bookmark-check"), html.B('Data uploaded.')]]
    else:
        return [['Drag and Drop or ',
                                                                                   html.B('Select Files for applying the model (Cadaster information)')]]
                                
@app.callback(
    [Output('RC-histogram', 'figure'), Output('vars_', 'options')],
    [Input('Organization', 'value'), Input('upload-data-f','contents')])
def update_RC_distribution(Organization, list_of_contents):
        
    if list_of_contents is not None:
        
        # Read data
        cont = list_of_contents.split(',')[1]
        decoded = base64.b64decode(cont)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        
        # Create figure of radon measurements distribution
        fig = VIS.plot_RC_dist(Organization, df)
        
        # Clean variable names (Remove ID, RC, radon)
        df = df.T[df.apply(lambda df: ('ID' not in df.name) and ('RC' not in df.name) and ('Radon' not in df.name))].T     
        var_names = list(df.columns)
        
    else:
        
        df = pd.read_csv('https://raw.githubusercontent.com/mdominguezd/RnSurvey_Bogota_DataAnalysis/main/Dataset%20for%20fitting/Processed_DataFrame.csv')
        
        # Create figure of radon measurements distribution
        fig = VIS.plot_RC_dist(Organization, df)

        df = df.T[df.apply(lambda df: ('ID' not in df.name) and ('RC' not in df.name) and ('Radon' not in df.name))].T   
        
        var_names = list(df.columns)
    
    return fig, var_names


@app.callback(
    Output('FS_out', 'figure'),
    [Input('FS','value'), Input('upload-data-f','contents')]
)
def feature_sel(info_FS, list_of_contents):
    if list_of_contents is not None:
        
        # Read data
        cont = list_of_contents.split(',')[1]
        decoded = base64.b64decode(cont)
        DF_RC = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        
        # Create figure that can be used for feature selection
        fig = VIS.plot_feature_sel(DF_RC, info_FS)


        fig.update_layout(title_text = 'Information for feature selection', 
                          title_font_family = 'bahnschrift',
                          font_family = 'bahnschrift')
    else:
        
        DF_RC = pd.read_csv('https://raw.githubusercontent.com/mdominguezd/RnSurvey_Bogota_DataAnalysis/main/Dataset%20for%20fitting/Processed_DataFrame.csv')
        
        # Create figure that can be used for feature selection
        fig = VIS.plot_feature_sel(DF_RC, info_FS)


        fig.update_layout(title_text = 'Information for feature selection', 
                          title_font_family = 'bahnschrift',
                          font_family = 'bahnschrift')
            
    return fig
    

lst_clicks_mp = []

@app.callback(
    [Output('RC-model-map', 'figure'),Output('imp', 'data'),Output('RMSE', 'data')],
    [Input('Predict_Rn','n_clicks'),Input('model', 'value'), Input('vars_','value'), Input('HQ_model','on'), Input('upload-data-f', 'contents'), Input('upload-data-r', 'contents'), Input('EPSG', 'value')]
)

def update_map(Predict_Rn, model, vars_, HQ, DF_RC_c, df_RnModel_c, crs):
    
    if df_RnModel_c is not None:
    
        lst_clicks_mp.append(Predict_Rn)

        if (Predict_Rn == 0):
            df = pd.DataFrame([[0,-72]])
            df_ = pd.DataFrame(['  '])
            df_.columns = [' ']
            imp = df_.to_dict('records')
            RMSE = imp
            fig = px.scatter_mapbox(df, lat = 0, lon = 1, opacity = 0)

            fig.update_traces(hoverinfo = 'skip', hovertemplate = " ")
            fig.update_layout(mapbox_style="carto-positron",
                              mapbox_zoom = 1.5)

        elif (lst_clicks_mp[-1] == lst_clicks_mp[-2]):
            raise PreventUpdate

        elif (lst_clicks_mp[-1] > lst_clicks_mp[-2]):
            if DF_RC_c is not None:

                cont = DF_RC_c.split(',')[1]

                decoded = base64.b64decode(cont)

                DF_RC = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

            if df_RnModel_c is not None:

                cont = df_RnModel_c.split(',')[1]

                decoded = base64.b64decode(cont)

                df_RnModel = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

            if  HQ:    
                X, y, msg = RP.read_data(vars_, DF_RC)
                print(msg)
                imp, RMSE, mod, msg = RP.fit_model(X,y,HQ, model = model)
                print(msg)
                rc_pol, x_c, y_c, n, msg = RP.apply_model(mod, model, X, HQ, df_RnModel, crs, res=100)
                print(msg)
            else:
                X, y, msg = RP.read_data(vars_, DF_RC)
                print(msg)
                imp, RMSE, mod, msg = RP.fit_model(X, y, HQ, model = model)
                print(msg)
                rc_pol, x_c, y_c, n, msg = RP.apply_model(mod, model, X, HQ, df_RnModel, crs)
                print(msg)

            fig = ff.create_hexbin_mapbox(data_frame=rc_pol,
                                          lat="Y", 
                                          lon="X",
                                          nx_hexagon=n,
                                          opacity=0.65,
                                          min_count = 1,
                                          labels={"color": "RC"},
                                          color="RC",
                                          agg_func=np.mean,
                                          color_continuous_midpoint=100,
                                          color_continuous_scale="Portland")

            fig.update_traces(marker_line_width = 0, hoverinfo = 'z')

            fig.update_layout(mapbox_style="carto-positron",
                              mapbox_center = {'lat':y_c, 'lon':x_c},
                              mapbox_zoom = 10)
            
    else:
        
        lst_clicks_mp.append(Predict_Rn)

        if (Predict_Rn == 0):
            df = pd.DataFrame([[0,-72]])
            df_ = pd.DataFrame(['  '])
            df_.columns = [' ']
            imp = df_.to_dict('records')
            RMSE = imp
            fig = px.scatter_mapbox(df, lat = 0, lon = 1, opacity = 0)

            fig.update_traces(hoverinfo = 'skip', hovertemplate = " ")
            fig.update_layout(mapbox_style="carto-positron",
                              mapbox_zoom = 1.5)

        elif (lst_clicks_mp[-1] == lst_clicks_mp[-2]):
            raise PreventUpdate

        elif (lst_clicks_mp[-1] > lst_clicks_mp[-2]):

            DF_RC = pd.read_csv('https://raw.githubusercontent.com/mdominguezd/RnSurvey_Bogota_DataAnalysis/main/Dataset%20for%20fitting/Processed_DataFrame.csv')

            df_RnModel = pd.read_csv('https://raw.githubusercontent.com/mdominguezd/RnSurvey_Bogota_DataAnalysis/main/Dataset%20for%20regression/Aggregated_Dataset_Bog.csv')

            if  HQ:    
                X, y, msg = RP.read_data(vars_, DF_RC)
                print(msg)
                imp, RMSE, mod, msg = RP.fit_model(X,y,HQ, model = model)
                print(msg)
                rc_pol, x_c, y_c, n, msg = RP.apply_model(mod, model, X, HQ, df_RnModel, crs, res=100)
                print(msg)
            else:
                X, y, msg = RP.read_data(vars_, DF_RC)
                print(msg)
                imp, RMSE, mod, msg = RP.fit_model(X, y, HQ, model = model)
                print(msg)
                rc_pol, x_c, y_c, n, msg = RP.apply_model(mod, model, X, HQ, df_RnModel, crs)
                print(msg)

            fig = ff.create_hexbin_mapbox(data_frame=rc_pol,
                                          lat="Y", 
                                          lon="X",
                                          nx_hexagon=n,
                                          opacity=0.65,
                                          min_count = 1,
                                          labels={"color": "RC"},
                                          color="RC",
                                          agg_func=np.mean,
                                          color_continuous_midpoint=100,
                                          color_continuous_scale="Portland")

            fig.update_traces(marker_line_width = 0, hoverinfo = 'z')

            fig.update_layout(mapbox_style="carto-positron",
                              mapbox_center = {'lat':y_c, 'lon':x_c},
                              mapbox_zoom = 10)
    
    
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        
    return fig, imp, RMSE

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader = False)
    
