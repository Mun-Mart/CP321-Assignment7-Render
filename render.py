# Imports used libraries
import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# Pulls data from wiki page and grabs the appropriate table
df_list = pd.read_html("https://en.wikipedia.org/wiki/List_of_FIFA_World_Cup_finals")
df = df_list[3]

# Edits the german entry in table and makes another dataframe for winners
df = df.replace({"Winners": {"West Germany": "Germany"}, "Runners-up": {"West Germany": "Germany"}})
df_winners = df["Winners"].value_counts().reset_index()
df_winners.columns = ["Country", "Wins"]

# Initializes the dashboard and its layout
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(
    [
        # Tille header
        html.H1("FIFA World Cup Winners and Runners-Up"),
        
        # Radio items to choose selection method
        dcc.RadioItems(
            id="selection-mode",
            options=[
                {"label": "Select by Country", "value": "country"},
                {"label": "Select by Year", "value": "year"},
            ],
            value="country",
            labelStyle={"display": "inline-block", "margin": "10px"},
        ),
        
        # Dropdown to select country
        dcc.Dropdown(
            id="country-dropdown",
            options=[
                {"label": country, "value": country}
                for country in df_winners["Country"]
            ],
            placeholder="Select a Country",
            clearable=True,
        ),
        
        # Dropdown to select year
        dcc.Dropdown(
            id="year-dropdown",
            options=[{"label": str(year), "value": year} for year in df["Year"]],
            placeholder="Select a Year",
            clearable=True,
        ),
        
        # Added choropleth map to layout
        dcc.Graph(id="choropleth-map"),
        html.Div(id="output-div"),
    ]
)

# Callback for dropdown initialization
@app.callback(
    [
        Output("country-dropdown", "style"),
        Output("year-dropdown", "style"),
        Output("country-dropdown", "value"),
        Output("year-dropdown", "value"),
    ],
    [Input("selection-mode", "value")],
)
def toggle_dropdowns(selection_mode):
    if selection_mode == "country":
        return {"display": "block"}, {"display": "none"}, None, None
    else:
        return {"display": "none"}, {"display": "block"}, None, None
    
    # Callback to update map and return results
@app.callback(
    [Output("choropleth-map", "figure"), Output("output-div", "children")],
    [Input("country-dropdown", "value"), Input("year-dropdown", "value")],
)
def update_map(selected_country, selected_year):

    # When countries are being used map shows all countries and their wins and returns win for selected country
    if selected_country:
        wins = df_winners[df_winners["Country"] == selected_country]["Wins"].values[0]
        choro_map = px.choropleth(
            df_winners,
            locations="Country",
            locationmode="country names",
            color="Wins",
            title="World Cup Wins by Country",
        )
        return choro_map, f"{selected_country} has won {wins} times."

    # When year is selected map shows winner and runner up and returns the winner and runner up for that year
    elif selected_year:
        row = df.loc[df["Year"] == selected_year].iloc[0]
        highlight_df = pd.DataFrame(
            {
                "Country": [row["Winners"], row["Runners-up"]],
                "Result": ["Winner", "Runner-Up"],
            }
        )
        choro_map = px.choropleth(
            highlight_df,
            locations="Country",
            locationmode="country names",
            color="Result",
            title=f"World Cup {selected_year} Winner and Runner-Up",
            color_discrete_map={"Winner": "green", "Runner-Up": "red"},
        )
        return choro_map, f"Year {selected_year}: Winner - {row[1]}, Runner-Up - {row[3]}"

    # Just shows map with wins per country upon initialization or no selection
    choro_map = px.choropleth(
        df_winners,
        locations="Country",
        locationmode="country names",
        color="Wins",
        title="World Cup Wins by Country",
    )
    return choro_map, ""

# Runs dashboard
if __name__ == "__main__":
    app.run(debug=True)
