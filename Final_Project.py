import streamlit as stl
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression ##Use to implement trendline calculation

spreadsheet = pd.ExcelFile('Density_05-01-2020.xlsx')
sheetnames = spreadsheet.sheet_names

#Make Database of ILs and properties
df_ILs = spreadsheet.parse(sheetnames[1],skiprows=4)
cation_abbrev = dict(zip(df_ILs["Abbreviations"],df_ILs["Names"]))
anion_abbrev = dict(zip(df_ILs["Abbreviations.1"],df_ILs["Names.1"]))
dict_props = {"Density":"Density (g/cm3)","Viscosity":"Viscosity (cP)"}

#Define functions used later
def get_il_family(cation):
    sheet_index = None

    for j in sheetnames[2:]: 
         if j[8:].lower() in cation_abbrev.get(cation): 
            sheet_index = (sheetnames.index(j)) 
    
    y = datasheet.parse(sheetnames[sheet_index],skiprows=2)
    y = y.dropna(axis=0,how='all')
    return y

def swap_columns(df, col1, col2): ##Snippet from https://www.statology.org/swap-columns-pandas/
    col_list = list(df.columns)
    x, y = col_list.index(col1), col_list.index(col2)
    col_list[y], col_list[x] = col_list[x], col_list[y]
    df = df[col_list]
    return df

def display_regs(df,prop_col):
    T='T'
    for k in df['Full Reference'].unique():
        short_ref = k.split(", ")[0]
        #Figure out which type of fit to use
        if prop_col=='Density (g/cm3)':
            Y = np.array(df.loc[df['Full Reference']==k][f'{prop_col}'])
            X = np.array(df.loc[df['Full Reference']==k]['T /K']).reshape(-1,1)
        else:
            Y = np.array(np.log(df.loc[df['Full Reference']==k][f'{prop_col}']))
            X = np.array(1000/(df.loc[df['Full Reference']==k]['T /K'])).reshape(-1,1)
        #FIt the model
        model = LinearRegression().fit(X,Y)
        #Choose type of equation to display
        if prop_col=='Density (g/cm3)':
            eqn = f'\u03c1_({short_ref})={model.coef_[0]:.4e}*T+{model.intercept_:.4f}'
        else:
            eqn = f'ln(\u03bc_({short_ref})=$\frac{1000*model.coef_[0]:.4f}{T}$+{model.intercept_:.4f}'
        #Display equation
        stl.latex(eqn)

#Make webapp inputs
stl.title("Brennecke Group Internal IL Database")
cation = stl.selectbox(label="Please select IL cation:",options=cation_abbrev.keys())
anion = stl.selectbox(label="Please select IL anion:",options=anion_abbrev.keys())
prop = stl.selectbox(label="Which property would you like to see?",options = ['Density','Viscosity'])
# cation = 'bmim' ##Test case cation. Also try P2224, Pyrro14, emim
# anion = 'Tf2N' ##Test case anion. Also try BF4, PF6, 2CNPyrro

#Choose property and file to read
prop_column = dict_props.get(prop)
datasheet = pd.ExcelFile(f'{prop}_05-01-2020.xlsx')
sheetnames = datasheet.sheet_names

#Get Property Data
il_input = f"[{cation}][{anion}]"
il_family = get_il_family(cation)
stl.markdown(f"This IL's full name is {cation_abbrev.get(cation)} {anion_abbrev.get(anion)}.")
       
if il_input in list(il_family['IL']):
    il_dens = il_family.loc[il_family["IL"] == il_input][['T /K',f'{prop_column}','Full Reference']]
    il_dens.replace(np.nan,None,inplace=True)
    il_dens["Ref"] = None
    for x in list(il_dens.index): 
        if il_dens["Full Reference"][x] != None:
            il_dens['Ref'][x] = il_dens["Full Reference"][x].split(", ")[0] +" et al."
        else:
             il_dens['Ref'][x] = il_dens["Full Reference"][x-1].split(", ")[0] +" et al."
    swap_columns(il_dens,f'{prop_column}','Ref')
    
    unique_refs = il_dens["Full Reference"].unique()
 
    fig = sns.lmplot(data=il_dens,x='T /K',y = f'{prop_column}', hue = 'Ref', fit_reg=False).set(title=f'{prop} of {il_input}')
    stl.pyplot(fig)
    stl.write('## Line Equations:')
    display_regs(il_dens,f'{prop_column}')
    stl.write('## Data:')
    stl.write(il_dens.drop('Ref',axis=1))
    stl.markdown('## References')
    for j in unique_refs: stl.write(j)
else:
    stl.write(f"{il_input} is currently **not** in our database. :confused: Try [ILthermo](https://ilthermo.boulder.nist.gov/)! Remember they use full IL name! :smile:")

