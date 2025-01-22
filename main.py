# LES LIBRAIRIES
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.offline import plot
import plotly.graph_objects as go

pd.set_option('future.no_silent_downcasting', True)


# Mes fonctions
def etl_format_input(df):
    # Convertir les colonnes en numérique et gérer les valeurs manquantes
    df = df.apply(pd.to_numeric, errors='coerce')
    # Liste des mois pour référence
    mois_noms = df.columns.tolist()
    mois_noms = [mois for mois in mois_noms
                 if mois != "Jour"]  # Exclure la colonne "Jour" si elle existe
    # Générer les dates et les températures
    dates = []
    temperatures = []
    for month_idx, month in enumerate(mois_noms):
        for day_idx, temp in enumerate(df[month]):
            try:
                # Créer une date pour chaque jour
                date = pd.Timestamp(year=2018,
                                    month=month_idx + 1,
                                    day=day_idx + 1)
                dates.append(date.strftime("%d/%m/%Y"))
                temperatures.append(temp)
            except ValueError:
                # Ignorer les jours invalides
                continue
    # Créer un DataFrame avec les colonnes souhaitées
    df_transformed = pd.DataFrame({"Date": dates, "Temperature": temperatures})
    df_transformed["Date"] = pd.to_datetime(df_transformed['Date'],
                                            format="%d/%m/%Y")
    df_transformed = df_transformed.set_index('Date')
    return df_transformed


def etl_format_observatoire(df):
    # Convertir les colonnes en numérique et gérer les valeurs manquantes
    df["Temperature"] = df["Air temperature (degC)"].apply(pd.to_numeric,
                                                           errors='coerce')
    # Générer les dates et les températures
    df["Date"] = pd.to_datetime({
        'year': df['Year'],
        'month': df['m'],
        'day': df['d']
    })
    # Créer un DataFrame avec les colonnes souhaitées
    df_transformed = pd.DataFrame({
        "Date": df["Date"],
        "Temperature": df["Temperature"]
    })
    df_transformed = df_transformed.set_index('Date')
    return df_transformed


def etl_format_opendata(df):
    # Supprime les données non utilisées (Non Europe et Non 2018)
    drop_condition = (df["Region"] != "Europe") | (df["Year"] != 2018)
    df.drop(df[drop_condition].index, inplace=True)
    # Convertir les colonnes en numérique et gérer les valeurs manquantes
    df["Temperature"] = df["AvgTemperature"].apply(pd.to_numeric,
                                                   errors='coerce')
    # Convertion °F en °C
    df["Temperature"] = round((df["Temperature"] - 32) * 5 / 9, 1)
    # Générer les dates et les températures
    df["Date"] = pd.to_datetime({
        'year': df['Year'],
        'month': df['Month'],
        'day': df['Day']
    })
    df["Ville"] = df["City"]
    # Créer un DataFrame avec les colonnes souhaitées
    df_transformed = pd.DataFrame({
        "Date": df["Date"],
        "Temperature": df["Temperature"],
        "Ville": df["Ville"]
    })
    return df_transformed


def standardize(df):
    # Range les dates dans l'ordre chronologique
    df.sort_values(by="Date", inplace=True)
    # Convertir la colonne en numérique, forcer les erreurs à NaN
    df["Temperature"] = pd.to_numeric(df["Temperature"], errors='coerce')
    # Remplace par Nan si valeur trop extreme
    df.loc[df["Temperature"] > 50,
           "Temperature"] = np.nan  # Syracuse Italie 48.8 en 2021
    df.loc[df["Temperature"] < -60,
           "Temperature"] = np.nan  # Oust-Chtchougor Russie en 1978
    # Remplace par NaN si  valeur trop extreme en local (+/- 17 par rapport aux valeurs de proximité)
    diff_precedente = df["Temperature"].diff().abs()
    diff_suivante = df["Temperature"].shift(-1).diff().abs()
    condition = (diff_precedente > 17) | (diff_suivante > 17)
    df.loc[condition, "Temperature"] = np.nan
    # Remplacer les NaN (valeurs non numériques) par la moyenne des valeurs à proximitées
    df["Temperature"].interpolate(method='linear', inplace=True)
    return df


