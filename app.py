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

# Fungsi untuk memuat data dari AdventureWorks (contoh SQL Server)
@st.cache(allow_output_mutation=True)
def load_aw_data():
    # Koneksi ke database AdventureWorks
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

# Streamlit App
st.title('Dashboard Visualisasi Data')

# Sidebar untuk memilih dataset
dataset = st.sidebar.selectbox('Dataset', ('AdventureWorks',))

# Sidebar untuk memilih tipe chart
tipe_chart = st.sidebar.selectbox('Tipe Chart', ('Comparison', 'Distribution', 'Composition', 'Relationship'))

# Memuat data sesuai pilihan dataset
if dataset == 'AdventureWorks':
    df_donut, df_scatter, df_hist, df_bar = load_aw_data()

# Menampilkan chart sesuai pilihan tipe chart
if tipe_chart == 'Comparison':
    if dataset == 'AdventureWorks':
        st.subheader('Comparison Bar Chart')
        fig_bar = px.bar(df_bar, x='City', y='CustomerCount', title='Jumlah Pelanggan Berdasarkan Kota (Top 10)')
        fig_bar.update_layout(
            xaxis_title='Kota',
            yaxis_title='Jumlah Pelanggan'
        )
        st.plotly_chart(fig_bar)

elif tipe_chart == 'Distribution':
    if dataset == 'AdventureWorks':
        st.subheader('Distribution Histogram')
        fig_hist = px.histogram(df_hist, x='YearlyIncome', nbins=30, title='Distribusi Pendapatan Tahunan Pelanggan')
        fig_hist.update_layout(
            xaxis_title='Pendapatan Tahunan',
            yaxis_title='Jumlah Pelanggan',
            bargap=0.1
        )
        st.plotly_chart(fig_hist)

elif tipe_chart == 'Composition':
    if dataset == 'AdventureWorks':
        st.subheader('Composition Donut Chart')
        fig_donut = px.pie(df_donut, values='SalesCount', names='Currency', title='Komposisi Penjualan Berdasarkan Mata Uang',
                        hole=0.3, labels={'SalesCount': 'Jumlah Penjualan', 'Currency': 'Mata Uang'})
        st.plotly_chart(fig_donut)

elif tipe_chart == 'Relationship':
    if dataset == 'AdventureWorks':
        st.subheader('Relationship Scatter Plot')
        fig_scatter = px.scatter(df_scatter, x='NumberEmployees', y='AnnualSales',
                                 title='Relationship between Number of Employees and Annual Sales',
                                 labels={'NumberEmployees': 'Number of Employees', 'AnnualSales': 'Annual Sales'})
        fig_scatter.update_layout(xaxis_title='Number of Employees', yaxis_title='Annual Sales')
        st.plotly_chart(fig_scatter)
