import streamlit as sl
import datetime as dt
import gspread
import toml
import pandas as pd
import polars as pl
import warnings
import streamlit.components.v1 as components
warnings.simplefilter(action='ignore', category=FutureWarning)
    
    
def highlight(series, value, column) -> list:
    is_max = pd.Series(data=False, index=series.index)
    is_max[column] = series.loc[column] == value
    return ['background-color : #3392FF' if is_max.any() else 'background-color : #FF4233' for _ in is_max]

def determine_score(df, team: str, adversaire: str) -> tuple:
    team_score , adversaire_score = 0, 0
    # Get Unique Actions    
    unique_actions = df["Action"].unique().to_list()
    # Get Conditions
    c1 = "Essai" in unique_actions
    c2 = "Transformation" in unique_actions
    c3 = "Drop" in unique_actions
    ### Calculate Score ###
    if c1 or c2 or c3:
        # Filter by Team
        team_filter = (df["Actor"] == team)
        adversaire_filter = (df["Actor"] == adversaire)
        # Determine Score
        team_score = sum(team_filter & (df["Action"] == "Essai")) * 4 + sum(team_filter &  (df["Action"] == "Transformation")) * 2 + sum(team_filter & (df["Action"] == "Drop"))
        adversaire_score = sum(adversaire_filter & (df["Action"] == "Essai")) * 4 + sum(adversaire_filter & (df["Action"] == "Transformation")) * 2 + sum(adversaire_filter & (df["Action"] == "Drop"))
    return (team_score , adversaire_score)

def determine_set(df, actor):
        # Automatically determine series
    if df.height == 0:
        series = 1
    elif df["Actor"][-1] == actor and df["Action"][-1] == "Plaquage":
        series = df["Série"][-1]
    elif df["Actor"][-1] == actor and df["Action"][-1] == "Coup de pied":
        series = df["Série"][-1]
    elif df["Actor"][-1] == actor and df["Action"][-1] == "Essai":
        series = df["Série"][-1]
    else:
        series = df["Série"][-1] + 1
    return series

def determine_tackle(df, actor, action):
    if df.height == 0:
        event = 1
    elif df["Actor"][-1] == actor and df["Action"][-1] == "Plaquage" and action == "Plaquage":
        event = df["Plaquage"][-1] + 1
    elif df["Actor"][-1] == actor and df["Action"][-1] == "Plaquage" and action == "Coup de pied":
        event = df["Plaquage"][-1] + 1
    elif df["Actor"][-1] == actor and df["Action"][-1] == "Plaquage" and action == "Essai":
        event = df["Plaquage"][-1] + 1
    elif df["Actor"][-1] == actor and df["Action"][-1] == "Essai" and action == "Transformation":
        event = df["Plaquage"][-1] + 1
    elif df["Actor"][-1] == actor and df["Action"][-1] == "Plaquage" and action == "Drop":
        event = df["Plaquage"][-1] + 1
    elif df["Actor"][-1] == actor and df["Action"][-1] == "Plaquage" and action == "Pénalité/Faute":
        event = df["Plaquage"][-1] + 1
    else:
        event = 1
    return event

def main():
    # Toml Configuration
    conf = toml.load("config.toml")

    # Google Connection & Match Data
    # gc = gspread.service_account(filename="cred.json")
    gc = gspread.service_account_from_dict(dict(sl.secrets["config"]))
    match_worksheet = gc.open_by_url(conf["url"]["match"]).sheet1
    match_data = pl.DataFrame(match_worksheet.get_all_records())

    # Empty Dataframe Condition
    not_empty = match_data.height != 0
    # Set Scores
    team_score, adversaire_score = conf["values"]["team_score"], conf["values"]["team_score"]
    # Set Team
    team, adversaire = "Nantes", "Adversaire"

    ###### Image ######
    right, center, left = sl.columns([1, 1, 1])
    with center:
        sl.image("logo.png")
        ### Title ###
        sl.title("Les Vikings Rugby XIII")

    ###### Side Bar ######
    menu_choice = sl.sidebar.selectbox("Match", conf["pages"].values())
    
    ### Before Match ###
    sl.subheader("Avant le match")
    right, center, left = sl.columns([1, 1, 1])
    
    with right:
        team = sl.selectbox("Choisissez votre équipe", list(conf["teams"].values())[:-1])
    with left:
        tmp = list(reversed(conf["teams"].values()))
        tmp.remove(team)
        adversaire = sl.selectbox("Choisissez votre adversaire", tmp)
    with center:
        # Home or Away Game
        place_choice = sl.selectbox("Lieu du match", conf["places"].values())

    # Determine Scores
    if not_empty:
        team_score, adversaire_score = determine_score(match_data, team, adversaire)

