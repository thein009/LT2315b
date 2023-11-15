import pandas as pd
from dash import Dash, dcc, html, Input, Output, callback, Patch, clientside_callback
import csv
import plotly.io as pio
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
import dash_ag_grid as dag
import plotly.graph_objects as go
import datetime


dat_file = "assets/LT2312_LT2312.dat"
dat_file1 = "assets/LT2312_Sum.dat"
csv_file = "assets/LT2312_LT2312.csv"
csv_file1 = "assets/LT2312_Sum.csv"


def update_dat(data_file, csv_file):
    file = open(data_file, "r")
    reader = csv.reader(file)
    lines = list(reader)
    header_row = ["TimeStamp", "Record", "Batt", "Temp", "Load_kN", "Load_Pct", "S1", "S2", "S3", "S4", "S_avg",
                  "RB_Mov", "S_Cor"]
    n_file = open(csv_file, "w", newline="")
    writer = csv.writer(n_file)
    writer.writerow(header_row)
    writer.writerows(lines[4:])
    file.close()
    n_file.close()


def update_latest(csv_file):
    update_dat(dat_file, csv_file)
    df = pd.read_csv(csv_file, na_values=['NAN'])
    df['TimeStamp'] = pd.to_datetime(df['TimeStamp']).dt.strftime("%Y-%m-%d %H:%M")
    last_row = df.iloc[-1]
    load_kN = f'{last_row[4]:.0f}'
    load_pct = f'{last_row[5]:.0f}'
    sett = f'{last_row[12]:.2f}'
    return f'{last_row[0]} - {load_kN} kN, {load_pct} %, Sett = {sett} mm'


# stylesheet with the .dbc class to style dcc, DataTable and AG Grid components with a Bootstrap theme
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, dbc_css, '/assets/styles.css'])


company_logos = html.Div([
        html.Img(src="/assets/company_logo.png", style={'position': 'absolute', 'top': '5px', 'right': '10px', 'z-index': 2, 'height': '40px', 'width': '60px'}),
        html.Img(src="/assets/ajc_logo.png", style={'position': 'absolute', 'top': '5px', 'left': '10px', 'z-index': 2, 'height': '40px', 'width': '120px'}),
    ])

color_mode_switch = html.Span(
    [
        dbc.Label(className="fa fa-moon", html_for="switch"),
        dbc.Switch(id="switch", value=True, className="d-inline-block ms-1", persistence=True),
        dbc.Label(className="fa fa-sun", html_for="switch")
    ], style={"float": "right"},
)

# The ThemeChangerAIO loads all 52  Bootstrap themed figure templates to plotly.io
theme_controls = html.Div(
    [ThemeChangerAIO(aio_id="theme")],
)

header = html.H4("PTP2 (MLT @ M Minori, Seri Austin, Johor)", className="scroll-left", style={"margin": "10px 0px"})

dropdown = html.Div(
    [
        dbc.Row([
            dbc.Col([theme_controls], style={"margin": "10px 10px"}),
            dbc.Col([color_mode_switch], style={"margin": "13px 10px"}),
        ])
    ],
)

download_btn1 = dbc.Button('Download Summary', id='download-data-button1', n_clicks=0, style={'font-size': '14px',
    'padding': '5px 10px', 'box-shadow': '7px 7px 7px rgba(0, 0, 0, 0.5)', 'margin-left': '5px'})
download_1 = dcc.Download(id="download-data1")

download_btn2 = dbc.Button('Download All Data', id='download-data-button2', n_clicks=0, style={'font-size': '14px',
    'padding': '5px 10px', 'box-shadow': '7px 7px 7px rgba(0, 0, 0, 0.5)', 'margin-left': '10px'})
download_2 = dcc.Download(id="download-data2")

date_time = html.Div(id='date-time', style={'text-align': 'center', 'padding-top': '10px', 'padding-bottom': '0px',
                                            'font-size': '18px', 'font-weight': 'bold'}),


