###
# App Name:  Quantity take-offs (QTO) from Revit and IFC
# App URI: https://DataDrivenConstruction.io/
# Description: Finding volumes for elements grouped according to conditions specified by the user
# Version:  0.3
# DataDrivenConstruction
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
###

import base64
import io
import pandas as pd
import pathlib
from pathlib import Path
import xml.etree.ElementTree as ET
import dash
from dash import dcc
from dash import html
from dash import dash_table
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import dash_uploader as du
import numpy as np
import os
import re
import uuid
import vaex

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

# CSV file loader and its settings


def get_upload_component(id):
    return du.Upload(
        id=id,
        max_file_size=1000,
        filetypes=['csv'],
        upload_id=uuid.uuid1(),  # Unique session id
        text='Drag and Drop Here to upload CSV 📥 ',
        text_completed='✔️ Uploaded: ',
        text_disabled='The uploader is disabled.',
        cancel_button=True,
        pause_button=False,
        disabled=False,
        chunk_size=1000,
        default_style=None,
        max_files=1,
    )

# DAE file loader and its settings


def get_upload_component2(id):
    return du.Upload(
        id=id,
        max_file_size=1000,  # 1800 Mb
        filetypes=['dae'],
        upload_id=uuid.uuid1(),  # Unique session id
        text='Drag and Drop Here to upload DAE 📥',
        text_completed='✔️ Uploaded: ',
        text_disabled='The uploader is disabled.',
        cancel_button=True,
        pause_button=False,
        disabled=False,
        chunk_size=1000,
        default_style=None,
        max_files=1,
    )


# Properties of volumes that can be filtered
propstr = ['Area', 'Volume', 'Width', 'Length', ]

# Path to the folder on the server where the files will be saved
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
UPLOAD_FOLDER_ROOT = UPLOAD_FOLDER
du.configure_upload(app, UPLOAD_FOLDER_ROOT)

