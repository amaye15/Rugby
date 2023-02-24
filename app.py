import streamlit as sl
import datetime as dt
import gspread
import toml
import pandas as pd
import polars as pl
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
    
def highlight(series, threshold, column):
    is_max = pd.Series(data=False, index=series.index)
    is_max[column] = series.loc[column] == threshold
    return ['background-color : #7EBAFE' if is_max.any() else 'background-color : #FF887F' for v in is_max]

def main():
    # Toml Configuration
    conf == toml.load("config.toml")

    # Google Connection & Match Data
    # gc = gspread.service_account(filename="cred.json")
    gc = gspread.service_account_from_dict(dict(sl.secrets["config"]))
    match_worksheet = gc.open_by_url(conf["url"][""]).sheet1
    match_data = pl.DataFrame(match_worksheet.get_all_records())

    # Empty Dataframe Condition
    not_empty = match_data.height != 0
    
    # Set Scores
    nantes_score = conf["values"]["your_team_score"]
    adversaire_score = conf["values"]["adversaire_score"]


    ### Image ###
    _, center, _ = sl.columns([1, 1, 1])
    with center:
        sl.image("logo.png")
        ### Title ###
        sl.title("Les Vikings Rugby XIII")

    ###### Side Bar ######
    menu_choice = sl.sidebar.selectbox("Match", menu)

    if not_empty:
        # Get unique actions    
        match_data_unique_actions = match_data["Action"].unique()
        ### Calculate Score ###
        if "Essai" in match_data_unique_actions or "Transformation" in match_data_unique_actions or "Drop" in match_data_unique_actions:
            # Filter by Team
            nantes_filter = (match_data["Possession"] == "Nantes")
            adversaire_filter = (match_data["Possession"] == "Adversaire")
            # Determine Score
            nantes_score = sum(nantes_filter &  (match_data["Action"] == "Essai")) * 4 + sum(nantes_filter &  (match_data["Action"] == "Transformation")) * 6 +  sum(nantes_filter &  (match_data["Action"] == "Drop"))
            adversaire_score = sum(adversaire_filter &  (match_data["Action"] == "Essai")) * 4 + sum(adversaire_filter &  (match_data["Action"] == "Transformation")) * 6 +  sum(adversaire_filter &  (match_data["Action"] == "Drop"))

################################################################################################################################################################################################################################################

    ### New Game ###
    if menu_choice == "En Cours":

        left, _, right = sl.columns([1, 1, 1])
        
        with left:
            sl.markdown(f'<p style="font-family:sans-serif; color:#3392FF; font-size: 36px;">{f"Nantes: {nantes_score}"}</p>', unsafe_allow_html=True)

        with right:
            sl.markdown(f'<p style="font-family:sans-serif; color:#FF4233; font-size: 36px;">{f"Adversaire: {adversaire_score}"}</p>', unsafe_allow_html=True)

