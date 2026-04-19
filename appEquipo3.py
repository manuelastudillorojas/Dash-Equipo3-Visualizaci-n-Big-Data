import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# --- 1. CONFIGURACIÓN Y CARGA DE DATOS ---
st.set_page_config(page_title="Dashboard Integral ZOFRI-Supermarket", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('dataset_lab_3.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# --- 2. SIDEBAR (FILTROS INTERACTIVOS) ---
st.sidebar.header("🎯 Filtros Globales")

# Filtro de Fecha (Rango)
min_date = df['Date'].min()
max_date = df['Date'].max()
date_range = st.sidebar.date_input("Rango de Fechas:", [min_date, max_date], min_value=min_date, max_value=max_date)

# Filtro de Sucursal
sucursales = st.sidebar.multiselect("Sucursales:", options=df["Branch"].unique(), default=df["Branch"].unique())

# Filtro de Rating (Slider)
rating_range = st.sidebar.slider("Rango de Rating (Satisfacción):", 0.0, 10.0, (0.0, 10.0))

# --- APLICAR FILTROS ---
mask = (df['Date'] >= pd.to_datetime(date_range[0])) & \
       (df['Date'] <= pd.to_datetime(date_range[1])) & \
       (df['Branch'].isin(sucursales)) & \
       (df['Rating'].between(rating_range[0], rating_range[1]))
df_filt = df.loc[mask]

# --- 3. DISEÑO DEL DASHBOARD ---
st.title("🚀 Business Intelligence Dashboard: Supermarket Sales")
st.markdown("Análisis multidimensional de operaciones y clientes.")

# Métricas rápidas
m1, m2, m3, m4 = st.columns(4)
m1.metric("Ventas Totales", f"${df_filt['Total'].sum():,.0f}")
m2.metric("Transacciones", len(df_filt))
m3.metric("Promedio Rating", f"{df_filt['Rating'].mean():.2f}")
m4.metric("Ingreso Bruto", f"${df_filt['gross income'].sum():,.0f}")

# --- 4. ORGANIZACIÓN DE LOS 8 ANÁLISIS ---
tabs = st.tabs([f"Análisis {i}" for i in range(1, 9)])

# Análisis 1: Tiempo
with tabs[0]:
    st.subheader("1. Patrones Temporales de Demanda")
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    daily = df_filt.groupby('Date')['Total'].sum()
    sns.lineplot(x=daily.index, y=daily.values, ax=ax1, color="#2E86C1")
    st.pyplot(fig1)

# Análisis 2: Portafolio
with tabs[1]:
    st.subheader("2. Rendimiento del Portafolio")
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    prod = df_filt.groupby('Product line')['gross income'].sum().sort_values()
    sns.barplot(x=prod.values, y=prod.index, hue=prod.index, palette='viridis', ax=ax2, legend=False)
    st.pyplot(fig2)

# Análisis 3: Fidelización
with tabs[2]:
    st.subheader("3. Perfil del Cliente (Membresía)")
    fig3, ax3 = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=df_filt, x='Customer type', y='Total', hue='Customer type', palette='Set2', ax=ax3, legend=False)
    st.pyplot(fig3)

# Análisis 4: Calidad
with tabs[3]:
    st.subheader("4. Diagnóstico de Satisfacción (Rating)")
    fig4 = sns.FacetGrid(df_filt, col="Branch", hue="Branch", palette="rocket")
    fig4.map(sns.histplot, "Rating", kde=True)
    st.pyplot(fig4.fig)

# Análisis 5: Radiografía Multidimensional
with tabs[4]:
    st.subheader("5. Comparativa de Sucursales (Multidimensional)")
    branch_agg = df_filt.groupby('Branch').agg({'Quantity':'mean', 'gross income':'mean', 'Rating':'mean'}).reset_index()
    fig5, ax5 = plt.subplots()
    sns.scatterplot(data=branch_agg, x='Quantity', y='gross income', size='Rating', hue='Branch', sizes=(100, 500), ax=ax5)
    st.pyplot(fig5)

# Análisis 6: Medios de Pago
with tabs[5]:
    st.subheader("6. Preferencias de Pago por Sucursal")
    pay_ct = pd.crosstab(df_filt['Branch'], df_filt['Payment'], normalize='index')
    fig6, ax6 = plt.subplots()
    pay_ct.plot(kind='bar', stacked=True, ax=ax6, color=['#AED6F1','#FAD7A0','#D2B4DE'])
    st.pyplot(fig6)

# Análisis 7: Relaciones
with tabs[6]:
    st.subheader("7. Matriz de Correlación de Variables")
    fig7, ax7 = plt.subplots()
    sns.heatmap(df_filt[['Unit price','Quantity','Total','gross income','Rating']].corr(), annot=True, cmap='RdBu_r', ax=ax7)
    st.pyplot(fig7)

# Análisis 8: Síntesis Libre
with tabs[7]:
    st.subheader("8. Síntesis: Gasto Promedio Género vs Producto")
    fig8, ax8 = plt.subplots()
    sns.barplot(data=df_filt, x='gross income', y='Product line', hue='Gender', estimator='mean', ax=ax8)
    st.pyplot(fig8)