# App Layout
app.layout = html.Div(
    children=[
        # Error Message
        html.Div(id="error-message"),
        # Top Banner
        html.Div(
            className="study-browser-banner row",
            children=[
                html.A(
                    html.Div(
                        className="div-logo2",
                        children=html.Img(
                            className="logo2", src="https://DataDrivenConstruction.com/wp-content/uploads/2021/11/VENDOR-FREE-5.png",
                        ),
                    ),
                    href="https://DataDrivenConstruction.com/#", target="_blank",),
                html.H2(className="h2-title", children="Quantity Takeoff OSS", style={
                    'margin-left': '45px',
                }),
                html.A(
                    id='gh-link',
                    children=[
                        'View on GitHub'
                    ],
                    href="https://github.com/DataDrivenConstruction/QuantityTakeoff-Python",
                    style={'color': 'white',
                           'border': 'solid 1px white',
                           'text-decoration': 'none',
                           'font-size': '10pt',
                           'font-family': 'sans-serif',
                           'color': '#fff',
                           'border': 'solid 1px #fff',
                                        'border-radius': '2px',
                                        'padding': '2px',
                                        'padding-top': '5px',
                                        'padding-left': '15px',
                                        'padding-right': '15px',
                                        'font-weight': '100',
                                        'position': 'relative',
                                        'top': '15px',
                                        'float': 'right',
                                        'margin-right': '40px',
                                        'margin-left': '5px',
                                        'transition-duration': '400ms',
                           }
                ),

                html.Div(
                    className="div-logo",
                    children=html.Img(
                        className="logo", src=("https://DataDrivenConstruction.io/wp-content/uploads/2021/12/GitHub-Mark-Light-64px-1.png")
                    ),
                ),
                html.H2(className="h2-title-mobile",
                        children="QTO DataDrivenConstruction.com"),
            ],
        ),

        # Body of the App
        html.Div(
            className="row app-body",
            children=[
                # User Controls
                html.Div(
                    className="four columns card",
                    children=[
                        html.Div(
                            [
                                html.H4(
                                    [
                                        html.Div([
                                            html.H5("🗂️ Upload your files or use a ready-made",
                                                    style={'padding-left': '30px', 'padding-top': '20px'},),
                                            html.Div([
                                                dcc.Dropdown(
                                                    id='hf-dropdown',
                                                    options=[
                                                        {'label': 'Upload files to the site',
                                                         'value': 'UF'},
                                                        {'label': 'Preloaded dataset House 1',
                                                         'value': 'H1'},
                                                        {'label': 'Preloaded dataset House 2',
                                                         'value': 'H2'}
                                                    ],
                                                    value='UF',
                                                    style={'height': '40px',
                                                           'width': '300px',
                                                           'margin-left':  '20px',
                                                           'margin-bottom':  '20px',
                                                           'font-size': '20px'}
                                                ),
                                                html.Div(id='dd-output-container', style={
                                                    'margin-left':  '50px',
                                                    'font-size': '16px'})
                                            ]),
                                        ]),
                                        get_upload_component(
                                            id='dash-uploader'),
                                        html.Div(id='callback-output'),
                                    ],
                                ),
                            ],
                            style={  # wrapper div style

                                'width': '100%',
                                'padding-right': '5px',
                                'padding-left': '5px',
                                'display': 'inline-block',
                                'background': 'rgb(233 238 246)',
                                'border': '2px', 'border-radius': '10px', 'box-shadow': '3px 10px 10px silver'
                            },
                        ),

                        html.Div(
                            [
                                html.H4(
                                    [
                                        get_upload_component2(
                                            id='dash-uploader2'),
                                        html.Div(id='containerfilename'),
                                    ],
                                    style={  # wrapper div style
                                        'textAlign': 'center',
                                        'width': '100%',
                                        'padding': '5px',
                                        'margin-top': '-35px',
                                        'background': 'rgb(237 245 255)',
                                    }),
                            ],
                            style={
                                'textAlign': 'center',
                            },
                        ),
                        html.Div(
                            className="bg-white user-control",
                            children=[
                                html.Div([
                                    html.H5(
                                        "🗃️ Selecting a property for grouping"),
                                    html.Div(id="containerb",
                                             children=dcc.Checklist(
                                                 id="dd_groupval",
                                                 options=[
                                                     {"label": "Select All Regions", "value": "All"}],
                                                 value=[],
                                             ),
                                             ),
                                    html.H6(
                                        children='selection from all properties of all elements',
                                        style={'font-size': '13px',  "padding-left": "15px", "padding-top": "5px"}),
                                ], style={'width': '95%',  "padding-top": "10px", 'display': 'inline-block'}),

                                html.Div([
                                    html.H5("📑 Filter refined"),
                                    dbc.InputGroup(
                                        [
                                            dbc.InputGroupText("ReGex "),
                                            dbc.Input(
                                                id="regexq",
                                                valid=True,
                                                type="text",
                                                value='*[wW]all*',
                                                style={'height': '40px',
                                                       'width': '260px',
                                                       'paddin-left':  '10px',
                                                       'font-size': '20px'}
                                            ),
                                        ],
                                    ),
                                    html.H6(
                                        children='examples: *[wW]all* , *Window*  More details: regex101.com',
                                        style={'font-size': '13px',
                                               "padding-top": "5px"}
                                    ),

                                ], style={"margin-top": "20px", }),

                                html.H5(children='🧮 Aggregated for the group', style={
                                        "padding-top": "25px"}),
                                html.Div([
                                    html.Div(id="containerc",
                                             children=dcc.Checklist(
                                                id="dd_propv",
                                                options=[
                                                    {"label": "Select All Regions", "value": "All"}],
                                                value=[],
                                             ),
                                             ),
                                    html.H6(
                                        children='select all categories or one specific',
                                        style={
                                            'font-size': '13px',  "padding-left": "5px", "padding-top": "5px"}
                                    ),
                                    html.H6(
                                        children='🧾 To reduce the load on the server, the number of items that are unloaded from CSV is limited to the first 10,000 items',
                                        style={
                                            'font-size': '15px',  "padding-left": "5px", "padding-top": "5px"}
                                    ),
                                ], style={}),
                            ], style={'background': 'rgb(233 238 246)', "padding-left": "40px",
                                      "padding-right": "30px", "margin-top": "10px",  'border': '2px', 'border-radius': '10px', 'box-shadow': '3px 10px 10px silver'},
                        )
                    ],
                ),
                # Graph
                html.Div(
                    className="eight columns card-left",
                    children=[
                        html.Div(id="elementhide",

                                 children=[

                                     html.Div([
                                         html.Div(id='divbutt'),
                                         dcc.Download(id="download-dae"),
                                         html.Div([html.Button(
                                             "Download DAE", id="btn-download-txt", n_clicks=0)], style={'display': 'none', },),
                                     ], style={"margin-top": "20px", },
                                     ),
                                 ], style={'display': 'block', },
                                 ),
                    ]
                ),
                html.Div(
                    className="eight columns card-left",
                    children=[
                        html.Div(id="elementhide2",

                                 children=[

                                     html.Div([

                                         html.Img(
                                             src='https://DataDrivenConstruction.com/wp-content/uploads/2021/11/qto_free_tool-3.png', style={"width": "100%", })
                                     ], style={"margin-top": "20px", },
                                     ),

                                     dcc.Markdown('''
                                        #### Who Does Quantity Takeoffs?
                                        Simply put, all parties involved in the front-end of a construction project need to be involved in the quantity takeoff.
                                        A construction quantity takeoff is a term commonly used in the industry to describe one of its most essential functions: the process by which a cost estimator reviews a set of plans during preconstruction in order to “take off” measurements from these plans to forecast construction costs.
                                        More about the project [DataDrivenConstruction](https://DataDrivenConstruction.com/).
                                        ''')
                                 ], style={'display': 'block', },
                                 ),
                    ]
                ),
                html.Div(
                    className="eight columns card-left",
                    children=[
                        html.Div(id="element-to-hide_h",
                                 children=[
                                     html.Div(
                                         children=[
                                             dcc.Graph(id="plot"),
                                         ],
                                     ),
                                     html.Div(
                                         children=[
                                             dcc.Graph(id="plot2"),
                                         ], style={'margin-top': '-30px'},
                                     ),
                                     html.Div(
                                         children=[
                                             dcc.Graph(id="plot3"),
                                         ], style={'margin-top': '-40px'},
                                     )
                                 ], style={'display': 'none'},
                                 ),
                        html.Div(
                            className="eight columns card-left",
                            children=[
                            ],
                        ),
                    ]),
                dcc.Store(id="error", storage_type="memory"),
            ],
        ),
    ]
)


