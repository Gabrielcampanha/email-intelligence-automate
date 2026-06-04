import streamlit as st
import pandas as pd
import sqlite3
import psycopg2
import os
import plotly.express as px
from pathlib import Path

# Configuração da Página
st.set_page_config(page_title="Email Intelligence Dashboard", page_icon="📧", layout="wide")

def is_postgres():
    db_url = os.getenv("DATABASE_URL")
    return db_url and db_url.startswith("postgres")

# Função para conectar ao banco
def get_data():
    db_url = os.getenv("DATABASE_URL")
    
    try:
        if is_postgres():
            conn = psycopg2.connect(db_url, sslmode="require")
        else:
            db_path = Path("data/emails.db")
            if not db_path.exists():
                return pd.DataFrame()
            conn = sqlite3.connect(db_path)
        
        df = pd.read_sql_query("SELECT * FROM emails ORDER BY processed_at DESC", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao ler banco de dados: {e}")
        return pd.DataFrame()

# Título
st.title("📧 Email Intelligence Dashboard")
st.markdown("Visualize as análises feitas pela IA em tempo real.")

# Carregar Dados
df = get_data()

if df.empty:
    st.warning("Nenhum e-mail processado encontrado no banco de dados. Rode o pipeline primeiro!")
else:
    # --- MÉTRICAS LATERAIS ---
    st.sidebar.header("Filtros e Métricas")
    total_emails = len(df)
    
    # Tratamento de booleano para diferentes bancos
    if is_postgres():
        urgentes = df[df['urgent'] == True].shape[0]
    else:
        urgentes = df[df['urgent'] == 1].shape[0]
    
    st.sidebar.metric("Total de E-mails", total_emails)
    st.sidebar.metric("Urgentes 🔥", urgentes)
    
    # Filtro de Categoria
    categorias = ["Todas"] + list(df['category'].unique())
    cat_filter = st.sidebar.selectbox("Filtrar por Categoria", categorias)
    
    df_filtered = df if cat_filter == "Todas" else df[df['category'] == cat_filter]

    # --- GRÁFICOS ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribuição por Categoria")
        fig_cat = px.pie(df, names='category', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_cat, use_container_width=True)
        
    with col2:
        st.subheader("Urgência dos E-mails")
        # Conta valores de urgência
        urgent_counts = df['urgent'].value_counts().reset_index()
        urgent_counts.columns = ['Status', 'Quantidade']
        
        # Mapeamento dinâmico para booleano/inteiro
        if is_postgres():
            urgent_counts['Status'] = urgent_counts['Status'].map({True: 'Urgente', False: 'Normal'})
        else:
            urgent_counts['Status'] = urgent_counts['Status'].map({1: 'Urgente', 0: 'Normal'})
        
        fig_urg = px.bar(urgent_counts, x='Status', y='Quantidade', color='Status', 
                         color_discrete_map={'Urgente': '#ef553b', 'Normal': '#636efa'})
        st.plotly_chart(fig_urg, use_container_width=True)

    # --- TABELA DE DADOS ---
    st.subheader("📋 Últimos E-mails Analisados")
    
    # Formatando a exibição da tabela
    display_df = df_filtered[['processed_at', 'sender', 'category', 'urgent', 'summary', 'recommended_action']].copy()
    
    if is_postgres():
        display_df['urgent'] = display_df['urgent'].map({True: '🚨 SIM', False: '✅ NÃO'})
    else:
        display_df['urgent'] = display_df['urgent'].map({1: '🚨 SIM', 0: '✅ NÃO'})
    
    st.dataframe(display_df, use_container_width=True)

    # --- DETALHES AO CLICAR ---
    st.subheader("🔍 Detalhes da Recomendação")
    selected_email = st.selectbox("Selecione um assunto para ver o detalhe:", df_filtered['subject'])
    
    if selected_email:
        row = df_filtered[df_filtered['subject'] == selected_email].iloc[0]
        st.info(f"**Resumo da IA:** {row['summary']}")
        st.success(f"**Ação Sugerida:** {row['recommended_action']}")

# Botão de Atualizar
if st.button("Atualizar Dados"):
    st.rerun()
