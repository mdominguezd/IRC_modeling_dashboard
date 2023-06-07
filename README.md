# Indoor Radon Concentrations Modeling Dashboard (IRCMod)

**Created by:** [**Martín Domínguez Durán**](https://www.martindominguezduran.com/)

This repository includes the necessary code to run the Indoor Radon Concentrations Modeling dashboard (**IRCmod**) locally in your own machine. This dashboard was elaborated to model the radon concentrations in the city of Bogotá, Colombia using a log-linear regression model. By making the repository public, we encourage researchers to use it for other cities in which radon measurements is scarce. A web version of the app can be accessed [**here**](http:/ircmodelingdashboard.eu.pythonanywhere.com), however, due to the remote server limitations it cannot handle large datasets.

## Installation
To run the dashboard locall you will need to intall all of the python packages that are contained in `requirements.txt`. To do so we suggest to use *Anaconda prompt* that can be downloaded [**here**](https://www.anaconda.com/download).

Once downloaded, open the *Anaconda prompt* and type the following commands (You can replace the name of your conda environment as you wish).


    conda create -n YOUR_ENVIRONMENT python=3.9
    conda activate YOUR_ENVIRONMENT
    conda install pip
    pip install -r requirements.txt
    
    python IRCmod_app.py
   
After running the final line you should get a message with the location of the local serve in which the app is running. This should be: `http://127.0.0.1:8050/`.

## How to use

The IRCmod dashboard requires to tables as input.

1. A table that will be used for the fitting of the log-linear model.
    * This table should include a column with the radon measurements named **RC** and several columns with the explanatory variables selected to model RC as shown below.
    * An example of this table can be accessed [**here**](https://github.com/mdominguezd/RnSurvey_Bogota_DataAnalysis/blob/main/Dataset%20for%20fitting/Processed_DataFrame.csv)

| RC | var_1 | var_2 | ... | var_n |
| -- | -- | -- | -- | -- |
|val_RC1 | val_var_1 | val_var_2 | ... | val_var_n |

2. A table with the **cadaster information** that will be used for applying the model to the rest of the houses in the specific place.
    * This table should include the same columns with the information of the explanatory variables and two extra columns with **X** and **Y** coordinates in a known **Projected** (Info. on projections [**here**](https://www.esri.com/arcgis-blog/products/arcgis-pro/mapping/gcs_vs_pcs/#:~:text=What%20is%20the%20difference%20between,map%20or%20a%20computer%20screen.)) Coordinate Reference System (CRS). The table should follow th structure shown below.
    * An example of this table can be accessed [**here**](https://github.com/mdominguezd/RnSurvey_Bogota_DataAnalysis/blob/main/Dataset%20for%20regression/Houses_for_Rn_estimation_processed_3116.txt)

|  var_1 | var_2 | ... | var_n | X | Y |
| -- | -- | -- | -- | -- | -- |
| val_var_1 | val_var_2 | ... | val_var_n | val_X | val_Y |
    
Once the two tables have been uploaded to the dashboard, you now may continue to the second block of the dashboard. There, you can compare yout measurments with recommendation levels and select the features to be used in the regression according to the information provided by the correlation matrix and/or the variance inflation factor.

Once you have selected the features you can now run the model. Nevertheless, if your study area is outside of Colombia you will need to change the Coordinate Reference System to the one used in the table with the cadaster information.

When you have run the model you will get two main results. A map of the study area with the concentrations modeled and two tables with the statistical results of the log-linear regression.



