# Analytics & Visualization Example
# Streamlit dashboard
import streamlit as st
import pandas as pd

data = pd.DataFrame({
    'symbol': ['AAPL', 'GOOG', 'MSFT'],
    'price': [150, 2800, 300]
})
st.title('InfinityAI Dashboard')
st.dataframe(data)

# Real-time analytics (Dash)
import dash
from dash import html, dcc
import plotly.graph_objs as go

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1('Real-Time Price Chart'),
    dcc.Graph(id='live-graph', figure=go.Figure())
])

if __name__ == '__main__':
    app.run_server(debug=True)