# Les dataframmes
url_part = 'import/tableau_erreur.csv'
url_full = 'import/tableau.csv'
url_observatoire = 'import/observatoire.csv'
url_opendata = 'import/city_temperature.csv'

# Charger les fichiers CSV dans des DataFrames
df_full = etl_format_input(pd.read_csv(url_full))
df_part = etl_format_input(pd.read_csv(url_part))
df_observatoire = etl_format_observatoire(pd.read_csv(url_observatoire))
df_opendata = etl_format_opendata(
    pd.read_csv(url_opendata,
                dtype={
                    "Region": "string",
                    "Country": "string",
                    "Sate": "string",
                    "City": "string",
                    "Month": "int",
                    "Day": "int",
                    "Year": "int",
                    "AvgTemperature": float
                }))
standardize(df_full)
standardize(df_part)
standardize(df_observatoire)
standardize(df_opendata)

# Moyenne par mois
mean_full = df_full.groupby(pd.Grouper(freq='ME'))['Temperature'].mean()
mean_part = df_part.groupby(pd.Grouper(freq='ME'))['Temperature'].mean()

# Min & Max par mois
stats_full = df_full.groupby(pd.Grouper(freq='ME'))['Temperature'].agg(
    ['min', 'max'])
stats_part = df_part.groupby(pd.Grouper(freq='ME'))['Temperature'].agg(
    ['min', 'max'])

# Min & Max par an
stats_full_annual = df_full.agg(['min', 'max'])
stats_part_annual = df_part.agg(['min', 'max'])

# Ecart type par mois
std_full = df_full.std()
std_part = df_part.std()

# Afficher les résultats
print(
    f"\nStatistiques (moyenne par mois) pour le DataFrame complet : \n{mean_full}"
)
print(
    f"\nStatistiques (moyenne par mois) pour le DataFrame incomplet : \n{mean_part}"
)
print(
    f"\nStatistiques (min et max par mois) pour le DataFrame complet : \n{stats_full}"
)
print(
    f"\nStatistiques (min et max par mois) pour le DataFrame incomplet : \n{stats_part}"
)
print(
    f"\nStatistiques (min et max par an) pour le DataFrame complet : \n{stats_full_annual}"
)
print(
    f"\nStatistiques (min et max par an) pour le DataFrame incomplet : \n{stats_part_annual}"
)
print(f"\nÉcart-type pour le DataFrame complet : \n{std_full}")
print(f"\nÉcart-type pour le DataFrame incomplet : \n{std_part}")

nomMois = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août",
    "Septembre", "Octobre", "Novembre", "Décembre"
]

# Init Graph Full
df_full_graph = pd.DataFrame({
    "Date": df_full.index,
    "Jour": df_full.index.day,
    "Mois": df_full.index.month - 1,
    "Temperature": df_full["Temperature"]
})
df_full_graph["Mois"] = df_full_graph['Mois'].apply(lambda x: nomMois[x])
df_full_graph = df_full_graph.set_index('Date')

# Première figure : Températures par mois
fig1 = px.line(df_full_graph,
               x='Jour',
               y='Temperature',
               color='Mois',
               title="Courbes des températures par mois",
               labels={
                   'Jour': 'Jour',
                   'Temperature': 'Température (°C)',
                   'Mois': 'Mois'
               },
               hover_data={
                   'Jour': True,
                   'Mois': True,
                   'Temperature': True
               })

# Deuxième figure : Températures sur l'année entière
fig2 = px.line(df_full_graph,
               x=df_full_graph.index,
               y='Temperature',
               title="Températures sur l'année entière",
               labels={
                   'index': 'Jours (1 à 365)',
                   'Temperature': 'Température (°C)'
               },
               hover_data={
                   'Jour': True,
                   'Mois': True,
                   'Temperature': True
               })

# Init Graph Part
df_part_graph = pd.DataFrame({
    "Date": df_part.index,
    "Jour": df_part.index.day,
    "Mois": df_part.index.month - 1,
    "Temperature": df_part["Temperature"]
})
df_part_graph["Mois"] = df_part_graph['Mois'].apply(lambda x: nomMois[x])
df_part_graph = df_part_graph.set_index('Date')

