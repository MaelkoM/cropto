import pandas as pd
import plotly.express as px

prices = pd.read_csv("prices_history.csv", index_col=0)
prices.index = pd.to_datetime(prices.index, unit="s")
prices_change = prices / prices.mean()
print(prices_change)
prices_total_change = (prices_change.iloc[-1][:] - prices_change.iloc[0][:]) * 100
print(prices_total_change["PERPEUR"])
fig = px.bar(prices_total_change)
fig.show()
