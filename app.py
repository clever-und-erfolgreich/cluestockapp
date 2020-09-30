import streamlit as st
import streamlit.components.v1 as stc

import datetime as dt

#panda is the datareader from web
import pandas as pd
import pandas_datareader.data as web
import requests

import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

import numpy as np

from PIL import Image

###From her set General Settings like App/Tab Icon and Name
st.beta_set_page_config(page_title='CLUE Stock Analyzing App', page_icon='logo.jpg')

###From her import Stock List
@st.cache
def stock_list(stock_list):
    df = pd.read_excel('output_2.xlsx', index_col=0)
#    df.drop(['Change in %', 'Last Price', 'Name.1', 'Letzter Preis', 'Änderung'], inplace=True, axis=1)
    df_li = df.dropna()
    return df_li

df_li = stock_list(stock_list)

### From her Stock List Overview and day price and change
@st.cache
def stock_data(stock_data):
    rdax_ = requests.get('https://de.finance.yahoo.com/quote/%5EGDAXI/components?p=%5EGDAXI')
    rmax_ = requests.get('https://de.finance.yahoo.com/quote/%5EMDAXI/components?p=^MDAXI&.tsrc=fin-srch')
    rsax_ = requests.get('https://de.finance.yahoo.com/quote/%5ESDAXI/components?p=^SDAXI&.tsrc=fin-srch')
    rtax_ = requests.get('https://de.finance.yahoo.com/quote/%5ETECDAX/components?p=^TECDAX&.tsrc=fin-srch')

    #pd.read_html reads all tables from request - [0] is output frist table - [1] is ouput second table and so on
    df_dax_ = pd.read_html(rdax_.text)[0]
    df_dax_ = pd.DataFrame(df_dax_)
    df_mdax_ = pd.read_html(rmax_.text)[0]
    df_mdax_ = pd.DataFrame(df_mdax_)
    df_sdax_ = pd.read_html(rsax_.text)[0]
    df_sdax_ = pd.DataFrame(df_sdax_)
    df_tdax_ = pd.read_html(rtax_.text)[0]
    df_tdax_ = pd.DataFrame(df_tdax_)

    yah_1 = pd.merge(df_dax_[['Symbol', 'Firmenname', 'Letzter Preis', 'Änderung']], df_mdax_[['Symbol', 'Firmenname', 'Letzter Preis', 'Änderung']], how='outer')
    yah_2 = pd.merge(yah_1, df_sdax_[['Symbol', 'Firmenname', 'Letzter Preis', 'Änderung']], how='outer')
    yah_list = pd.merge(yah_2, df_tdax_[['Symbol', 'Firmenname', 'Letzter Preis', 'Änderung']], how='outer')
    yah_list.sort_values(by=['Änderung'], ascending=False, inplace=True)

    yah_list.convert_dtypes()
    yah_list[['Last Price', 'Change in %', 'Name']] = yah_list[['Letzter Preis', 'Änderung', 'Firmenname']]
    yah_list[['Last Price', 'Change in %']] = yah_list[['Last Price', 'Change in %']]/100
    yah = yah_list[['Name', 'Symbol', 'Last Price', 'Change in %']]
    yah.set_index('Name', inplace=True)

    ###From her joining excel and request yahoo for Stock List Overview
    join = pd.merge(df_li, yah_list, left_on='Symbol', right_on='Symbol')
    join_1 = join[['Firmenname', 'Symbol', 'Country', 'List', 'Industry', 'Last Price', 'Change in %']]
    join_1['Name'] = join_1['Firmenname']
    join_1.drop(['Firmenname'], axis=1, inplace=True)
    join_1.set_index('Name', inplace=True)

    return join_1

join_1 = stock_data(stock_data)

def main():
    """ Stock APP """
