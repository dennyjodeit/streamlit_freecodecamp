import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

# Streamlit App
st.title('📈 Stock Price Dashboard')
st.write('Powered by Yahoo Finance (yfinance)')

# Sidebar for user inputs
st.sidebar.header('Stock Selection')
tickerSymbol = st.sidebar.text_input('Enter Stock Symbol', 'AAPL').upper()

# Time period selection
period_options = {
    '1 week': '7d',
    '1 month': '1mo',
    '3 months': '3mo',
    '6 months': '6mo',
    '1 year': '1y',
    '2 years': '2y',
    '5 years': '5y'
}

selected_period = st.sidebar.selectbox(
    'Time Period',
    list(period_options.keys()),
    index=2  # Default to 3 months
)

if st.sidebar.button('Get Data') or tickerSymbol:
    if tickerSymbol:
        try:
            # Create ticker object
            ticker = yf.Ticker(tickerSymbol)
            
            # Get ticker info
            info = ticker.info
            
            # Get historical data
            period_code = period_options[selected_period]
            hist_data = ticker.history(period=period_code)
            
            if not hist_data.empty:
                # Display company information
                st.subheader(f"{info.get('longName', tickerSymbol)} ({tickerSymbol})")
                
                # Current price metrics
                current_price = hist_data['Close'].iloc[-1]
                previous_close = info.get('previousClose', hist_data['Close'].iloc[-2])
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Current Price", 
                        f"${current_price:.2f}",
                        delta=f"{change:+.2f} ({change_percent:+.2f}%)"
                    )
                
                with col2:
                    latest_volume = hist_data['Volume'].iloc[-1]
                    st.metric("Volume", f"{latest_volume:,.0f}")
                
                with col3:
                    latest_high = hist_data['High'].iloc[-1]
                    st.metric("Day High", f"${latest_high:.2f}")
                
                with col4:
                    latest_low = hist_data['Low'].iloc[-1]
                    st.metric("Day Low", f"${latest_low:.2f}")
                
                # Additional company info
                if info:
                    col5, col6, col7, col8 = st.columns(4)
                    
                    with col5:
                        market_cap = info.get('marketCap', 0)
                        if market_cap:
                            if market_cap >= 1e12:
                                cap_display = f"${market_cap/1e12:.2f}T"
                            elif market_cap >= 1e9:
                                cap_display = f"${market_cap/1e9:.2f}B"
                            elif market_cap >= 1e6:
                                cap_display = f"${market_cap/1e6:.2f}M"
                            else:
                                cap_display = f"${market_cap:,.0f}"
                            st.metric("Market Cap", cap_display)
                    
                    with col6:
                        pe_ratio = info.get('trailingPE', 'N/A')
                        if pe_ratio != 'N/A' and pe_ratio:
                            st.metric("P/E Ratio", f"{pe_ratio:.2f}")
                        else:
                            st.metric("P/E Ratio", "N/A")
                    
                    with col7:
                        week_52_high = info.get('fiftyTwoWeekHigh', 0)
                        st.metric("52W High", f"${week_52_high:.2f}")
                    
                    with col8:
                        week_52_low = info.get('fiftyTwoWeekLow', 0)
                        st.metric("52W Low", f"${week_52_low:.2f}")
                
                # Company details
                if info:
                    st.subheader("Company Information")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Sector:** {info.get('sector', 'N/A')}")
                        st.write(f"**Industry:** {info.get('industry', 'N/A')}")
                        st.write(f"**Country:** {info.get('country', 'N/A')}")
                        st.write(f"**Exchange:** {info.get('exchange', 'N/A')}")
                    
                    with col2:
                        st.write(f"**Employees:** {info.get('fullTimeEmployees', 'N/A'):,}" if info.get('fullTimeEmployees') else "**Employees:** N/A")
                        dividend_yield = info.get('dividendYield')
                        if dividend_yield:
                            st.write(f"**Dividend Yield:** {dividend_yield*100:.2f}%")
                        else:
                            st.write("**Dividend Yield:** N/A")
                        
                        if info.get('website'):
                            st.write(f"**Website:** [{info.get('website')}]({info.get('website')})")
                    
                    # Business summary
                    if info.get('longBusinessSummary'):
                        st.subheader("Business Summary")
                        st.write(info['longBusinessSummary'])
                
                # Price chart
                st.subheader(f'Stock Price Chart ({selected_period})')
                
                # Prepare data for chart
                chart_data = hist_data.reset_index()
                chart_data['Date'] = pd.to_datetime(chart_data['Date'])
                
                # Create price chart
                price_chart = alt.Chart(chart_data).mark_line(
                    point=False,
                    strokeWidth=2
                ).add_selection(
                    alt.selection_interval(bind='scales')
                ).encode(
                    x=alt.X('Date:T', title='Date'),
                    y=alt.Y('Close:Q', title='Close Price ($)', scale=alt.Scale(zero=False)),
                    color=alt.value('#1f77b4'),
                    tooltip=['Date:T', 'Open:Q', 'High:Q', 'Low:Q', 'Close:Q', 'Volume:Q']
                ).properties(
                    width=700,
                    height=400,
                    title=f'{tickerSymbol} Stock Price - {selected_period}'
                )
                
                st.altair_chart(price_chart, use_container_width=True)
                
                # Volume chart
                st.subheader(f'Volume Chart ({selected_period})')
                volume_chart = alt.Chart(chart_data).mark_bar().add_selection(
                    alt.selection_interval(bind='scales')
                ).encode(
                    x=alt.X('Date:T', title='Date'),
                    y=alt.Y('Volume:Q', title='Volume'),
                    color=alt.value('#ff7f0e'),
                    tooltip=['Date:T', 'Volume:Q']
                ).properties(
                    width=700,
                    height=200,
                    title=f'{tickerSymbol} Trading Volume - {selected_period}'
                )
                
                st.altair_chart(volume_chart, use_container_width=True)
                
                # Performance metrics
                st.subheader('Performance Summary')
                
                # Calculate performance metrics
                returns_1d = ((hist_data['Close'].iloc[-1] / hist_data['Close'].iloc[-2]) - 1) * 100
                returns_1w = ((hist_data['Close'].iloc[-1] / hist_data['Close'].iloc[-5]) - 1) * 100 if len(hist_data) >= 5 else None
                returns_1m = ((hist_data['Close'].iloc[-1] / hist_data['Close'].iloc[-21]) - 1) * 100 if len(hist_data) >= 21 else None
                returns_period = ((hist_data['Close'].iloc[-1] / hist_data['Close'].iloc[0]) - 1) * 100
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("1 Day Return", f"{returns_1d:+.2f}%")
                
                with col2:
                    if returns_1w is not None:
                        st.metric("1 Week Return", f"{returns_1w:+.2f}%")
                    else:
                        st.metric("1 Week Return", "N/A")
                
                with col3:
                    if returns_1m is not None:
                        st.metric("1 Month Return", f"{returns_1m:+.2f}%")
                    else:
                        st.metric("1 Month Return", "N/A")
                
                with col4:
                    st.metric(f"{selected_period} Return", f"{returns_period:+.2f}%")
                
                # Data table
                st.subheader('Recent Trading Data')
                display_data = hist_data.tail(10).round(2)
                st.dataframe(display_data, use_container_width=True)
                
            else:
                st.error(f"No data found for {tickerSymbol}")
                
        except Exception as e:
            st.error(f"Error fetching data for {tickerSymbol}: {str(e)}")
            
    else:
        st.info("👆 Enter a stock symbol in the sidebar to get started!")

# Sidebar footer
with st.sidebar:
    st.markdown("---")
    st.subheader("About")
    st.caption("This app uses yfinance library to fetch data from Yahoo Finance.")
    st.caption("Data is free and doesn't require API keys.")
    st.caption("Perfect for learning and personal projects!")
    
    # Popular stocks suggestions
    st.subheader("Popular Stocks")
    popular_stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
    
    for stock in popular_stocks:
        if st.button(stock, key=f"btn_{stock}"):
            st.rerun()