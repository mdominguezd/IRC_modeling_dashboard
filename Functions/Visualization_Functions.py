import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor



def plot_RC_dist(Organization, DF_RC):
    """ plotFigure

        Objective: Plot radon concentration distribution and pie plot with percentage of concentrations above some reference level
        
        Input: 
            - Organization: Which reference level to compare it with (WHO or EPA)
            - DF_RC: Dataframe with dependent and independent variables.
        Output:
            - fig: Plotly figure with Radon distribution and pie plot.
            - DF_data: Dataset with a column of exceedence
    """ 
    DF_data = pd.DataFrame(DF_RC['RC'])

    DF_data['Exceed WHO'] = DF_data.RC.apply(lambda df :'Above WHO recommended level' if  (df >100) else 'Below WHO recmmended level')
    DF_data['Exceed EPA'] = DF_data.RC.apply(lambda df :'Above EPA action level' if  (df >148) else 'Below EPA action level')
    
    RC_max = np.max(DF_data['RC'])
    
    x = np.arange(0,(RC_max - RC_max%25) + 26,25)
    rc = DF_data['RC']
    y = np.histogram(rc, bins = x)

    hist = px.histogram(DF_data, x = 'RC', range_x = [0,(RC_max - RC_max%25) + 25])

    fig = make_subplots(specs=[[{'secondary_y': True}, {"type": "pie"}]],
                      cols = 2)

    fig.update_layout(template = 'morph');

    fig.add_trace(
        go.Histogram(x=hist.data[0].x,
               y=hist.data[0].y,
               name="Percentage of<br>RC measurements", 
               histnorm = 'percent', marker_color = 'rgb(55,100,200)',
               hoverinfo = 'x+y',
              ), secondary_y=False)
    
    ref_levs = [100,148]
    
    if Organization[-3:] == 'WHO':
        fig.add_vline(ref_levs[0], annotation_text = Organization[-3:] + ' recommended level',
                      annotation_position = 'top',
                      line_dash="dash", row = 1, col =1)
    else:
        fig.add_vline(ref_levs[1], annotation_text = Organization[-3:] + ' recommended level',
                      annotation_position = 'top',
                      line_dash="dash", row = 1, col =1)

    fig.update_traces(xbins=dict( # bins used for histogram
            start=0.0,
            end=425.0,
            size=25
            ))
    
    fig.update_xaxes(range = [0, max(rc) + max(rc)*0.05])

    fig.add_trace(
        go.Scatter(x = (x[1:]),
                   y = np.round(100*np.cumsum(y[0]/30),2),
                   name="Accumulated<br>percentage of<br>RC measurements",
                   line_color="#ee0000", hoverinfo="x+y"), secondary_y=True)

    fig.update_layout(title_text = 'Residential RC measurements distribution', 
                      title_font_family = 'bahnschrift',
                      font_family = 'bahnschrift',
                      title_font_size = 30, xaxis_title_text='Residential RC [Bq/m^3]', # xaxis label
                      yaxis_title_text='Percentage of RC measurements' # yaxis label
                     )

    labels = DF_data.groupby(Organization).count().iloc[:,0].index
    values = DF_data.groupby(Organization).count().iloc[:,0].values

    fig.add_trace(go.Pie(labels = labels,
                         values = values,
                         textinfo = 'percent',
                         hoverinfo = 'label+value', 
                         marker = dict(colors = ['rgb(255,0,0)', 'rgb(55,100,200)']),
                         showlegend = False,
                         title = 'Comparison with ' + Organization[-3:] + ' recommedation',
                         titleposition = 'bottom center',
                         titlefont = dict(size = 20)
                        ),
                  row = 1, col = 2 
                 )


    fig.update_layout(title_font_size = 30)
    
    return fig

def plot_feature_sel(DF_RC, fig_type):

    if fig_type == 'Correlation matrix':
        
        cor = DF_RC.corr().iloc[1:,1:]

        for i in range(len(cor)):
            for j in range(len(cor)):
                if i < j:
                    cor.iloc[i,j] = np.nan

        fig = px.imshow(cor, color_continuous_scale='RdBu_r', zmin = -1, zmax = 1)

        fig.update_traces(hoverinfo = 'z', hovertemplate = "r_pearson: %{z:.2f}")

    elif fig_type == 'Variance Inflation Factor':

        X = DF_RC.iloc[:,2:]
        X = sm.add_constant(X)

        tab = pd.DataFrame()
        tab["Features"] = X.columns[1:]
        tab["VIF Factor"] = [round(variance_inflation_factor(X.values, i+1),2) for i in range(X.shape[1]-1)]
        VIF_vars = list(tab[tab['VIF Factor'] < 4]['Features'])
        tab = tab.sort_values(by = 'VIF Factor', ascending = False)
        tab=tab.set_index('Features')

        fig = px.imshow(tab, color_continuous_scale='RdBu_r', zmax = 4, zmin = 0)
        fig.update_coloraxes(showscale=False)
        fig.update_traces(hoverinfo = 'z', hovertemplate = "VIF: %{z:.2f}")
        
    return fig