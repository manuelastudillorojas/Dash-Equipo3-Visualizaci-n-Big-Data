import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os

# --- 1. CONFIGURACIÓN Y CARGA SEGURA ---
st.set_page_config(page_title="Dashboard Operaciones - Equipo 3", layout="wide")

@st.cache_data
def load_data():
    # Ruta dinámica para carga automática del archivo data.csv
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, 'data.csv')
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error crítico: No se encontró 'data.csv' o el formato es incorrecto. {e}")
    st.stop()

# --- 2. SIDEBAR CON FILTROS ---
st.sidebar.header("🎛️ Panel de Control")

# Rango de Fecha
date_range = st.sidebar.date_input("Rango de Fechas:", [df['Date'].min(), df['Date'].max()])

# Resto de filtros
sucursales = st.sidebar.multiselect("Sucursales:", options=df["Branch"].unique(), default=df["Branch"].unique())
generos = st.sidebar.multiselect("Género:", options=df["Gender"].unique(), default=df["Gender"].unique())
productos = st.sidebar.multiselect("Líneas de Producto:", options=df["Product line"].unique(), default=df["Product line"].unique())
pagos = st.sidebar.multiselect("Métodos de Pago:", options=df["Payment"].unique(), default=df["Payment"].unique())
rating_range = st.sidebar.slider("Satisfacción (Rating):", 0.0, 10.0, (0.0, 10.0))

# Aplicar Filtros
mask = (
    (df['Date'] >= pd.to_datetime(date_range[0])) & 
    (df['Date'] <= pd.to_datetime(date_range[1])) &
    (df['Branch'].isin(sucursales)) &
    (df['Gender'].isin(generos)) &
    (df['Product line'].isin(productos)) &
    (df['Payment'].isin(pagos)) &
    (df['Rating'].between(rating_range[0], rating_range[1]))
)
df_filt = df.loc[mask]

# --- 3. CABECERA Y KPIs ---
st.title("🚀 Dashboard de Operaciones - Equipo 3")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Venta Total", f"${df_filt['Total'].sum():,.0f}")
m2.metric("Tickets", len(df_filt))
m3.metric("Promedio Rating", f"{df_filt['Rating'].mean():.2f}")
m4.metric("Ingreso Bruto", f"${df_filt['gross income'].sum():,.0f}")

st.divider()

# --- 4. CUADRÍCULA DE GRÁFICOS ---
col1, col2 = st.columns(2)

with col1:
    # 1. Tendencia Diaria
    st.subheader("📈 Evolución Diaria de Ventas")
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    daily = df_filt.groupby('Date')['Total'].sum().reset_index()
    sns.lineplot(data=daily, x='Date', y='Total', color='#2C5F8A', linewidth=1.8, ax=ax1)
    plt.xticks(rotation=30)
    sns.despine()
    st.pyplot(fig1)

    # 3. Boxplot de Gasto
    st.subheader("👥 Gasto por Tipo de Cliente")
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=df_filt, x='Customer type', y='Total', hue='Customer type', 
                palette={'Member': '#2C5F8A', 'Normal': '#A8C4D4'}, ax=ax3, legend=False)
    sns.despine()
    st.pyplot(fig3)

    # 5. Scatter Multidimensional
    st.subheader("🎯 Desempeño por Sucursal (Promedios)")
    branch_agg = df_filt.groupby('Branch').agg({'Quantity':'mean', 'gross income':'mean', 'Rating':'mean'}).reset_index()
    fig5, ax5 = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=branch_agg, x='Quantity', y='gross income', size='Rating', hue='Branch', 
                    sizes=(300, 1200), palette={'A': '#2C5F8A', 'B': '#5B8DB8', 'C': '#A8C4D4'}, ax=ax5)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    sns.despine()
    st.pyplot(fig5)

    # 7. Matriz de Correlación
    st.subheader("🔗 Correlación de Variables")
    fig7, ax7 = plt.subplots(figsize=(10, 6))
    cols_corr = ['Unit price', 'Quantity', 'Total', 'gross income', 'Rating']
    corr = df_filt[cols_corr].corr()
    mask_tri = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask_tri, annot=True, cmap='Blues', fmt=".2f", ax=ax7)
    st.pyplot(fig7)

with col2:
    # 2. Desempeño Producto
    st.subheader("💰 Ingreso por Línea de Producto")
    prod_perf = df_filt.groupby('Product line')['gross income'].sum().sort_values().reset_index()
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.barplot(data=prod_perf, x='gross income', y='Product line', palette='Blues_r', ax=ax2)
    sns.despine()
    st.pyplot(fig2)

    # 4. Satisfacción por Sucursal
    st.subheader("⭐ Satisfacción por Sucursal")
    g = sns.FacetGrid(df_filt, col="Branch", hue="Branch", palette={'A': '#2C5F8A', 'B': '#5B8DB8', 'C': '#A8C4D4'}, height=4)
    g.map(sns.histplot, "Rating", kde=True)
    st.pyplot(g.fig)

    # 6. Medios de Pago con Etiquetas
    st.subheader("💳 Preferencia de Pago por Sucursal")
    pay_branch = pd.crosstab(df_filt['Branch'], df_filt['Payment'], normalize='index') * 100
    fig6, ax6 = plt.subplots(figsize=(10, 6))
    pay_branch.plot(kind='barh', stacked=True, color=['#2C5F8A', '#5B8DB8', '#A8C4D4'], ax=ax6)
    for n, x in enumerate([*pay_branch.index.values]):
        for (proportion, y_loc) in zip(pay_branch.loc[x], pay_branch.loc[x].cumsum()):
            ax6.text(x=(y_loc - proportion/2), y=n, s=f'{np.round(proportion, 1)}%', 
                     color='white', fontweight='bold', ha='center', va='center', fontsize=9)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    sns.despine()
    st.pyplot(fig6)

    # 8. Margen por Género
    st.subheader("👫 Ingreso Promedio por Género")
    fig8, ax8 = plt.subplots(figsize=(10, 5))
    sns.barplot(data=df_filt, x='gross income', y='Product line', hue='Gender', 
                estimator='mean', palette={'Female': '#2C5F8A', 'Male': '#A8C4D4'}, ax=ax8)
    plt.legend(loc='lower right')
    sns.despine()
    st.pyplot(fig8)