###    st.sidebar.image('D:\Python\Python\Stock Investing\StockApp\LOGO.png')

    ###Selectbox/Dorpdown of Stocks as Input
    Input = st.sidebar.selectbox('Select Stock', df_li['Name'])

    st.sidebar.text('Country of selected Stock: '+ df_li.Country[Input])
    st.sidebar.text('Index of selected Stock: '+ df_li.List[Input])

    ###Input leads to Search of finanzen.net P&L-BS
    output = df_li['Search']
    entry = output[Input]

    ###Imput leads to Symbol for yahoo chart data
    chart_in = df_li['Symbol']
    chart = chart_in[Input]

    @st.cache
    def stat_list(stat_list):
        r = requests.get('https://de.finance.yahoo.com/quote/'+chart+'/key-statistics?p='+chart)
        s1 = pd.read_html(r.text)[1]
        s2 = pd.read_html(r.text)[0]
        s3 = pd.read_html(r.text)[3]

        s1.dropna(inplace=True)
        s2.dropna(inplace=True)
        s3.dropna(inplace=True)
        s3[1] = s3[1].str.replace('%', '')
        s3[1] = s3[1].str.replace(',', '')

        div_quo = s3[s3[0] == 'Ausschüttungsquote 4'].apply(pd.to_numeric, errors='coerce') / 100
        av_div = s3[s3[0] == 'Durchschnittliche Dividendenrendite über 5 Jahre 4'].apply(pd.to_numeric, errors='coerce') / 100
        est_div = s3[s3[0] == 'Erwarteter Jahresdividendenertrag 4'].apply(pd.to_numeric, errors='coerce') / 100
        beta = s1[s1[0] == 'Beta (5 J., monatlich)'].apply(pd.to_numeric, errors='coerce') / 100
        val_sal = s2[s2[0] == 'Unternehmenswert/Umsatz 3'].apply(pd.to_numeric, errors='coerce') / 100
        val_ebitda = s2[s2[0] == 'Unternehmenswert/EBITDA 6'].apply(pd.to_numeric, errors='coerce') / 100

        fig = pd.merge(beta, val_sal, how='outer')
        fig_1 = pd.merge(fig, val_ebitda, how='outer')
        fig_2 = pd.merge(fig_1, div_quo, how='outer')
        fig_3 = pd.merge(fig_2, av_div, how='outer')
        fig_4 = pd.merge(fig_3, est_div, how='outer')

        fig_4.drop([0], inplace=True, axis=1)
        figure = fig_4.rename(index={0: 'Beta', 1: 'Company Value/Sales', 2: 'Company Value/EBITDA', 3: 'Payout Quote in % (P&L)', 4: 'Est. Dividend Return in %', 5: 'Average Dividend       Return in % (5 Years)'}, columns={1: 'Value'})
        return figure
    
    figure = stat_list(stat_list).style.set_precision(2)
    st.sidebar.table(figure)

    menu = ['Stock List - Top & Flop', 'Key Figures', 'Chart']
    choice = st.sidebar.selectbox('Menu', menu)
    