################################################################################################################################################################################################################################################
    
    if menu_choice == "Données des Match":

        left, center, right = sl.columns([1, 1, 1])
        
        with left:
            sl.markdown(conf["html"]["string_one"].format(value = team), unsafe_allow_html=True)
            sl.markdown(conf["html"]["string_one"].format(value = team_score), unsafe_allow_html=True)
            
        with right:
            sl.markdown(conf["html"]["string_two"].format(value = adversaire), unsafe_allow_html=True)
            sl.markdown(conf["html"]["string_two"].format(value = adversaire_score), unsafe_allow_html=True)

        ### During Match ###
        sl.subheader("Pendant le match")

        left, center, right = sl.columns([1, 1, 1])
        with left:
            # Possesion of the ball
            ball_choice = sl.selectbox("Qui a fait l'action ?", [team, adversaire])

        #with center:
        with center:
            # Action or Event taken place
            action_choice = sl.selectbox("Quelle action s'est passée ?", conf["actions"].values())

        with right:
            # Zone of field
            zone_choice = sl.selectbox("Où l'action s'est-elle déroulée ?", [team + " " + conf["zones"]["meters"],
                                                                             adversaire + " " + conf["zones"]["meters"],
                                                                             conf["zones"]["middle"]])
        
        # Update Results
        if sl.button("Mise à jour des résultats"):
            
            # Automatically determine set
            series = determine_set(match_data, ball_choice)

            # Automatically determine event
            event = determine_tackle(match_data, ball_choice, action_choice)

            # Automatically determine half
            if match_data.height == 0:
                half = "Première"
            elif ((dt.datetime.now() - pd.to_datetime(match_data["Temps"][0])).total_seconds() / 60) < 40:
                half = "Première"
            else:
                half = "Deuxième"

            match_values = [place_choice, team, adversaire, dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), half,
                            series, event, ball_choice, action_choice, zone_choice, team_score, adversaire_score]

            if not_empty:
                # Extend Dataframe
                match_data = match_data.extend(pl.DataFrame(dict(zip(conf["column_names"].values(), match_values))))
            else:
                # Create Dataframes
                match_data = pl.DataFrame(dict(zip(conf["column_names"].values(), match_values)))
            
            match_data = match_data.to_pandas()
            match_worksheet.update([match_data.columns.to_list()] + match_data.values.tolist())
            # Refresh Page
            sl.experimental_rerun()
        
        
        # Show Data
        sl.subheader("\n Résultats")

        if not_empty:
            sl.dataframe(match_data[["Actor", "Action", "Zone"]].to_pandas().style.apply(highlight, 
                                                                                         value = "Nantes", 
                                                                                         column = ["Actor"], 
                                                                                         axis = 1), 
                                                                                         use_container_width = True)
        
            ### Delete Row ###
            left, _, _ = sl.columns([1.3, 2, 2])
            with left:
                row = range(match_data.height)
                row_choice = sl.selectbox("Ligne", row)
                delete_button = sl.button("Supprimer une ligne")
            # Delete button
            if delete_button: 
                match_worksheet.delete_row(row_choice + 2)
                sl.experimental_rerun()

        ### After Match ###
        sl.subheader("Fin du match")
        left_v2, _, _ = sl.columns([1.35, 1, 1])
        with left_v2:
            winner_choice = sl.selectbox("Winner", [team, adversaire])
            save_delete_button = sl.button("Enregistrer et supprimer les résultats")
        # Save match data to historical data
        if save_delete_button:

            # Match Data
            historical_worksheet = gc.open_by_url(conf["url"]["history"]).sheet1
            historical_data = pd.DataFrame(historical_worksheet.get_all_records())
        
            match_data = match_data.with_columns(pl.lit(winner_choice).alias("Winner"))
            historical_data = historical_data.append(match_data.to_pandas())
            historical_worksheet.update([historical_data.columns.to_list()] + historical_data.values.tolist())
            match_worksheet.clear()
            sl.experimental_rerun()

    return
if __name__ == "__main__":
    main()