# Callback to download CSV file
@app.callback(
    [
        Output("containerc", "children"),
        Output("containerb", "children"),
    ],
    [
        Input('dash-uploader', 'isCompleted'),
        Input('hf-dropdown', 'value'),
    ],
    [
        State('dash-uploader', 'fileNames'),
        State('dash-uploader', 'upload_id')
    ],
)
def update_error(iscompleted, valuedd, filenames, upload_id):

    if filenames is not None:
        if upload_id:
            root_folder = Path(UPLOAD_FOLDER_ROOT) / upload_id
        else:
            root_folder = Path(UPLOAD_FOLDER_ROOT)

        for filename in filenames:
            file = root_folder / filename
    # If a predefined dataset is selected in the dropdown menu - use it
    if valuedd == 'H1':
        file = '/var/www/qto/data/1house.csv'
    elif valuedd == 'H2':
        file = '/var/www/qto/data/6house.csv'
    else:
        pass

    # Formation of options for selection in the filtering settings module
    dfi = pd.read_csv(file, low_memory=False, error_bad_lines=False, nrows=10)
    onlycat = dfi['Category'].unique()
    dfi['Category'].unique()
    onlycat = np.insert(onlycat, 0, 'All categories')
    allpropdf = dfi.columns
    propstr_csv = []
    for el in propstr:
        if el in allpropdf:
            propstr_csv.append(el)
    return [
        dcc.Dropdown(
            id='dd_propv',
            options=[{'label': i, 'value': i} for i in propstr_csv],
            value=propstr_csv[1],
            style={'height': '40px',
                   'width': '310px',
                   # 'padding-top':   '10px',
                   'paddin-left':  '10px',
                   'font-size': '20px'}
        ),
        dcc.Dropdown(
            id='dd_groupval',
            options=[{'label': i, 'value': i} for i in allpropdf],
            value='Type',
            style={'height': '40px',
                   'width': '310px',
                   # 'padding-top':   '10px',
                   'paddin-left':  '10px',
                   'font-size': '20px'}
        )]