###From her Table - Key Figures
    if choice == 'Key Figures':
        st.title(Input)

        #Data Request
        @st.cache
        def key_list(key_list):
            r = requests.get('https://www.finanzen.net/bilanz_guv/'+entry)

            ##Try to get Data - if not in first table, go to next
            try:
                t = pd.read_html(r.text)[1]
                t.drop(columns=['Chart'], inplace=True)
                t_r = t.rename(columns={"Unnamed: 1": "Key Figures"})
                signal = "signal_1"
            except:
                signal = "signal_2"

            ##Get Data - Equity, Dividend
            if signal == "signal_1":
                t = pd.read_html(r.text)[2]
                t.drop(columns=['Chart'], inplace=True)
                df_e = t.rename(columns={"Unnamed: 1": "Key Figures"})
                df_e.set_index('Key Figures', inplace=True)
                df_e = df_e.transpose()
                df_e.reset_index(inplace=True)
                df_e = df_e.rename(columns={"index": "Year"})

                t_d = pd.read_html(r.text)[1]
                t_d.drop(columns=['Chart'], inplace=True)
                df_d = t_d.rename(columns={"Unnamed: 1": "Key Figures"})
                df_d.set_index('Key Figures', inplace=True)
                df_d = df_d.transpose()
                df_d.reset_index(inplace=True)
                df_d = df_d.rename(columns={"index": "Year"})

                e_d = df_e.merge(df_d, left_on='Year', right_on='Year')
            elif signal == "signal_2":
                t = pd.read_html(r.text)[3]
                t.drop(columns=['Chart'], inplace=True)
                df_e = t.rename(columns={"Unnamed: 1": "Key Figures"})
                df_e.set_index('Key Figures', inplace=True)
                df_e = df_e.transpose()
                df_e.reset_index(inplace=True)
                df_e = df_e.rename(columns={"index": "Year"})
    
                t_d = pd.read_html(r.text)[2]
                t_d.drop(columns=['Chart'], inplace=True)
                df_d = t_d.rename(columns={"Unnamed: 1": "Key Figures"})
                df_d.set_index('Key Figures', inplace=True)
                df_d = df_d.transpose()
                df_d.reset_index(inplace=True)
                df_d = df_d.rename(columns={"index": "Year"})

                e_d = df_e.merge(df_d, left_on='Year', right_on='Year')
            else:
                pass

            if signal == "signal_1":
                e = e_d.apply(pd.to_numeric, errors='coerce')
                e['Year'] = e['Year'].astype(object)
                e[['Equity Ratio in %', 'Dividend Return in %', 'Dividend']] = round(e[['Eigenkapitalquote in %', 'Dividendenrendite Jahresende in %', 'Dividende je Aktie']]/100, 2)
        
                e_e = e[['Year', 'Equity Ratio in %', 'Dividend', 'Dividend Return in %']]
            elif signal == "signal_2":
                e = e_d.apply(pd.to_numeric, errors='coerce')
                e['Year'] = e['Year'].astype(object)
                e[['Equity Ratio in %', 'Dividend Return in %', 'Dividend']] = round(e[['Eigenkapitalquote in %', 'Dividendenrendite Jahresende in %', 'Dividende je Aktie']]/100, 2)
    
                e_e = e[['Year', 'Equity Ratio in %', 'Dividend', 'Dividend Return in %']]


            ##Get Data - Profit & Loss
            if signal == "signal_1":
                t_pl = pd.read_html(r.text)[3]
                t_pl.drop(columns=['Chart'], inplace=True)
                df_pl = t_pl.rename(columns={"Unnamed: 1": "Key Figures"})
                df_pl.set_index('Key Figures', inplace=True)
                df_pl = df_pl.transpose()
                df_pl.reset_index(inplace=True)
                df_pl = df_pl.rename(columns={"index": "Year"})
            elif signal == "signal_2":
                t_pl = pd.read_html(r.text)[4]
                t_pl.drop(columns=['Chart'], inplace=True)
                df_pl = t_pl.rename(columns={"Unnamed: 1": "Key Figures"})
                df_pl.set_index('Key Figures', inplace=True)
                df_pl = df_pl.transpose()
                df_pl.reset_index(inplace=True)
                df_pl = df_pl.rename(columns={"index": "Year"})
            else:
                pass

            if signal == "signal_1":
                pl = df_pl.apply(pd.to_numeric, errors='coerce')
                pl['Year'] = pl['Year'].astype(object)
                pl[['Umsatzerlöse', 'Sales Change yty in %', 'Bruttoergebnis vom Umsatz', 'Sales Margin Change yty in %', 'Operatives Ergebnis', 'EBIT Margin Change yty in %']] = pl[['Umsatzerlöse', 'Umsatzveränderung in %', 'Bruttoergebnis vom Umsatz', 'Bruttoergebnisveränderung in %', 'Operatives Ergebnis', 'Veränderung Operatives Ergebnis in %']]/100
                pl['Sales Margin in %'] = round(pl['Bruttoergebnis vom Umsatz']/pl['Umsatzerlöse'] * 100, 2)
                pl['EBIT Margin in %'] = round(pl['Operatives Ergebnis']/pl['Umsatzerlöse'] * 100, 2)
    
                pl_e = pl[['Year', 'Umsatzerlöse', 'Sales Change yty in %', 'Sales Margin in %', 'Sales Margin Change yty in %', 'EBIT Margin in %', 'EBIT Margin Change yty in %']]
            elif signal == "signal_2":
                pl = df_pl.apply(pd.to_numeric, errors='coerce')
                pl['Year'] = pl['Year'].astype(object)
                pl[['Sales Change yty in %', 'Sales Margin Change yty in %', 'EBIT Margin Change yty in %']] = pl[['Umsatzveränderung in %', 'Bruttoergebnisveränderung in %', 'Veränderung Operatives Ergebnis in %']]/100
                pl['Sales Margin in %'] = round(pl['Bruttoergebnis vom Umsatz']/pl['Umsatzerlöse'] * 100, 2)
                pl['EBIT Margin in %'] = round(pl['Operatives Ergebnis']/pl['Umsatzerlöse'] * 100, 2)
    
                pl_e = pl[['Year', 'Umsatzerlöse', 'Sales Change yty in %', 'Sales Margin in %', 'Sales Margin Change yty in %', 'EBIT Margin in %', 'EBIT Margin Change yty in %']]

            tables = pl_e.merge(e_e, left_on='Year', right_on='Year')
            tables.set_index('Year', inplace=True)
            tables['Year'] = tables.index
            return tables
        
        tables = key_list(key_list)
        
        table_chart = px.line(tables, 
                    x=tables['Year'],
                    y=['Sales Change yty in %', 'Sales Margin in %', 'Sales Margin Change yty in %', 'EBIT Margin in %', 'EBIT Margin Change yty in %'],
                    )
        
        table_chart.update_layout(
            autosize=True,
        #    width=auto,
        #    height=500,
            legend=dict(
                     yanchor="top",
                     y=0.99,
                     xanchor="left",
                     x=0.01,
                    font_color='black'),
            yaxis_title='in %',
            paper_bgcolor="White"
        )
        
        st.plotly_chart(table_chart, use_container_width=False)