df_observatoire_graph = pd.DataFrame({
    "Date":
    df_observatoire.index,
    "Jour":
    df_observatoire.index.day,
    "Mois":
    df_observatoire.index.month - 1,
    "Temperature":
    df_observatoire["Temperature"]
})
df_observatoire_graph["Mois"] = df_observatoire_graph['Mois'].apply(
    lambda x: nomMois[x])
df_observatoire_graph = df_observatoire_graph.set_index('Date')

# Troisième figure : Températures par mois
fig3 = px.line(df_part_graph,
               x='Jour',
               y='Temperature',
               color='Mois',
               title="Courbes des températures par mois",
               labels={
                   'Jour': 'Jour',
                   'Temperature': 'Température (°C)',
                   'Mois': 'Mois'
               },
               hover_data={
                   'Jour': True,
                   'Mois': True,
                   'Temperature': True
               })

# Quatrième figure : Températures sur l'année entière
fig4 = px.line(df_part_graph,
               x=df_part_graph.index,
               y='Temperature',
               title="Températures sur l'année entière",
               labels={
                   'index': 'Jours (1 à 365)',
                   'Température': 'Température (°C)'
               },
               hover_data={
                   'Jour': True,
                   'Mois': True,
                   'Temperature': True
               })

# Graph de comparaison
df_full_graph["datasource"] = "cible propre"
df_part_graph["datasource"] = "cible réel"
df_observatoire_graph["datasource"] = "observatoire Finlande"
df_full_graph.reset_index(inplace=True)
df_part_graph.reset_index(inplace=True)
df_observatoire_graph.reset_index(inplace=True)

df_graph5 = pd.concat([df_full_graph, df_part_graph, df_observatoire_graph],
                      ignore_index=True)

fig5 = px.line(df_graph5,
               x=df_graph5["Date"],
               y='Temperature',
               color='datasource',
               title="Températures sur l'année entière",
               labels={
                   'index': 'Jours (1 à 365)',
                   'Température': 'Température (°C)'
               },
               hover_data={
                   'Jour': True,
                   'Mois': True,
                   'Temperature': True
               })

df_opendata_graph = pd.DataFrame({
    "Date": df_opendata["Date"],
    "Jour": df_opendata["Date"].dt.day,
    "Mois": df_opendata["Date"].dt.month - 1,
    "Temperature": df_opendata["Temperature"],
    "Ville": df_opendata["Ville"]
})
df_opendata_graph["Mois"] = df_opendata_graph['Mois'].apply(
    lambda x: nomMois[x])
df_part_graph["Ville"] = "Ville Mystère"

df_graph6 = pd.concat([df_opendata_graph, df_part_graph], ignore_index=True)

print(df_opendata_graph["Date"].head())

fig6 = px.line(df_graph6,
               x=df_graph6["Date"],
               y='Temperature',
               color='Ville',
               title="Températures sur l'année entière",
               labels={
                   'index': 'Jours (1 à 365)',
                   'Température': 'Température (°C)'
               },
               hover_data={
                   'Jour': True,
                   'Mois': True,
                   'Temperature': True
               })

fig1.write_html("export/fig1_courbes_par_mois.html")
fig2.write_html("export/fig2_temps_annee_entiere.html")
fig3.write_html("export/fig3_courbes_par_mois.html")
fig4.write_html("export/fig4_temps_annee_entiere.html")
fig5.write_html("export/fig5_temps_annee_comparatif.html")
fig6.write_html("export/fig6_temps_annee_europe.html")
print("Les graphiques ont été sauvegardés en tant que fichiers HTML.")
print("Téléchargez-les ou ouvrez-les dans un navigateur.")

# Fusionner les deux DataFrames sur la colonne 'date'
merged_df = pd.merge(df_opendata_graph, df_part, on='Date', suffixes=('_df1', '_df2'))

# Calculer la différence absolue entre les températures
merged_df['diff'] = np.abs(merged_df['Temperature_df1'] - merged_df['Temperature_df2'])

# Calculer la somme des différences par ville
diff_by_city = merged_df.groupby('Ville')['diff'].sum()

print("Top 10 des villes les plus proches en terme de température : ", diff_by_city.sort_values().head(10))
# Trouver la ville avec la différence minimale (le meilleur match)
best_match_city = diff_by_city.idxmin()
print(f"La ville qui match le plus avec le DataFrame de référence est : {best_match_city}")