# Callback to download DAE file
@app.callback(
    [Output("containerfilename", "value"),
     ],
    [Input('dash-uploader2', 'isCompleted'), Input('hf-dropdown', 'value'), ],
    [State('dash-uploader2', 'fileNames'),
     State('dash-uploader2', 'upload_id')],

)
def update_error2(iscompleted2, valuedd, filenames2, upload_id2):
    if filenames2 is not None:
        if upload_id2:
            root_folder2 = Path(UPLOAD_FOLDER_ROOT) / upload_id2
        else:
            root_folder2 = Path(UPLOAD_FOLDER_ROOT)

        for filename2 in filenames2:
            filedae = root_folder2 / filename2

    # If a predefined dataset is selected in the dropdown menu - use it
    if valuedd == 'H1':
        filedae = '/var/www/qto/data/1house.dae'
    elif valuedd == 'H2':
        filedae = '/var/www/qto/data/6house.dae'
    else:
        pass
    return [str('filedae')]


# Callback filters selected by the user
@app.callback(
    [
        Output("download-dae", "data"),
        Output('dd-output-container', 'children'),
        Output("plot", "figure"),
        Output("plot2", "figure"),
        Output("plot3", "figure"),
        Output("elementhide", "style"),
        Output("element-to-hide_h", "style"),
        Output("elementhide2", "style"),
        Output("divbutt", "children")],
    [
        Input("dd_groupval", "value"),
        Input("dd_propv", "value"),
        Input('regexq', 'value'),
        Input('dash-uploader', 'isCompleted'),
        Input('containerfilename', 'value'),
        Input('dash-uploader2', 'isCompleted2'),
        Input("btn-download-txt", "n_clicks"),
        Input('hf-dropdown', 'value'),
    ],
    [
        State('dash-uploader', 'fileNames'),
        State('dash-uploader', 'upload_id'),
        State('dash-uploader2', 'fileNames'),
        State('dash-uploader2', 'upload_id')
    ], prevent_initial_call=True,
)
def update_output(dd_groupval, dd_propv, regexq, iscompleted, filedae, iscompleted2, n_clicks, valuedd, filenames, upload_id, filenames2, upload_id2):

    # File upload check
    try:
        if upload_id:
            root_folder = Path(UPLOAD_FOLDER_ROOT) / upload_id
        else:
            root_folder = Path(UPLOAD_FOLDER_ROOT)

        for filename in filenames:
            file = root_folder / filename
    except:
        pass

    # Formation of a graph, if there is no data to display
    fig_none = go.Figure()
    fig_none.add_trace(go.Scatter(
        x=[0, 1, 2, 3, 4, 5, 6, 7, 8, 10],
        y=[0, 4, 5, 1, 2, 3, 2, 4, 2, 1],
        mode="lines+markers+text",
        text=["", "", "", "", "no items found", "", "", "", "", ''],
        textfont_size=40,
    ))
    fig_none.update_layout(
        paper_bgcolor='#fff',
        plot_bgcolor='#fff'
    )
    fig_none.update_layout(
        xaxis=dict(
            showgrid=False,
            gridcolor='#fff',
            zerolinecolor='#fff'),
        yaxis=dict(
            showgrid=False,
            gridcolor='#fff',
            zerolinecolor='#fff'))

    if valuedd == 'H1':
        file = '/var/www/qto/data/1house.csv'
    elif valuedd == 'H2':
        file = '/var/www/qto/data/6house.csv'
    else:
        pass

    # Restricting loading data from the first "nrows" of a table
    dfi = pd.read_csv(file, low_memory=False, nrows=10000)
    df = dfi

    # Forming a copy of columns for string values
    for el in propstr:
        try:
            df[el+'_str'] = df[el]
            df[el+'_str'] = df[el+'_str'].fillna(0)
            df[el+'_str'] = df[el+'_str'].astype(str)
        except:
            pass

    #  Fetching only numbers from string values of volumetric parameters
    def find_number(text):
        num = re.findall(r'[0-9]+', text)
        return ".".join(num)
    for el in propstr:
        try:
            df[el] = df[el].astype(str)
            df[el] = df[el].apply(lambda x: find_number(x))
            df[el] = df[el].fillna(0)
            df[el] = pd.to_numeric(df[el], errors='coerce')
            df[el] = df[el].replace(np.nan, 0)
            df[el] = df[el].replace('None', 0)
            df[el] = df[el].fillna(0)
        except:
            pass
        try:
            df[el] = df[el].astype(float)
        except:
            pass

    # Checking the condition if something will be found with Regex
    if not df[df[dd_groupval].str.match('.'+regexq) == True].empty:

        # Grouping by a regular expression that was entered by the user
        df_group_byword = df[df[dd_groupval].str.match('.'+regexq) == True]
        df_groups_wall = df_group_byword.groupby(
            [dd_groupval])[dd_propv].agg(['sum', 'count'])
        df_groups_wall.columns = [
            ''.join(str(i) for i in col) for col in df_groups_wall.columns]
        df_groups_wall = df_groups_wall.rename(
            {'sum': 'Sum of the Areas', 'count': 'Number of elements'}, axis=1)
        df_groups_wall.reset_index(inplace=True)
        df_group_byword = df_group_byword.rename(columns={'Unnamed: 0': 'id'})

        # Grouping string values by a regular expression that was entered by the user
        df_group_byword2 = df[df[dd_groupval].str.match('.'+regexq) == True]
        df_groups_wall2 = df_group_byword.groupby(
            [dd_groupval])[dd_propv+"_str"].agg(['sum', 'count'])
        df_groups_wall2 = df_groups_wall2.rename(
            {'sum': 'Separate ' + dd_propv + ' of elements', 'count': 'Number of elements'}, axis=1)
        df_groups_wall2.reset_index(inplace=True)
        df_group_byword2 = df_group_byword2.rename(
            columns={'Unnamed: 0': 'id'})
        df_groups_wall2['Sum of the ' +
                        dd_propv] = df_groups_wall['Sum of the Areas']
        group_ids = df_group_byword.id.values

        # Find all element ids that have been grouped by regular expression
        group_ids_str = []
        for el in group_ids:
            group_ids_str.append(str(el))

        # Formation of a table for displaying data of grouped elements
        fig3 = go.Figure(data=[go.Table(
            header=dict(values=list(df_groups_wall2.columns),
                        line_color='darkslategray',
                        fill_color='lightskyblue',
                        align='left'),
            cells=dict(values=df_groups_wall2.values.T,
                       fill_color='lavender',
                       align='left'))
        ])
        fig3.update_layout(width=1000, height=500,
                           margin=dict(l=70, r=30, t=0, b=0),
                           paper_bgcolor='#fff',
                           plot_bgcolor='#fff',)

        # Formation of pie chart for displaying data of grouped elements
        fig2 = make_subplots(rows=1, cols=2, specs=[
                             [{'type': 'domain'}, {'type': 'domain'}]])
        fig2.add_trace(go.Pie(labels=df_groups_wall[dd_groupval], values=df_groups_wall["Number of elements"], name="Quantity, PCS"),
                       1, 1)
        fig2.add_trace(go.Pie(labels=df_groups_wall[dd_groupval], values=df_groups_wall["Sum of the Areas"], name=dd_propv),
                       1, 2)

        fig2.update_layout(
            annotations=[dict(text='Quantity', x=0.15, y=0.5, font_size=20, showarrow=False),
                         dict(text=dd_propv, x=0.84, y=0.5, font_size=20, showarrow=False)],
            paper_bgcolor='#fff',
            plot_bgcolor='#fff',
            margin=dict(l=150, r=150, t=50, b=100),
            height=370,)

        # Form a bar chart to display the data of grouped members
        fig = make_subplots(rows=1, cols=2, specs=[
                            [{}, {}]], shared_xaxes=True, shared_yaxes=False, vertical_spacing=0.001)
        fig.append_trace(go.Bar(
            x=df_groups_wall["Number of elements"],
            y=df_groups_wall[dd_groupval],
            marker=dict(
                color='rgba(50, 171, 96, 0.6)',
                line=dict(color='rgba(50, 171, 96, 1.0)', width=3),),
            name='The number of elements in a group',
            orientation='h',
        ), 1, 1)
        fig.append_trace(go.Bar(
            x=df_groups_wall["Sum of the Areas"],
            y=df_groups_wall[dd_groupval],
            marker=dict(
                color='rgba(58, 71, 80, 0.6)',
                line=dict(color='rgba(58, 71, 80, 1.0)', width=3),),
            name=dd_propv + ' value in the group',
            orientation='h',
        ), 1, 2)
        fig.update_layout(
            title='Number and ' + dd_propv + ' of grouped elements by ' +
            dd_groupval + ' and expression' + regexq,
            yaxis=dict(
                showgrid=False,
                showline=True,
                showticklabels=True,
                domain=[0, 0.85],
            ),
            yaxis2=dict(
                showgrid=False,
                showline=True,
                showticklabels=False,
                linecolor='rgba(102, 102, 102, 0.8)',
                domain=[0, 0.85],
            ),
            xaxis=dict(
                zeroline=False,
                showline=False,
                showticklabels=True,
                showgrid=True,
                domain=[0, 0.42],
                side='top',
            ),
            xaxis2=dict(
                zeroline=False,
                showline=False,
                showticklabels=True,
                showgrid=True,
                domain=[0.47, 1],
                side='top',
            ),
            legend=dict(x=0.029, y=1.1, font_size=10),
            margin=dict(l=70, r=20, t=80, b=30),
            paper_bgcolor='#fff',
            plot_bgcolor='#fff',
            height=370,
        )

        # Adding annotations
        annotations = []
        y_s = np.round(df_groups_wall["Number of elements"], decimals=2)
        y_nw = np.rint(df_groups_wall["Sum of the Areas"])

        # Adding labels
        for ydn, yd, xd in zip(y_nw, y_s, df_groups_wall[dd_groupval]):

            annotations.append(dict(xref='x2', yref='y2',
                                    y=xd, x=ydn,
                                    text='{:,}'.format(ydn),
                                    font=dict(family='Arial', size=12,
                                              color='rgb(128, 0, 128)'),
                                    showarrow=False))
            # labeling the bar net worth
            annotations.append(dict(xref='x1', yref='y1',
                                    y=xd, x=yd,
                                    text=str(yd) + ' PCS.',
                                    font=dict(family='Arial', size=12,
                                              color='rgb(50, 171, 96)'),
                                    showarrow=False))
        fig.update_layout(annotations=annotations)

    # In the absence of data, show the fig_none
    else:

        fig = fig_none
        fig2 = fig_none
        fig3 = fig_none
    try:
        try:
            if upload_id2:
                root_folder2 = Path(UPLOAD_FOLDER_ROOT) / upload_id2
            else:
                root_folder2 = Path(UPLOAD_FOLDER_ROOT)
            for filename2 in filenames2:
                filedae = root_folder2 / filename2
        except:
            pass
        if valuedd == 'H1':
            filedae = '/var/www/qto/data/1house.dae'
        elif valuedd == 'H2':
            filedae = '/var/www/qto/data/6house.dae'
        else:
            pass

        # Start sorting geometry from DAE file
        fileObject = open(filedae, "r")
        ET.register_namespace(
            "", "http://www.collada.org/2005/11/COLLADASchema")
        tree = ET.parse(fileObject)

        # Formation of a data tree from the DAE format
        root = tree.getroot()
        geom_list = []

        # If the ID of an element from the group_ids_str list that was found earlier matches,
        # all elements with this ID are found in the DAE file, and all other elements are deleted
        for node in root.findall('.//{http://www.collada.org/2005/11/COLLADASchema}node'):
            if node.attrib['id'] in group_ids_str:
                url = list(node)[0].get('url')
                geom_list.append(url[1:])
            else:
                try:
                    nd = node.find(
                        '{http://www.collada.org/2005/11/COLLADASchema}instance_geometry')
                    node.remove(nd)
                except:
                    0
        for geomet in root.findall('.//{http://www.collada.org/2005/11/COLLADASchema}geometry'):
            if geomet.attrib['id'] in geom_list:
                0
            else:
                md = geomet.find(
                    '{http://www.collada.org/2005/11/COLLADASchema}mesh')
                geomet.remove(md)

        # Formation of a new name for the DAE file with grouped elements
        words_pattern = '[a-zA-Z10-9]+'
        regw = re.findall(words_pattern, regexq, flags=re.IGNORECASE)
        regwn = ''
        for el in regw:
            regwn = regwn + el
        if valuedd == 'H1':
            filename2 = '1house.dae'
            root_folder2 = Path(
                '/var/www/qto/uploads/421169a4-46b0-11ec-a3ea-a9e6df576ad3')
        elif valuedd == 'H2':
            filename2 = '6house.dae'
            root_folder2 = Path(
                '/var/www/qto/uploads/421169a4-46b0-11ec-a3ea-a9e6df576ad3')
        else:
            pass
        filename2nn = regwn + '_' + filename2
        filedaena = root_folder2 / filename2nn
        with open(filedaena, 'w') as f:
            tree.write(f, encoding='unicode')
        if n_clicks > 1:
            return dcc.send_file(filedaena), 'You have selected "{}"'.format(valuedd), fig, fig2, fig3, {'display': 'block'}, {'display': 'block'}, {'display': 'none'}, html.Div([html.Button("📤 Download DAE geometry "+filename2nn, id="btn-download-txt", n_clicks=n_clicks+1)])
            n_clicks = 0
        else:
            return ['', 'You have selected dataset "{}"'.format(valuedd), fig, fig2, fig3, {'display': 'block'}, {'display': 'block'}, {'display': 'none'}, html.Div([html.Button("📤 Download DAE geometry "+filename2nn, id="btn-download-txt", n_clicks=n_clicks+1)])]
    except:
        return ["", 'You have selected dataset "{}"'.format(valuedd), fig, fig2, fig3, {'display': 'none'}, {'display': 'block'}, {'display': 'none'},
                html.Div(
                    [html.Button("Download D2a", id="btn-download-txt", n_clicks=0)])
                ]


if __name__ == "__main__":
    app.run_server(host='93.188.165.241', port=8050,  use_reloader=True,)