################################################################################################################################################################################################################################################
    
    if menu_choice == "Données des Match":

        left, _, right = sl.columns([1, 1, 1])
        
        with left:
            sl.markdown(f'<p style="font-family:sans-serif; color:#3392FF; font-size: 36px;">{f"Nantes:   {nantes_score}"}</p>', unsafe_allow_html=True)
        with right:
            sl.markdown(f'<p style="font-family:sans-serif; color:#FF4233; font-size: 36px;">{f"Adversaire:   {adversaire_score}"}</p>', unsafe_allow_html=True)

        ### Before Match ###
        sl.subheader("Avant le match")

        left, right = sl.columns([1, 1])

        with left:
            # Home or Away Game
            place_choice = sl.selectbox("Lieu du match", place)

        with right:
            # Opponent
            team_choice = sl.selectbox("Nom de l'adversaire", teams)

        ### During Match ###
        sl.subheader("Pendant le match")

        #left,center, right = sl.columns([1, 1, 1])
        left, right = sl.columns([1,1])
        #with left:
            # Possesion of the ball
            #ball = ["Nantes", "Adversaire"]
            #ball_choice = sl.selectbox("Possession de balle", ball)

        #with center:
        with left:
            # Action or Event taken place
            action_choice = sl.selectbox("Action", action)

        with right:
            # Zone of field
            zone_choice = sl.selectbox("Zone", zone)
        
        # Update Results
        if sl.button("Mise à jour des résultats"):
            
            # Automatically determine series
            if match_data.height == 0:
                series = 1
            elif match_data["Possession"][-1] == ball_choice and match_data["Action"][-1] == "Plaquage":
                series = match_data["Série"][-1]
            elif match_data["Possession"][-1] == ball_choice and match_data["Action"][-1] == "Coup de pied":
                series = match_data["Série"][-1]
            else:
                series = match_data["Série"][-1] + 1

            # Automatically determine series
            
            if match_data.height == 0:
                event = 1
            elif match_data["Possession"][-1] == ball_choice and match_data["Action"][-1] == "Plaquage" and action_choice == "Plaquage":
                event = match_data["Evénement"][-1] + 1
            elif match_data["Possession"][-1] == ball_choice and match_data["Action"][-1] == "Plaquage" and action_choice == "Coup de pied":
                event = match_data["Evénement"][-1] + 1
            elif match_data["Possession"][-1] == ball_choice and match_data["Action"][-1] == "Plaquage" and action_choice == "Essai (4pt)":
                event = match_data["Evénement"][-1] + 1
            elif match_data["Possession"][-1] == ball_choice and match_data["Action"][-1] == "Plaquage" and action_choice == "Essai et Transformation (6pt)":
                event = match_data["Evénement"][-1] + 1
            elif match_data["Possession"][-1] == ball_choice and match_data["Action"][-1] == "Plaquage" and action_choice == "Drop (1pt)":
                event = match_data["Evénement"][-1] + 1
            elif match_data["Possession"][-1] == ball_choice and match_data["Action"][-1] == "Plaquage" and action_choice == "Pénalité/Faute":
                event = match_data["Evénement"][-1] + 1
            else:
                event = 1

            # Automatically determine half
            if match_data.height == 0:
                half = "Première"
            elif ((dt.datetime.now() - pd.to_datetime(match_data["Temps"][0])).total_seconds() / 60) < 40:
                half = "Première"
            else:
                half = "Deuxième"
            if not_empty:
                # Add Data
                match_data = match_data.extend(pl.DataFrame({"Lieu du match": place_choice,
                            "Nom de l'adversaire": team_choice,
                            "Temps": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Mi-Temps": half,
                            "Série": series,
                            "Possession": ball_choice,
                            "Evénement": event, 
                            "Action": action_choice, 
                            "Zone": zone_choice,
                            "Nantes Score": nantes_score,
                            "Adversaire Score": adversaire_score}))
            else:
                match_data = pl.DataFrame({"Lieu du match": place_choice,
                            "Nom de l'adversaire": team_choice,
                            "Temps": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Mi-Temps": half,
                            "Série": series,
                            "Possession": ball_choice,
                            "Evénement": event, 
                            "Action": action_choice, 
                            "Zone": zone_choice,
                            "Nantes Score": nantes_score,
                            "Adversaire Score": adversaire_score})
            
            match_data = match_data.to_pandas()
            match_worksheet.update([match_data.columns.to_list()] + match_data.values.tolist())
            # Refresh Page
            sl.experimental_rerun()
        
        
        # Show Data
        sl.subheader("\n Résultats")
        #st.markdown('<style>div[title="OK"] { color: green; } div[title="KO"] { color: red; } .data:hover{ background:rgb(243 246 255)}</style>', unsafe_allow_html=True)
        #'background-color : #3392FF' if match_data[["Possession"]] == "Nantes" else 'background-color : #FF4233'
        if not_empty:
            sl.dataframe(match_data[["Série", "Evénement", "Possession", "Action", "Zone"]].to_pandas().style.apply(highlight, threshold="Nantes", column=["Possession"], axis=1), use_container_width=True)
        
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
            winner_choice = sl.selectbox("Winner", winner)
            save_delete_button = sl.button("Enregistrer et supprimer les résultats")
        # Save match data to historical data
        if save_delete_button:

            # Match Data
            historical_worksheet = gc.open_by_url(conf["url"]["history"]).sheet1
            historical_data = pd.DataFrame(historical_worksheet.get_all_records())

            # If empty, create empty dataframe
            #if historical_data.height == 0:
                #historical_data = pl.DataFrame(schema = "Lieu du match", "Nom de l'adversaire", "Temps", "Mi-Temps", "Série", "Possession",  "Plaquage", "Action", "Zone", "Nantes Score", "Adversaire Score", "Winner"])
        
            match_data = match_data.with_columns(pl.lit(winner_choice).alias("Winner"))
            historical_data = historical_data.append(match_data.to_pandas())
            historical_worksheet.update([historical_data.columns.to_list()] + historical_data.values.tolist())
            match_worksheet.clear()
            sl.experimental_rerun()

    return
if __name__ == "__main__":
    main()