def update_grid():
    update_dat(dat_file1, csv_file1)
    df = pd.read_csv(csv_file1, na_values=['NAN'])
    df = df.drop(columns=[df.columns[1], df.columns[2], df.columns[3], df.columns[6], df.columns[7], df.columns[8],
                          df.columns[9], df.columns[10], df.columns[11]])
    df['TimeStamp'] = pd.to_datetime(df['TimeStamp']).dt.strftime("%Y-%m-%d %H:%M")

    grid = dag.AgGrid(
            id="grid",
            columnDefs=[
            {"field": "TimeStamp", "headerName": "Time Stamp", "autoWidth": True},
            {"field": "Load_kN", "headerName": "Load (kN)", "autoWidth": True},
            {"field": "Load_Pct", "headerName": "Load (%)", "autoWidth": True},
            {"field": "S_Cor", "headerName": "Sett (mm)", "autoWidth": True},
            ],
            rowData=df.to_dict("records"),
            defaultColDef={"flex": 1, "minWidth": 180, "sortable": True, "resizable": True, "filter": True},
            dashGridOptions={"rowSelection": "multiple"},
        )
    return grid


theme_colors = ["primary", "secondary", "success", "warning", "danger", "info", "light", "dark", "link"]
colors = html.Div(
    [dbc.Button(f"{color}", color=f"{color}", size="sm", style={"margin": "5px 5px"}) for color in theme_colors]
)
colors = html.Div(["Theme Colors:", colors], className="mt-2")


controls = dbc.Card(
    dropdown,
    body=False
)

tab1 = dbc.Tab([dcc.Graph(id="time-series-chart")], label="Time Series")
tab2 = dbc.Tab([dcc.Graph(id="load-sett-chart")], label="Load-Sett")
tab3 = dbc.Tab([dcc.Graph(id="summary-chart")], label="Summary")
tab4 = dbc.Tab(update_grid(), label="Data", className="p-4")
tabs = dbc.Card(dbc.Tabs([tab1, tab2, tab3, tab4]))

app.layout = dbc.Container(
    [
        header,
        company_logos,
        controls,
        html.Div(id='date-time', style={'text-align': 'center', 'padding-top': '7px', 'padding-bottom': '0px', 'font-weight': 'bold'}),
        html.H6(id='latest-data', className="scroll-left", style={"margin": "7px 0px"}),
        tabs,
        html.H6("Download Data", style={"margin": "10px 0px", }),
        download_btn1, download_1, download_btn2, download_2,
        colors,
    dcc.Interval(
        id='interval-time',
        interval=1 * 1000,  # in milliseconds (every second)
    ),
    dcc.Interval(
        id='interval-charts-tables',
        interval=60 * 1000,  # in milliseconds (every minute)
        n_intervals=0
    ),
    ],
    fluid=True,
    className="dbc dbc-ag-grid",
)