### from here coloring the Table-Output
        tb = tables[['Sales Change yty in %', 'Sales Margin in %', 'Sales Margin Change yty in %', 'EBIT Margin in %', 'EBIT Margin Change yty in %', 'Equity Ratio in %', 'Dividend', 'Dividend Return in %']]
        def color_negative_red(val):
            color = 'red' if val < 0 else 'black'
            return 'color: %s' % color
        tb = tb.style\
             .applymap(color_negative_red)\
             .bar(subset=['Sales Change yty in %', 'Sales Margin in %', 'Sales Margin Change yty in %', 'EBIT Margin in %', 'EBIT Margin Change yty in %', 'Equity Ratio in %', 'Dividend', 'Dividend Return in %'], align='mid', color=['grey', 'green'])\
             .set_precision(2)
#            .set_properties(**{'background_color': 'white', 'border_color': 'black'})
        st.subheader('Key Figures')
        
        st.table(tb)

        st.subheader('Key Figures - Statistics')
        st.write(tables[['Sales Change yty in %', 'Sales Margin in %', 'Sales Margin Change yty in %', 'EBIT Margin in %', 'EBIT Margin Change yty in %', 'Equity Ratio in %', 'Dividend', 'Dividend Return in %']].describe())


###From her Chart
    elif choice == 'Chart':
        st.subheader(Input+ ' - Daily Chart')
                        
        #Define point to start and end for historical data
        start = st.sidebar.date_input('Start Date', dt.datetime(2010, 1, 1), min_value=dt.datetime(2000, 1, 1), max_value=dt.datetime(2019, 1, 1))
        end = dt.datetime.now()

