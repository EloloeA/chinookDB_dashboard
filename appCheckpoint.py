# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 15:52:30 2020

@author: scriba
"""

import dash
import dash_core_components as dcc
import dash_html_components as html

import checkpoint as cp


resVentes = cp.init()
resTracks = cp.df_resTracks()




app = dash.Dash()
app.layout = html.Div(id = 'main', style = {'margin' : '3% 15% 5% 15%'}, children = [
                        html.H1("Music Chinook DataBase"),
                        html.H2("Dashboard analysis of the database"),
                        html.Div([
                                    html.Div('Number of Customers: ', style = {'textAlign' : 'center'}),
                                    html.P(cp.nbCustomers(), style = {'textAlign' : 'center', 'fontWeight' : 'bold', 'backgroundColor' : 'white'}),
                                    html.Br(),
                                    html.Div('Number of Employee : ')
                                    ]),
                                    dcc.Graph(style = {'width' : 'auto'}, figure = cp.employee_table()),
                        html.H3("Part 1 : Sales"),
                                    dcc.Graph(figure = cp.caParPays()), #afficher nbre de pays
                                    dcc.Graph(figure = cp.caParAnnee()),
                        
                        html.H3("Part 2 : Clients"),
                        html.Div([
                                html.Div('TOP 5 customers'),
                                dcc.Graph(figure = cp.top5client()),
                                html.Div('TOP 5 country'),
                                dcc.Graph(figure = cp.top5pays())
                                ], style = {'display' : 'flex'}),
                        dcc.Graph(figure = cp.carto()),
                        
                        html.H3("Part 3 : Music library"),
                        html.Div([
                                    html.Div('Number of artists :'),
                                    html.P(cp.nbArtistes()),
                                    html.Div('Number of tracks :'),
                                    html.P(cp.nbTracks()),
                                    html.Div('Number of albums :'),
                                    html.P(cp.nbAlbums())],
                            style = {'display' : 'flex'}),
                        html.Br(),
                        html.Hr(),
                        html.Br(),
                        html.P('Improve business', style = {'fontSize' : '2em', 'color' : 'grey', 'backgroundColor' : 'white'}),
                        html.P('Genre of music sold'),
                        dcc.Graph(figure = cp.plotGenre()),
                        html.Br(),
                        html.P("Customer profile : kind of music they buy/like ?"),
                        dcc.Graph(figure = cp.genreClient()),
                        html.Div('=> Same profile of customers'),
                        html.Br(),
                        dcc.Graph(figure = cp.artisteNonVendus())
                        
                    ])

app.run_server(debug=True, use_reloader=False) 