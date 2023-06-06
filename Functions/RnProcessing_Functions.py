import statsmodels.api as sm
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor as RFR
from shapely.geometry import Polygon
import geopandas as gpd


def read_data(variables, DF_RC):
    """ READ_DATA

        Objective: Read the dataframes and variables to consider and return prdictors and dependent variable seperated.
        
        Input: 
            - Variables: List with names of the variables to be considered in analysis
            - DF_RC: Dataframe with dependent and independent variables.
        Output:
            - X: Predictors (Ind. vars.)
            - y: Predicted varaiable (Dep. var.)
            - msg: Message with information of the process.
    """ 
    
    X = DF_RC[variables]
    y = DF_RC['RC']

    X = sm.add_constant(X)
    
    msg = 'Reading data...'
    
    return X, y, msg


def fit_model(X, y, HQ, model = 'Log_Linear'):
    """ FIT_MODEL

        Objective: Take X, y and the type of model and fits the data to the given model.
        
        Input: 
            - X: Predictors (Ind. vars.)
            - y: Predicted varaiable (Dep. var.)
            - HQ: Boolean. True if a High Quality result is wanted. False if HQ is not required.
            - model: Model to be fitted (Options are Log_linear or Random_Forest)
        Output:
            - importance: Either a table with weights and p-values estimated (Log_linear) or feature importances (Random Forest)
            - RMSE: Root Mean Squared Error calculated using the Leav On Out Crooss-Validation Approach.
            - mod: Model fitted
            - name_file: Name of he file to be saved if it doesn't exist.
            - msg: Message with information of the process.
    """ 
    variables = list(X.columns)[1:]
    
    var_ID = ''
    for i in variables:
        var_ID += i[0]
    
    if model == 'Log_Linear':
        lin_reg = sm.OLS(np.log(y), X).fit(maxiter=1000)
        mod = lin_reg
        importance = lin_reg.params
        pval = lin_reg.pvalues
        importance = pd.DataFrame(importance[1:])
        importance['Features'] = variables
        importance['p'] = pval
        importance.columns = ['Weight', 'Features','p_value']
        importance = importance[['Features', 'Weight', 'p_value']]
        importance['Weight'] = importance['Weight'].apply(lambda df : round(df,2))
        importance['p_value'] = importance['p_value'].apply(lambda df : round(df,2))
        
        # CROSS VALIDATION SCORE 
        df = pd.concat([X, np.log(y)], axis = 1)
        errors = []

        # LOOCV
        for i in range(len(df)):

            # splitting our dataset into train and test datasets.
            train = pd.concat([df.iloc[:i], df.iloc[(i+1):]])
            test = pd.DataFrame(df.iloc[i]).T
            lin_reg = sm.OLS(train.RC, train.iloc[:,:-1]).fit(maxiter=1000000)

            RMSE = np.sqrt(np.sum((np.exp(lin_reg.predict(test.iloc[:,:-1])) - np.exp(test.RC))**2)/1)
            errors.append(RMSE)
        
        RMSE = np.mean(errors)
        RMSE = pd.DataFrame([np.round(RMSE,2)])
        RMSE.columns = ['RMSE']
        
    elif model == 'Random_Forest': 
        RF_reg = RFR().fit(X, y)
        mod = RF_reg
        importance = RF_reg.feature_importances_
        importance = pd.DataFrame(importance[1:])
        importance['Features'] = variables
        importance.columns = ['Importance', 'Features']
        importance = importance[['Features', 'Importance']]
        importance['Importance'] = importance.Importance.apply(lambda df : round(df,2))
        
        # CROSS VALIDATION SCORE 
        df = pd.concat([X, y], axis = 1)
        errors = []

        # LOOCV
        for i in range(len(df)):

            # splitting our dataset into train and test datasets.
            train = pd.concat([df.iloc[:i, 1:], df.iloc[(i+1):, 1:]])
            test = pd.DataFrame(df.iloc[i]).T
            RF = RFR().fit(train.iloc[:,:-1], train.RC)

            RMSE = np.sqrt(np.sum((RF.predict(test.iloc[:,1:-1]) - test.RC)**2)/1)
            errors.append(RMSE)
        
        RMSE = np.mean(errors)
        RMSE = pd.DataFrame([RMSE])
        RMSE.columns = ['RMSE']
        
    importance = importance.to_dict('records')
    
    RMSE = RMSE.to_dict('records')
        
    msg = 'Fitting model...\nEstimating RC values...\n\nThis will take some time...\n\n'
        
    return importance, RMSE, mod, msg

def apply_model(mod,
                model,
                X,
                HQ,
                df_RnModel,
                crs = '3116',
                res = 300,
               ):
    """ apply_model

        Objective: Apply fitted model to the household dataset.
        
        Input: 
            - mod: Model fitted
            - model: Model to be fitted (Options are Log_linear or Random_Forest)
            - X: Predictors (Ind. vars.)
            - HQ: Boolean. True if a High Quality result is wanted. False if HQ is not required.
            - df_RnModel: Dataset to which the model is applied.
            - crs. Coordinate system EPSG (string)
            - res: Spatial resolution in meters.
        Output:
            - grid: Grid with the results of predicted Rn values.
            - x_c: centroid X coordinate
            - y_c: centroid Y coordinate
            - msg: Message with information of the process.
    """ 
    
    df_RnModel['const'] = np.ones(len(df_RnModel))

    x_range = df_RnModel['X'].max() - df_RnModel['X'].min()
    y_range = df_RnModel['Y'].max() - df_RnModel['Y'].min()

    df_RnModel['Cluster'] = np.zeros(len(df_RnModel))

    cols = np.arange(df_RnModel['X'].min() + res/2, df_RnModel['X'].max(), res)
    rows = np.arange(df_RnModel['Y'].min() + res/2, df_RnModel['Y'].max(), res)

    k = 0
    polygons = []
    
    for i in range(len(cols)-1):

        for j in range(len(rows)-1):

            k += 1
            df_RnModel.loc[(df_RnModel.X >= cols[i])&(df_RnModel.X < cols[i+1])&(df_RnModel['Y'] >= rows[j])&(df_RnModel['Y'] < rows[j+1]), 'Cluster'] = k
            polygons.append(Polygon([(cols[i],rows[j]),
                                     (cols[i]+res, rows[j]), 
                                     (cols[i]+res, rows[j]+res), 
                                     (cols[i], rows[j]+res)]))    

    df_RnModel = df_RnModel.groupby('Cluster').mean()

    df_RnModel_reg = df_RnModel[list(X.columns)]

    if model == 'Log_Linear':
        df_RnModel['RC'] = np.exp(mod.predict(df_RnModel_reg))
    elif model == 'Random_Forest':
        df_RnModel['RC'] = mod.predict(df_RnModel_reg)

    gdf = gpd.GeoDataFrame(df_RnModel['RC'], geometry=gpd.points_from_xy(df_RnModel.X, df_RnModel.Y))
    gdf = gdf.set_crs('EPSG:'+crs)
    gdf = gdf.to_crs('EPSG:4326')
    grid = gpd.GeoDataFrame({'geometry':polygons})
    grid = grid.set_crs('EPSG:'+crs)
    grid = grid.to_crs('EPSG:4326')
    grid = gpd.sjoin(grid, gdf)
    
    msg = 'Done :)'
    
    x_c = grid.dissolve().centroid.x.mean()
    y_c = grid.dissolve().centroid.y.mean()

    return grid, x_c, y_c, msg