# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 09:16:52 2020

Database is an example of a music album sales company. 

"""

import pandas as pd
import requests
import sqlite3
import json
import plotly.graph_objs as go
import plotly.express as px
import plotly.figure_factory as ff


link = "https://github.com/EloloeA/chinookDB_dashboard/blob/master/chinook.db?raw=true"
r = requests.get(link)
open('chinook.db', 'wb').write(r.content)


conn = sqlite3.connect('chinook.db')
cursor = conn.cursor()
cursor.execute('select * from invoice_items').fetchall()



# VENTES et CLIENTS
def init():
    resVentes = pd.read_sql("SELECT InvoiceDate, BillingCountry, CustomerId,\
                            SUM(UnitPrice * Quantity) AS Amount,\
                            FirstName, LastName, Company, City, Country\
                            FROM invoice_items \
                            INNER JOIN invoices\
                            ON invoice_items.InvoiceId = invoices.InvoiceId\
                            INNER JOIN customers\
                            USING (CustomerId)\
                            GROUP BY invoice_items.InvoiceId", conn)
    # Information temporelle des ventes : SAISONNALITE
    resVentes['InvoiceDate'] = pd.to_datetime(resVentes['InvoiceDate'])
    # type(resVentes['InvoiceDate'][0])
    return resVentes




# EMPLOYEES table
def employee_table():
    employees = pd.read_sql("SELECT * FROM employees", conn)
    employees = ff.create_table(employees[['LastName','FirstName', 'Title']])
    employees.layout.width=500
    return employees

def top5client():
    # TOP 5 des clients qui ont le plus dépensé :
    resVentesParClient = resVentes.groupby(['CustomerId', 'FirstName', 'LastName', 'Country']).sum().reset_index()
    resVentesParClient = resVentesParClient.sort_values(by='Amount', ascending = False)[0:5]
    resVentesParClient['Amount'] = round(resVentesParClient['Amount'],2)
    res = ff.create_table(resVentesParClient)
    res.layout.width = 600
    return res

def top5pays():
    # TOP 5 des pays où il y a le plus de ventes :
    resVentesParPays = resVentes.groupby('Country').sum().reset_index()
    resVentesParPays = resVentesParPays.sort_values(by='Amount', ascending = False)[0:5]
    resVentesParPays = resVentesParPays[['Country', 'Amount']]
    resVentesParPays['Amount'] = round(resVentesParPays['Amount'],0)
    res = ff.create_table(resVentesParPays)
    res.layout.width = 400
    return res

# Information temporelle des ventes : SAISONNALITE

## ventes par année
def caParAnnee():
    annee_sum = resVentes.groupby(resVentes['InvoiceDate'].dt.year).sum().reset_index()
    annee_sum.sort_values(by = 'Amount', inplace = True)
    # TRACE = séries
    trace0 = go.Bar(
        x = annee_sum['InvoiceDate']
        ,    y = annee_sum['Amount']
        )
    # DATA
    data = [trace0]
    
    # LAYOUT
    layout = go.Layout(title = "TURNOVER (quantity * price) for each YEAR",
                       yaxis = {"title" : "Turnover"},
                       xaxis = {"title" : "Year"})
    
    # FIGURE
    ventesAnnuelles = go.Figure(data = data, layout = layout)
    ventesAnnuelles.update_traces(marker_color='#C22C32')
    return ventesAnnuelles

## ventes par pays
def caParPays():
    pays_sum = resVentes.groupby(["Country"]).sum().reset_index()
    pays_sum.sort_values(by = 'Amount', inplace = True)
    # TRACE = séries
    trace0 = go.Bar(
        x = pays_sum['Country'], y = pays_sum['Amount'])
    
    # DATA 
    data = [trace0]
    
    # LAYOUT
    layout = go.Layout(title = "TURNOVER vs COUNTRY",
                       yaxis = {"title" : "Turnover"},
                       xaxis = {"title" : "Country"})
    
    # FIGURE
    ventesPays = go.Figure(data = data, layout = layout)
    ventesPays.update_traces(marker_color='#C22C32')
    return ventesPays

# CARTOGRAPHIE localisation clientèle
def carto():
    lien3 = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
    r = requests.get(lien3)
    res = json.loads(r.text)
    
    df_geo = pd.json_normalize(r.json(),  
                      record_path= "features")
    
    pays_sum = resVentes.groupby(["Country"]).sum().reset_index()
    df = pays_sum # Country et Amount
    # on a besoin de récupérer le code ISO 'id' pour faire la carte
    new = pd.merge(df, df_geo, how = 'left', left_on = 'Country', right_on = 'properties.name')
    # bug sur USA
    new.loc[new['Country'] == 'USA', 'id'] = 'USA'
    
    fig = px.choropleth_mapbox(new, geojson=res, color="Amount",
                               locations="id", 
                               center={"lat": 45.5517, "lon": -73.7073},
                               mapbox_style="carto-positron", zoom=1)
    fig.layout.height = 1000
    return fig
    # fig.write_html('figure', auto_open = True)


## CATALOGUE MUSICAL
def df_resTracks():
    resTracks = pd.read_sql("SELECT InvoiceLineId, InvoiceDate, CustomerId, TrackId,\
                            invoice_items.UnitPrice, Quantity, \
                            Title AS albumTitle, artists.Name AS artist,\
                            tracks.Name AS track, media_types.Name AS media, genres.Name AS genre \
                            FROM invoice_items \
                            INNER JOIN invoices\
                            ON invoice_items.InvoiceId = invoices.InvoiceId\
                            INNER JOIN tracks\
                            USING (TrackId)\
                            INNER JOIN albums\
                            USING (AlbumId)\
                            INNER JOIN artists\
                            USING (ArtistId)\
                            INNER JOIN media_types\
                            USING (MediaTypeId)\
                            INNER JOIN genres\
                            USING (GenreId)", conn)
    return resTracks

         

def nbArtistes():
    #Infos sur nb artiste :
    baseArtiste = pd.read_sql("select * from artists\
                  LEFT JOIN albums\
                  USING (ArtistId)", conn)
    res = baseArtiste['Name'].unique().size #275 
    return res
    
def nbAlbums():
    #infos sur nbre albums :
    baseAlbum = pd.read_sql("select * from albums\
              LEFT JOIN artists\
              USING (ArtistId)", conn)
    res = baseAlbum['Title'].unique().size # 347
    return res

def nbTracks():
    tracks = pd.read_sql("select * from tracks", conn)
    return tracks.shape[0]


def nbCustomers():
    customers = pd.read_sql("select * from customers", conn)
    return customers.shape[0]





# repérer les artistes "non vendus": REGARDER les trackId et pas les albums
def artisteNonVendus():
    artistesvendus = resTracks.groupby('artist').count().reset_index()
    # artistesvendus[artistesvendus.isna().any(axis = 1)]#pas de ventes de tracks sans albums 

    # voir dans la base artiste qui n'est pas dans resTracks
    baseArtiste = pd.read_sql("select * from artists\
                      LEFT JOIN albums\
                      USING (ArtistId)", conn)              
                      
    df = pd.merge(baseArtiste, artistesvendus, how = 'left', left_on = 'Name', right_on ='artist')
    dfnan = df[df.isna().any(axis = 1)] # il y a ceux qui n'ont pas d'albums, et ceux qui en ont mais pas vendus = 110
    dfnan = dfnan[['Name', 'Title', 'InvoiceLineId']]
    res = ff.create_table(dfnan)
    return res

## IMPROVE BUSINESS
# axer la com sur ces genres de musique ! + campagne marketing     
## les genres de musique proposés
# quel est le genre musical le plus vendu ?  ROCK, LATIN puis METAL

def plotGenre():
    res = resTracks.groupby('genre').count()
    res = res.sort_values(by='track', ascending = False)
    fig = px.pie(res, names = res.index, values = 'Quantity')
    return fig
    
    
def genreClient():
    # genre le plus acheté pour chaque client
    genreClient = resTracks.groupby(['CustomerId', 'genre']).count().reset_index()
    genreClient = genreClient.pivot_table(values = 'Quantity', index = 'CustomerId', columns = 'genre')
    genreClient.plot()
    # nom de la colonne qui a la valeur max...
    genreClient['genreMax'] = genreClient.idxmax(axis=1)
    res = genreClient['genreMax'].value_counts()
    fig = px.bar(res)
    fig.update_layout(
        title_text='Favorite kind of music of customers',
        xaxis_title_text='Genre',
        yaxis_title_text='Number of customer')
    fig.update_traces(marker_color='grey')
    return fig

resVentes = init()
resTracks = df_resTracks()


