# LES LIBRAIRIES
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.offline import plot

# Mes fonctions
def standardize(df):
    for column in df.columns:
        # Convertir la colonne en numérique, forcer les erreurs à NaN
        df[column] = pd.to_numeric(df[column], errors='coerce')
        # Remplace par Nan si valeur trop extreme
        df.loc[df[column] > 50, column] = np.nan
        df.loc[df[column] < -30, column] = np.nan     
        # Remplace par NaN si  valeur trop extreme en local (+/- 15 par rapport aux valeurs de proximité)
        diff_precedente = df[column].diff().abs()
        diff_suivante = df[column].shift(-1).diff().abs()
        condition = (diff_precedente > 15) | (diff_suivante > 15)
        df.loc[condition, column] = np.nan
        # Remplacer les NaN (valeurs non numériques) par la moyenne de la colonne
        mean_value = df[column].mean()
        df[column].fillna(mean_value, inplace=True)
    return df

# Les dataframmes
url_part = 'import/tableau_erreur.csv'
url_full = 'import/tableau.csv'

# Charger les fichiers CSV dans des DataFrames
df_full = pd.read_csv(url_full)
df_full = df_full.apply(pd.to_numeric)
df_part = pd.read_csv(url_part)
standardize(df_part)

# Moyenne par mois
mean_full = df_full.mean()
mean_part = df_part.mean()

# Min & Max par mois
stats_full = df_full.agg(['min', 'max'])
stats_part = df_part.agg(['min', 'max'])

# Min & Max par an
df_concat_mois_full = pd.concat([
    df_full["janvier"], df_full["février"], df_full["mars"], df_full["avril"],
    df_full["mai"], df_full["juin"], df_full["juillet"], df_full["août"],
    df_full["septembre"], df_full["octobre"], df_full["novembre"],
    df_full["décembre"]
], ignore_index=True)
stats_full_annual = df_concat_mois_full.agg(['min', 'max'])
df_concat_mois_part = pd.concat([
    df_part["janvier"], df_part["février"], df_part["mars"], df_part["avril"],
    df_part["mai"], df_part["juin"], df_part["juillet"], df_part["août"],
    df_part["septembre"], df_part["octobre"], df_part["novembre"],
    df_part["décembre"]
], ignore_index=True)
stats_part_annual = df_concat_mois_part.agg(['min', 'max'])

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

# Charger les données (assurez-vous que df_full est correctement défini)
# Remplir les valeurs manquantes par la moyenne des colonnes
df_full = df_full.fillna(df_full.mean())

# Restructurer les données pour un format long
df_full['Jour'] = df_full.index + 1  # Ajouter une colonne pour les jours
df_long = df_full.melt(id_vars=['Jour'], var_name='Mois', value_name='Température')

# Première figure : Températures par mois
fig1 = px.line(
    df_long,
    x='Jour',
    y='Température',
    color='Mois',
    title="Courbes des températures par mois",
    labels={'Jour': 'Jour', 'Température': 'Température (°C)', 'Mois': 'Mois'},
    hover_data={'Jour': True, 'Mois': True, 'Température': True}
)

# Deuxième figure : Températures sur l'année entière
fig2 = px.line(
    df_long,
    x=df_long.index,
    y='Température',
    title="Températures sur l'année entière",
    labels={'index': 'Jours (1 à 365)', 'Température': 'Température (°C)'},
    hover_data={'Jour': True, 'Mois': True, 'Température': True}
)

# Sauvegarder les graphiques comme fichiers HTML
fig1.write_html("export/fig1_courbes_par_mois.html")
fig2.write_html("export/fig2_temps_annee_entiere.html")

print("Les graphiques ont été sauvegardés en tant que fichiers HTML.")
print("Téléchargez-les ou ouvrez-les dans un navigateur.")


#DF_PART

# Remplacer les valeurs non numériques par NaN et interpoler les données manquantes
df_part = df_part.apply(pd.to_numeric, errors='coerce')
df_part = df_part.interpolate(method='linear', axis=0)

# Ajouter une colonne pour les jours
df_part['Jour'] = df_part.index + 1

# Restructurer les données pour un format long
df_long = df_part.melt(id_vars=['Jour'], var_name='Mois', value_name='Température')

# Troisième figure : Températures par mois
fig3 = px.line(
    df_long,
    x='Jour',
    y='Température',
    color='Mois',
    title="Courbes des températures par mois",
    labels={'Jour': 'Jour', 'Température': 'Température (°C)', 'Mois': 'Mois'},
    hover_data={'Jour': True, 'Mois': True, 'Température': True}
)

# Quatrième figure : Températures sur l'année entière
fig4 = px.line(
    df_long,
    x=df_long.index,
    y='Température',
    title="Températures sur l'année entière",
    labels={'index': 'Jours (1 à 365)', 'Température': 'Température (°C)'},
    hover_data={'Jour': True, 'Mois': True, 'Température': True}
)

# Sauvegarder les graphiques comme fichiers HTML
fig3.write_html("export/fig3_courbes_par_mois.html")
fig4.write_html("export/fig4_temps_annee_entiere.html")

print("Les graphiques ont été sauvegardés en tant que fichiers HTML.")
print("Téléchargez-les ou ouvrez-les dans un navigateur.")