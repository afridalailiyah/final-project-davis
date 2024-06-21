import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import mysql.connector

# Fungsi untuk mendapatkan koneksi ke database MySQL
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="kubela.id",
            user="davis2024irwan",
            password="wh451n9m@ch1n3",
            database="aw"
        )
        return connection
    except mysql.connector.Error as err:
        st.error(f"Error connecting to the database: {err}")
        return None

# Fungsi untuk load data dari IMDb (IMDB)
@st.cache
def load_imdb_data():
    data = pd.read_csv("imdb_usmovie.csv")
    return data

# Fungsi untuk memuat data dari AdventureWorks DATASET (contoh SQL Server)
@st.cache(allow_output_mutation=True)
def load_aw_data():
    # Koneksi ke database AdventureWorks DATASET
    mydb = get_db_connection()

    if mydb is not None:
        try:
            # Query untuk mengambil data sesuai kebutuhan
            query_donut = """
            SELECT 
                dc.CurrencyName AS Currency,
                COUNT(fis.SalesOrderNumber) AS SalesCount
            FROM 
                factinternetsales fis
            JOIN 
                dimcurrency dc ON fis.CurrencyKey = dc.CurrencyKey
            GROUP BY 
                dc.CurrencyName;
            """

            query_scatter = """
            SELECT 
                NumberEmployees, 
                AnnualSales 
            FROM 
                dimreseller
            WHERE 
                NumberEmployees IS NOT NULL AND AnnualSales IS NOT NULL;
            """

            query_hist = "SELECT YearlyIncome FROM dimcustomer"

            query_bar = """
            SELECT 
                g.City, 
                COUNT(c.CustomerKey) AS CustomerCount
            FROM 
                dimcustomer c
            JOIN 
                dimgeography g ON c.GeographyKey = g.GeographyKey
            GROUP BY 
                g.City
            ORDER BY 
                CustomerCount DESC
            LIMIT 10;
            """

            # Baca data dari database
            df_donut = pd.read_sql(query_donut, mydb)
            df_scatter = pd.read_sql(query_scatter, mydb)
            df_hist = pd.read_sql(query_hist, mydb)
            df_bar = pd.read_sql(query_bar, mydb)

            return df_donut, df_scatter, df_hist, df_bar
        
        except mysql.connector.Error as err:
            st.error(f"MySQL error: {err}")
            return None, None, None, None
        finally:
            mydb.close()
    else:
        return None, None, None, None


# Sidebar untuk memilih dataset
st.sidebar.title('Please Filter Here ')
dataset = st.sidebar.selectbox('Select Category', ('AdventureWorks DATASET', 'IMDB DATASET'))

# Sidebar untuk memilih tipe chart
tipe_chart = st.sidebar.selectbox('Type Chart', ('Comparison', 'Distribution', 'Composition', 'Relationship'))

# Memuat data sesuai pilihan dataset
if dataset == 'IMDB DATASET':
    data = load_imdb_data()
    st.title('A Dashboard for an IMDb Dataset')  # Judul untuk dataset IMDB
elif dataset == 'AdventureWorks DATASET':
    df_donut, df_scatter, df_hist, df_bar = load_aw_data()
    st.title('A Dashboard of AdventureWorks  Dataset')  # Judul untuk dataset AdventureWorks DATASET


# Menampilkan chart sesuai pilihan tipe chart
if tipe_chart == 'Comparison':
    if dataset == 'IMDB DATASET':
        st.subheader('Comparison (Bar Chart)')
        fig1 = px.bar(data, x='Name', y='Rating', title='Comparison by Rating')
        st.plotly_chart(fig1)

        st.write("DESCRIPTION")
        st.write("📊 The visualization uses a chart to display how ratings vary among various films.")
        st.write("📊 Every bar on the chart represents a film, and the height of each bar shows its respective rating.")
        st.write("📊 The chart helps user to compare the ratings of different films by looking at this chart.")
        
    elif dataset == 'AdventureWorks DATASET':
        st.subheader('Comparison (Bar Chart)')
        fig_bar = px.bar(df_bar, x='City', y='CustomerCount', title='Jumlah Customer Berdasarkan Kota (Top 10)')
        st.plotly_chart(fig_bar)
        
        st.write("DESCRIPTION")
        st.write("📊 The chart displays the number of customers for the top 10 cities. Each bar in the chart represents a city, and its size indicates the number of customers in that city.")
        st.write("📊 The information is centered on the top ten cities with the most customers.")
        st.write("📊 The chart facilitates straightforward comparisons of customer volumes across various cities.")
        st.write("📊 It's categorized as comparison because each bar's height shows how many customers each city has, making it easy to see which cities have more or fewer customers at a glance.")
        st.write("📊 This chart displays based on data from the AdventureWorks database.")

elif tipe_chart == 'Distribution':
    if dataset == 'IMDB DATASET':
        st.subheader('Distribution (Scatter Plot)')
        fig2 = px.scatter(data, x='Gross_US', y='Budget', title='Gross US X Budget')
        st.plotly_chart(fig2)
    elif dataset == 'AdventureWorks DATASET':
        st.subheader('Distribution (Histogram)')
        fig_hist = px.histogram(df_hist, x='YearlyIncome', nbins=30, title='Distribusi Pendapatan Tahunan Pelanggan')
        fig_hist.update_layout(
            xaxis_title='Pendapatan Tahunan',
            yaxis_title='Jumlah Pelanggan',
            bargap=0.1
        )
        st.plotly_chart(fig_hist)

elif tipe_chart == 'Composition':
    if dataset == 'IMDB DATASET':
        st.subheader('Composition (Donut Chart)')
        composition = data['Rating'].value_counts(normalize=True) * 100
        labels = composition.index.tolist()
        values = composition.values.tolist()
        fig3 = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)])
        fig3.update_traces(textposition='inside', textinfo='percent+label')
        fig3.update_layout(title='Rating Composition')
        st.plotly_chart(fig3)
    elif dataset == 'AdventureWorks DATASET':
        st.subheader('Composition (Donut Chart)')
        fig_donut = px.pie(df_donut, values='SalesCount', names='Currency', title='Komposisi Penjualan Berdasarkan Mata Uang',
                        hole=0.3, labels={'SalesCount': 'Jumlah Penjualan', 'Currency': 'Mata Uang'})
        st.plotly_chart(fig_donut)

elif tipe_chart == 'Relationship':
    if dataset == 'IMDB DATASET':
        st.subheader('Relationship (Scatter Plot)')
        fig4 = px.scatter(data, x='Name', y='Gross_US', hover_data=['Rating', 'Budget', 'Opening_Week', 'Durasi(Menit)'],
                          title='Name X Gross US')
        st.plotly_chart(fig4)
    elif dataset == 'AdventureWorks DATASET':
        st.subheader('Relationship (Scatter Plot)')
        fig_scatter = px.scatter(df_scatter, x='NumberEmployees', y='AnnualSales',
                                 title='Relationship between Number of Employees and Annual Sales',
                                 labels={'NumberEmployees': 'Number of Employees', 'AnnualSales': 'Annual Sales'})
        fig_scatter.update_layout(xaxis_title='Number of Employees', yaxis_title='Annual Sales')
        st.plotly_chart(fig_scatter)
