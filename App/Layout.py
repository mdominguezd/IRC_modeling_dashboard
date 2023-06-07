import dash
from dash import Dash, dcc, html, callback, callback_context
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import dash_table

color = 'lightsteelblue'

layout = html.Div([html.Div([html.Div([],style = {'width':'0.5%'}), html.H1('Indoor Radon Concentrations (IRC) modeling app', style={'font-family' : 'bahnschrift'})], 
                            style = {'display':'flex', 'width' : '100%', 'margin' : 'auto'}),
                   html.Div([''], style = {'height':20, 'background-color':color, 'width' : '100%', 'margin' : 'auto'}),
                       html.Div([html.H5('Upload here your datasets before you continue',
                                         style={'font-family' : 'bahnschrift'}),
                                 html.Div([html.Div([dcc.Upload(id='upload-data-f',
                                                                children=html.Div(id = 'uploaded1'),
                                                                style={'width': '100%',
                                                                       'height': 'auto',
                                                                       'minHeight' : '40px',
                                                                       'color' : 'darkblue',
                                                                       'lineHeight': '40px',
                                                                       'borderWidth': '1px',
                                                                       'borderStyle': 'dashed',
                                                                       'borderRadius': '5px',
                                                                       'textAlign': 'center',
                                                                       'margin': 'auto'
                                                                      }
                                                               )
                                                    ], style = {'width' : '49.5%', 'margin': 'auto'}),
                                           html.Div([dcc.Upload(id='upload-data-r',
                                                                children=html.Div(id = 'uploaded2'),
                                                                style={'width': '100%',
                                                                       'height': 'auto',
                                                                       'minHeight' : '40px',
                                                                       'color' : 'darkred',
                                                                       'lineHeight': '40px',
                                                                       'borderWidth': '1px',
                                                                       'borderStyle': 'dashed',
                                                                       'borderRadius': '5px',
                                                                       'textAlign': 'center',
                                                                       'margin': 'auto'
                                                                      }
                                                               )
                                                    ], style = {'width' : '49.5%', 'margin': 'auto'}),
                                          ],
                                          style = {'width' : '100%', 'display' : 'flex','margin' : 'auto', 'textAlign' :'center'}
                                         ),
                                 html.Div([''], style = {'height':20, 'background-color':color, 'width' : 1900}),
                                 html.Div([html.Div([''], style = {'width':10, 'minWidth' : 10}),
                                           html.Div([html.H5('Compare measurements with recommendation levels', 
                                                             style={'font-family' : 'bahnschrift', 'width' : 440}),
                                                     dcc.Dropdown(['Exceed WHO','Exceed EPA'],
                                                                  'Exceed WHO',
                                                                  id='Organization',
                                                                  style={'font-family' : 'bahnschrift','width':440}
                                                                 ),
                                                     html.H5('Feature and model selection for RC modeling', style={'font-family' : 'bahnschrift'}),
                                                     html.Div([html.Plaintext('   Feature selection information: ',
                                                                              style={'font-family' : 'bahnschrift', 'width' : 250}
                                                                             ),
                                                               dcc.Dropdown(['Correlation matrix', 'Variance Inflation Factor'],
                                                                            'Correlation matrix',
                                                                            id = 'FS', style={'font-family' : 'bahnschrift', 'width' : 200}
                                                                           )
                                                              ],
                                                              style=dict(display='flex', width = 440)
                                                             ),
                                                     html.Div([html.Plaintext('   Model: ',
                                                                              style={'font-family' : 'bahnschrift', 'width' : 100}
                                                                             ),
                                                               dcc.Dropdown(['Log_Linear'],
                                                                            'Log_Linear',
                                                                            id = 'model',
                                                                            style={'font-family' : 'bahnschrift', 'width' : 340}
                                                                           )
                                                              ], 
                                                              style=dict(display='flex', width = 440)
                                                             ),
                                                     html.Div([html.Plaintext('   Features: ',
                                                                              style={'font-family' : 'bahnschrift', 'width' : 100}
                                                                             ),
                                                               dcc.Dropdown([],
                                                                            False,
                                                                            id = 'vars_',
                                                                            style={'font-family' : 'bahnschrift' , 'width' : 340},
                                                                            multi = True
                                                                           )
                                                              ], 
                                                              style=dict(display='flex')
                                                             ),
                                                     html.Div([], style = {'height': 10}),
                                                     html.Div([html.Plaintext('   High quality model:',
                                                                              style={'font-family' : 'bahnschrift', 'width' : 170}
                                                                             ),
                                                               html.Div([html.Div([''], style = {'height':15}),
                                                                         daq.BooleanSwitch(id='HQ_model', on=False),
                                                                        ]
                                                                       ),
                                                              ],
                                                              style=dict(display='flex', width = 440)),
                                                     html.Div([html.Div([html.Plaintext('   Run model: ',
                                                                                        style={'font-family' : 'bahnschrift', 'width' : 100}
                                                                                       ),
                                                                         html.Button('RUN',
                                                                                     style={'font-family' : 'bahnschrift',
                                                                                            'background-color':'steelblue',
                                                                                            'font-size':'20px',
                                                                                            'border' : '0px',
                                                                                            'color': 'white',
                                                                                            'border-radius':'12px',
                                                                                            'width' : 340,
                                                                                            'height' :50},
                                                                                     id='Predict_Rn',
                                                                                     n_clicks=0),
                                                                        ],
                                                                        style=dict(display='flex', width = 440)
                                                                       ),
                                                              ],
                                                              style=dict(display='flex', width = 440)),
                                                    ],
                                                    style = {'minWidth' : 440}
                                                   ),
                                           html.Div([''], style = {'width':10, 'minWidth' : 10}),
                                           html.Div([''], style = {'width':20, 'minWidth' : 20, 'background-color':color}),
                                           html.Div([dcc.Loading(id = 'loadg', 
                                                                 children = [dcc.Graph(id='RC-histogram',
                                                                                       style = {'height' : 470, 'width' : 995}
                                                                                      ),]
                                                                ),
                                                     html.Div([''], style = {'width':20, 'minWidth' : 20, 'background-color':color}),
                                                     dcc.Loading(id = 'ld',
                                                                 children = [dcc.Graph(id = 'FS_out', style = {'height' : 470, 'width' : 400})]),
                                                    ],
                                                    style=dict(display='flex'))
                                          ],
                                          style=dict(display='flex')),
                                 html.Div([''],style = {'height':20, 'background-color':color, 'width' : 1900}),
                                 html.Div([html.Div([''], style = {'width':10, 'minWidth' : 10}),
                                           dcc.Loading(id='loadRes',
                                                      children = [html.Div([html.H5(' Regression results: ',
                                                                                    style={'font-family' : 'bahnschrift'}
                                                                                   ),
                                                                            dash_table.DataTable(id= 'imp',
                                                                                                 style_header={'backgroundColor': color, 'color':'black','fontWeight': 'bold'},
                                                                                                 style_cell={'textAlign': 'center', 'backgroundColor':'lightgray', 'color':'black'},
                                                                                                 style_table={'width':440}, cell_selectable = False, style_as_list_view=True
                                                                                                ),
                                                                            html.H6(' Cross-validation score:', style={'font-family' : 'bahnschrift'}),
                                                                            dash_table.DataTable(id= 'RMSE',
                                                                                                 style_header={'backgroundColor': color, 'color':'black','fontWeight': 'bold'},
                                                                                                 style_cell={'textAlign': 'center', 'backgroundColor':'lightgray', 'color':'black'},
                                                                                                 style_table={'width':440}, cell_selectable = False, style_as_list_view=True
                                                                                                )
                                                                           ]
                                                                          )
                                                                 ]
                                                      ),
                                           html.Div([''],style={'width':10, 'minWidth' : 10}),
                                           html.Div([''],style={'width':20, 'minWidth' : 20, 'background-color':color}),
                                           dcc.Loading(id = 'load',
                                                       children = [dcc.Graph(id='RC-model-map',
                                                                             style = {'height' : 520, 'width' : 1415},
                                                                             config = {'displayModeBar': False})])
                                          ],
                                          style=dict(display='flex')
                                         ),
                                 html.Div([''], style = {'height':20,'background-color':color, 'width' : 1900}),
                                 html.Div([''], style = {'height':20}),
                                 html.Div([html.Div([html.P('Dashboard created by:'),
                                                     html.A('Martín Domínguez Durán',
                                                            href='https://www.martindominguezduran.com',
                                                            target="_blank")
                                                    ],
                                                    style = {'width':1460}),
                                          ],
                                          style=dict(display='flex',width = 1900)
                                         ),
                                 html.P(id = 'none'),
                                 
                                ]
                               ),
                      ])
                                          