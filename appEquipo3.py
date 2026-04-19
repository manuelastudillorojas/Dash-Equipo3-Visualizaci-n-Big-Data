import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os

# --- 1. CONFIGURACIÓN Y CARGA SEGURA ---
st.set_page_config(page_title="Dashboard Equipo 3 - Full View", layout="wide")

@st.cache_data
def load_data():
    # Ruta dinámica para evitar el error de FileNotFoundError en el servidor
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, 'data.csv')
    df = pd.read_csv(file_path)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error al cargar el archivo: {e}")
    st.stop()

# --- 2. SIDEBAR CON FILTROS EXTENDIDOS ---
st.sidebar.header("🎛️ Panel de Control")

# Filtro 1: Rango de Fecha
date_range = st.sidebar.date_input("Rango de Fechas:", 
                                   [df['Date'].min(), df['Date'].max()])

# Filtro 2: Sucursales
sucursales = st.sidebar.multiselect("Sucursales:", 
                                    options=df["Branch"].unique(), 
                                    default=df["Branch"].unique())

# Filtro 3: Género
generos = st.sidebar.multiselect("Género:", 
                                 options=df["Gender"].unique(), 
                                 default=df["Gender"].unique())

# Filtro 4: Líneas de Producto
productos = st.sidebar.multiselect("Líneas de Producto:", 
                                   options=df["Product line"].unique(), 
                                   default=df["Product line"].unique())

# Filtro 5: Medios de Pago
pagos = st.sidebar.multiselect("Métodos de Pago:", 
                               options=df["Payment"].unique(), 
                               default=df["Payment"].unique())

# Filtro 6: Rating (Slider)
rating_range = st.sidebar.slider("Satisfacción (Rating):", 0.0, 10.0, (0.0, 10.0))

# --- APLICAR TODOS LOS FILTROS ---
df_filt = df[
    (df['Date'] >= pd.to_datetime(date_range[0])) & 
    (df['Date'] <= pd.to_datetime(date_range[1])) &
    (df['Branch'].isin(sucursales)) &
    (df['Gender'].isin(generos)) &
    (df['Product line'].isin(productos)) &
    (df['Payment'].isin(pagos)) &
    (df['Rating'].between(rating_range[0], rating_range[1]))
]

# --- 3. CABECERA Y MÉTRICAS ---
st.title("🚀 Dashboard de Operaciones - Equipo 3")
st.markdown("Vista integral de rendimiento sin pestañas para monitoreo continuo.")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Venta Total", f"${df_filt['Total'].sum():,.0f}")
m2.metric("Tickets", len(df_filt))
m3.metric("Promedio Rating", f"{df_filt['Rating'].mean():.2f}")
m4.metric("Margen Bruto", f"${df_filt['gross income'].sum():,.0f}")

st.divider()

# --- 4. CUADRÍCULA DE GRÁFICOS (2 COLUMNAS) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Tendencia de Demanda")
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    daily = df_filt.groupby('Date')['Total'].sum()
    sns.lineplot(x=daily.index, y=daily.values, ax=ax1, color="#2E86C1")
    plt.xticks(rotation=45)
    st.pyplot(fig1)

    st.subheader("3. Perfil de Gasto (Membresía)")
    fig3, ax3 = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=df_filt, x='Customer type', y='Total', hue='Customer type', palette='Set2', ax=ax3, legend=False)
    st.pyplot(fig3)

    st.subheader("5. Relación Volumen vs Rentabilidad")
    branch_agg = df_filt.groupby('Branch').agg({'Quantity':'mean', 'gross income':'mean', 'Rating':'mean'}).reset_index()
    fig5, ax5 = plt.subplots(figsize=(8, 5))
    sns.scatterplot(data=branch_agg, x='Quantity', y='gross income', size='Rating', hue='Branch', sizes=(200, 800), ax=ax5)
    st.pyplot(fig5)

    st.subheader("7. Matriz de Correlación")
    fig7, ax7 = plt.subplots(figsize=(8, 5))
    sns.heatmap(df_filt[['Unit price','Quantity','Total','gross income','Rating']].corr(), annot=True, cmap='RdBu_r', ax=ax7)
    st.pyplot(fig7)

with col2:
    st.subheader("2. Desempeño por Producto")
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    prod = df_filt.groupby('Product line')['gross income'].sum().sort_values()
    sns.barplot(x=prod.values, y=prod.index, hue=prod.index, palette='viridis', ax=ax2, legend=False)
    st.pyplot(fig2)

    st.subheader("4. Satisfacción por Sucursal")
    fig4 = sns.FacetGrid(df_filt, col="Branch", hue="Branch", palette="rocket", height=4)
    fig4.map(sns.histplot, "Rating", kde=True)
    st.pyplot(fig4.fig)

    st.subheader("6. Composición de Pagos")
    pay_ct = pd.crosstab(df_filt['Branch'], df_filt['Payment'], normalize='index')
    fig6, ax6 = plt.subplots(figsize=(8, 5))
    pay_ct.plot(kind='bar', stacked=True, ax=ax6, color=['#AED6F1','#FAD7A0','#D2B4DE'])
    plt.legend(loc='lower right', fontsize='small')
    st.pyplot(fig6)

    st.subheader("8. Síntesis: Margen por Género")
    fig8, ax8 = plt.subplots(figsize=(8, 5))
    sns.barplot(data=df_filt, x='gross income', y='Product line', hue='Gender', estimator='mean', ax=ax8)
    plt.legend(loc='lower right', fontsize='small')
    st.pyplot(fig8)