@callback(
    Output("time-series-chart", "figure"),
    Output("load-sett-chart", "figure"),
    Output("summary-chart", "figure"),
    Output("grid", "rowData"),
    Output('latest-data', 'children'),
    Input('interval-charts-tables', 'n_intervals'),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("switch", "value"),
)
def update(update_interval, theme, color_mode_switch_on):
    update_dat(dat_file, csv_file)
    df = pd.read_csv(csv_file, na_values=['NAN'])
    df['TimeStamp'] = pd.to_datetime(df['TimeStamp']).dt.strftime("%Y-%m-%d %H:%M")
    theme_name = template_from_url(theme)
    template_name = theme_name if color_mode_switch_on else theme_name + "_dark"
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["TimeStamp"], y=df["Load_kN"], mode='lines', name='Load (kN)', yaxis='y', line=dict(color='blue'),
                             customdata=df[['TimeStamp', 'Load_kN', 'S_Cor']],
                             hovertemplate="<b>%{customdata[0]}</b><br><b>Load </b>: %{customdata[1]} kN<br><b>Sett </b>: %{customdata[2]} mm",
                             hoverlabel={'bgcolor': 'rgba(0, 0, 255, 0.2)'}
                             ))
    fig.add_trace(go.Scatter(x=df["TimeStamp"], y=df["S_Cor"], mode='lines', name='Sett (mm)', yaxis='y2', line=dict(color='#FF0000'),
                             customdata=df[['TimeStamp', 'Load_kN', 'S_Cor']],
                             hovertemplate="<b>%{customdata[0]}</b><br><b>Load </b>: %{customdata[1]} kN<br><b>Sett </b>: %{customdata[2]} mm",
                             hoverlabel={'bgcolor': 'rgba(255, 0, 0, 0.2)'}
                             ))
    fig.update_layout(
        title="Load Vs Settlement Vs Time Chart",
        title_x=0.5, title_y=0.87,
        yaxis=dict(title="Applied Load (kN)", side="left", range=[-5000, 5000], zeroline=False, gridcolor='lightgrey', showline=True, linecolor='grey', ticks='outside'),
        yaxis2=dict(title="Settlement (mm)", overlaying="y", side="right", range=[50, -50], zeroline=False, gridcolor='lightgrey', showline=True, linecolor='grey', ticks='outside'),
        xaxis=dict(gridcolor='lightgrey', side="bottom", showline=True, linecolor='grey', linewidth=1, mirror=True, ticks='outside'),
        legend=dict(orientation="h", y=1.0),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        template=template_name
    ),

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df["Load_kN"], y=df["S_Cor"], mode='lines', name='Load-Sett', line=dict(color='red'),
                              customdata=df[['TimeStamp', 'Load_kN', 'S_Cor']],
                              hovertemplate="<b>%{customdata[0]}</b><br><b>Load </b>: %{customdata[1]} kN<br><b>Sett </b>: %{customdata[2]} mm",
                              hoverlabel={'bgcolor': 'rgba(255, 0, 0, 0.2)'}
                              ))
    fig2.update_layout(
        title="Load Vs Settlement Chart",
        title_x=0.5, title_y=0.87,
        yaxis=dict(title="Settlement (mm)", side="left", range=[30, 0], zeroline=False, gridcolor='lightgrey',
                   showline=True, linecolor='grey', mirror=True, ticks='outside'),
        xaxis=dict(title="Applied Load (kN)", side="bottom", range=[0, 4000], zeroline=False, gridcolor='lightgrey',
                   showline=True, linecolor='grey', mirror=True, ticks='outside'),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        template=template_name
    )

    update_dat(dat_file1, csv_file1)
    df = pd.read_csv(csv_file1, na_values=['NAN'])
    df['Load_Pct'] = df['Load_Pct'].apply(lambda x: round(x / 25, 0) * 25 if round(x / 25, 0) * 25 <= 200 else 200)
    df_1 = df[['TimeStamp', 'Load_kN', 'Load_Pct', 'S_Cor']][:9]
    df_2 = df[['TimeStamp', 'Load_kN', 'Load_Pct', 'S_Cor']][8:]
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=df_1["Load_kN"], y=df_1["S_Cor"], mode='lines+markers', line=dict(color='blue'), name='First Cycle',
                              customdata=df_1[['TimeStamp', 'Load_kN', 'Load_Pct', 'S_Cor']],
                              hovertemplate="<b>%{customdata[0]}</b><br><b>Load </b>: %{customdata[1]} kN<br><b>Load </b>: %{customdata[2]} %<br><b>Sett </b>: %{customdata[3]} mm",
                              hoverlabel={'bgcolor': 'rgba(0, 0, 255, 0.2)'}))
    fig3.add_trace(go.Scatter(x=df_2["Load_kN"], y=df_2["S_Cor"], mode='lines+markers', line=dict(color='red'), name='Second Cycle',
                              customdata=df_2[['TimeStamp', 'Load_kN', 'Load_Pct', 'S_Cor']],
                              hovertemplate="<b>%{customdata[0]}</b><br><b>Load </b>: %{customdata[1]} kN<br><b>Load </b>: %{customdata[2]} %<br><b>Sett </b>: %{customdata[3]} mm",
                              hoverlabel={'bgcolor': 'rgba(255, 0, 0, 0.2)'}))
    fig3.update_layout(
        title="Load Vs Settlement Summary Chart",
        title_x=0.5, title_y=0.87,
        yaxis=dict(title="Settlement (mm)", side="left", range=[30, 0], zeroline=False, gridcolor='lightgrey', showline=True, linecolor='grey', mirror=True, ticks='outside'),
        xaxis=dict(title="Applied Load (kN)", side="bottom", range=[0, 4000], zeroline=False, gridcolor='lightgrey', showline=True, linecolor='grey', mirror=True, ticks='outside'),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        legend=dict(x=0, y=0, xanchor='left', yanchor='bottom'),
        showlegend=True,
        template=template_name
    )

    update_grid()
    df = pd.read_csv(csv_file1, na_values=['NAN'])
    df['Load_Pct'] = df['Load_Pct'].apply(lambda x: round(x / 25, 0) * 25 if round(x / 25, 0) * 25 <= 200 else 200)
    # df['TimeStamp'] = pd.to_datetime(df['TimeStamp']).dt.strftime("%Y-%m-%d %H:%M")

    latest_data = update_latest(csv_file1)

    return fig, fig2, fig3, df.to_dict("records"), latest_data