######################################################################        
        #Get data for and from in defined datetime
        dataframe = web.DataReader(chart, 'yahoo', start, end)
        
        #Moving Avergae 200
        # #window is the function specification in module pandas for a time window, mean is a math function 
        dataframe['200ma'] = dataframe['Close'].rolling(window=200).mean()
        dataframe['50ma'] = dataframe['Close'].rolling(window=50).mean()
        dataframe['Volume'] = dataframe['Volume'].rolling(window=50).mean()
        #MA for the first dates are not available because of starting point, so let's drop all kind of data (start + window set)
        dataframe.dropna(inplace=True)
        
        data = dataframe[['Open', 'High', 'Low', 'Close', 'Volume', '200ma', '50ma']]
        data['Date'] = data.index
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02)

        fig.add_trace(go.Candlestick(
                    x=data['Date'],
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name='Open, High, Low, Close'),
                    row=1, col=1)
        
        fig.add_trace(go.Scatter( 
                    x=data['Date'],
                    y=data['200ma'],
                    name='MA200'),
                    row=1, col=1)
        
        fig.add_trace(go.Scatter( 
                    x=data['Date'],
                    y=data['50ma'],
                    name='MA50'),
                    row=1, col=1)

        fig.add_trace(go.Bar(
                    x=data['Date'],
                    y=data['Volume'],
                    name='MA50 Volume'),
#                    marker=dict(color='black')),
                    row=2, col=1)
        
        

        fig.update_layout(
            legend=dict(
            #         yanchor="top",
            #         y=0.99,
            #         xanchor="left",
            #         x=0.01
                font_color='white'),
#            xaxis_title='Date',
            xaxis_rangeslider_visible=False,
            yaxis_title='Volume / Price',
            width=800,
            height=800,
            plot_bgcolor='black',
            paper_bgcolor='black',
                font=dict(
                family="Arial",
                size=12,
                color='white'
            )
        )
        
        st.plotly_chart(fig, use_container_width=False)
    
###From her Stock List
    else:
        st.subheader('Stock List - Top & Flop')
        list_filter = ['All', 'DAX', 'MDAX', 'SDAX', 'TecDAX']
        l_f = st.sidebar.selectbox('Filter List by Index', list_filter)
        Industry_filter = ['All', 
           'Bahntechnik',
            'Biotechnologie',
            'Communication',
            'Consumer Discretionary',
            'Consumer Staples',
            'Dienstleistungen',
            'Einzel- und Großhandel',
            'Energy',
            'Fahrzeugwaschanlagen',
            'Financials',
            'Finanzdienstleistungen',
            'Fototechnik, Druckerei',
            'Fußball',
            'Handel',
            'Haustierbedarf',
            'Health Care',
            'Immobilien',
            'Industrials',
            'Industrie',
            'Industriedienstleistungen',
            'Information Technology',
            'Kabelnetzbetreiber, Internetdienstanbieter',
            'Kommunikationstechnik',
            'Logistik',
            'Maschinenbau',
            'Materials',
            'Medizintechnik',
            'Motorenhersteller',
            'Nahrungsmittel',
            'Nutzfahrzeuge',
            'Nutzfahrzeugzulieferer',
            'Online-Lotterien',
            'Personaldienstleistungen',
            'Real Estate',
            'Solartechnik',
            'Stahl- und Metallhandel',
            'Stahlindustrie',
            'Unternehmensbeteiligungen',
            'Utilities',
            'UV-Technologie']

        I_f = st.sidebar.selectbox('Filter List by Industry', Industry_filter)
        # st.sidebar.checkbox('All', value=1)
        # st.sidebar.checkbox('Germany', value=0)
        # st.sidebar.checkbox('USA', value=0)

        if l_f == 'All' and I_f == 'All':
            tab = join_1
            tab.sort_values(by=['Change in %'], ascending=False, inplace=True)
        else:
            if l_f != 'All' and I_f == 'All':
                tab = join_1[join_1['List'] == l_f]
                tab.sort_values(by=['Change in %'], ascending=False, inplace=True)
            else:
                if l_f == 'All' and I_f != 'All':
                    tab = join_1[join_1['Industry'] == I_f]
                    tab.sort_values(by=['Change in %'], ascending=False, inplace=True)
                elif l_f != 'All' and I_f != 'All':
                    tab = join_1[(join_1['List'] == l_f) & (join_1['Industry'] == I_f)]
                    tab.sort_values(by=['Change in %'], ascending=False, inplace=True)

        st.table(tab.style\
            .bar(subset=['Change in %'], align='mid', color=['grey', 'green'])\
            .set_precision(2))

###from her some Styling
    

if __name__ == '__main__':
    main()