@app.callback(
    Output("download-data1", "data"),
    Input("download-data-button1", "n_clicks")
)
def download_data1_callback(n_clicks):
    if n_clicks > 0:
        update_dat(dat_file1, csv_file1)
        df = pd.read_csv(csv_file1)
        df = df.drop(columns=[df.columns[1], df.columns[2], df.columns[3], df.columns[6], df.columns[7], df.columns[8],
                              df.columns[9], df.columns[10], df.columns[11]])
        df["TimeStamp"] = pd.to_datetime(df["TimeStamp"]).dt.strftime('%d-%m-%y %H:%M')
        df['Load_Pct'] = df['Load_Pct'].apply(lambda x: round(x / 25, 0) * 25 if round(x / 25, 0) * 25 <= 200 else 200)
        df = df.rename(columns={df.columns[0]: "Time Stamp", df.columns[1]: "Load (kN)", df.columns[2]: "(%)", df.columns[3]: "Sett (mm)"})
        return dcc.send_data_frame(df.to_csv, "LT2312_Summary.csv")


@app.callback(
    Output("download-data2", "data"),
    Input("download-data-button2", "n_clicks")
)
def download_data2_callback(n_clicks):
    if n_clicks > 0:
        update_dat(dat_file, csv_file)
        df = pd.read_csv(csv_file)
        df = df.drop(columns=[df.columns[1], df.columns[2], df.columns[3]])
        df = df.rename(columns={df.columns[0]: "Time Stamp", df.columns[1]: "Load (kN)", df.columns[2]: "Load (%)"})
        return dcc.send_data_frame(df.to_csv, "LT2312_All_Data.csv")


@app.callback(
    Output('date-time', 'children'),
    [Input('interval-time', 'n_intervals')]
)
def update_date_time(n_intervals):
    now = datetime.datetime.now()
    date_time = now.strftime('%Y-%m-%d %H:%M:%S')
    return date_time

# updates the Bootstrap global light/dark color mode
clientside_callback(
    """
    switchOn => {       
       switchOn
         ? document.documentElement.setAttribute('data-bs-theme', 'light')
         : document.documentElement.setAttribute('data-bs-theme', 'dark')
       return window.dash_clientside.no_update
    }
    """,
    Output("switch", "id"),
    Input("switch", "value"),
)


# This callback isn't necessary, but it makes updating figures with the new theme much faster
@callback(
    Output("time-series-chart", "figure", allow_duplicate=True),
    Output("load-sett-chart", "figure", allow_duplicate=True),
    Output("summary-chart", "figure", allow_duplicate=True),
    Input(ThemeChangerAIO.ids.radio("theme"), "value"),
    Input("switch", "value"),
    prevent_initial_call=True
)
def update_template(theme, color_mode_switch_on):
    theme_name = template_from_url(theme)
    template_name = theme_name if color_mode_switch_on else theme_name + "_dark"

    patched_figure = Patch()
    patched_figure["layout"]["template"] = pio.templates[template_name]
    return patched_figure, patched_figure, patched_figure


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=80815, debug=False)
