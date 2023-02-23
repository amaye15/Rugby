import streamlit as sl
import datetime as dt
import gspread
import pandas as pd
import polars as pl
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

    
def highlight(series, threshold, column):
    is_max = pd.Series(data=False, index=series.index)
    is_max[column] = series.loc[column] == threshold
    return ['background-color : #7EBAFE' if is_max.any() else 'background-color : #FF887F' for v in is_max]

def main():
    # Connect to Google
    #gc = gspread.service_account(filename="cred.json")
    gc = gspread.service_account_from_dict(dict(sl.secrets["config"]))

    ### Image ###
    _, center, _ = sl.columns([1, 1, 1])
    with center:
        sl.image("logo.png")
        ### Title ###
        sl.title("Les Vikings Rugby XIII")

    ### Side Bar ###
    menu = ["En Cours", "Données des Match", "Analyse des Match (Incomplet)", "Data Science (Incomplete)"]
    menu_choice = sl.sidebar.selectbox("Match", menu)

    # Match Data
    match_worksheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1F0NI-6_oi_geBDIJge9b6FXipMUyDw3XR90rHDALCx8/edit").sheet1
    match_data = pl.DataFrame(match_worksheet.get_all_records())
    
    if match_data.height != 0:
        # Get unique actions    
        match_data_unique_actions = match_data["Action"].unique()
    
    if match_data.height != 0:
        ### Calculate Score ###
        if "Essai (4pt)" in match_data_unique_actions or "Essai et Transformation (6pt)" in match_data_unique_actions or "Drop (1pt)" in match_data_unique_actions:
            # Filter by Team
            nantes_filter = (match_data["Possession"] == "Nantes")
            adversaire_filter = (match_data["Possession"] == "Adversaire")
            # Determine Score
            nantes_score = sum(nantes_filter &  (match_data["Action"] == "Essai (4pt)")) * 4 + sum(nantes_filter &  (match_data["Action"] == "Essai et Transformation (6pt)")) * 6 +  sum(nantes_filter &  (match_data["Action"] == "Drop (1pt)"))
            adversaire_score = sum(adversaire_filter &  (match_data["Action"] == "Essai (4pt)")) * 4 + sum(adversaire_filter &  (match_data["Action"] == "Essai et Transformation (6pt)")) * 6 +  sum(adversaire_filter &  (match_data["Action"] == "Drop (1pt)"))
    else:
        nantes_score = 0
        adversaire_score = 0

################################################################################################################################################################################################################################################

    ### New Game ###
    if menu_choice == "En Cours":

        left, _, right = sl.columns([1, 1, 1])
        
        with left:
            sl.markdown(f'<p style="font-family:sans-serif; color:#3392FF; font-size: 36px;">{f"Nantes:   {nantes_score}"}</p>', unsafe_allow_html=True)
            sl.text("Avant")
            sl.image("before.jpg")
        with right:
            sl.markdown(f'<p style="font-family:sans-serif; color:#FF4233; font-size: 36px;">{f"Adversaire:   {adversaire_score}"}</p>', unsafe_allow_html=True)
            sl.text("Après")
            sl.image("after.jpg")

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
            place = ["Domicile ", "Extérieur"]
            place_choice = sl.selectbox("Lieu du match", place)

        with right:
            # Opponent
            teams = ["Autre", "Pujols", "Trentels", "Begles", "Clairac", "Agenais", "Villeneuve-de-Rivière"]
            team_choice = sl.selectbox("Nom de l'adversaire", teams)

        ### During Match ###
        sl.subheader("Pendant le match")

        left,center, right = sl.columns([1, 1, 1])

        with left:
            # Possesion of the ball
            ball = ["Nantes", "Adversaire"]
            ball_choice = sl.selectbox("Possession de balle", ball)

        with center:

            # Action or Event taken place
            action = ["Plaquage", "Plaquage (en but)","Coup de pied",
                      "Essai (4pt)", "Essai et Transformation (6pt)",
                      "Drop (1pt)", "Sortie de balle", "Pénalité/Faute",
                      "Pénalité (Carte Jaune)", "Pénalité (Carte Rouge)"]
            
            action_choice = sl.selectbox("Action", action)

        with right:
            # Zone of field
            zone = ["Nantes 40m", "Adversaire 40m", "Milieu"]
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

            # Add Data
            match_data = match_data.update(pl.DataFrame({"Lieu du match": place_choice,
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
            match_worksheet.update([match_data.columns] + match_data.to_numpy().tolist())
            # Refresh Page
            sl.experimental_rerun()
        
        
        # Show Data
        sl.subheader("\n Résultats")
        #st.markdown('<style>div[title="OK"] { color: green; } div[title="KO"] { color: red; } .data:hover{ background:rgb(243 246 255)}</style>', unsafe_allow_html=True)
        #'background-color : #3392FF' if match_data[["Possession"]] == "Nantes" else 'background-color : #FF4233'
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
            winner = ["Nantes", "Adversaire"]
            winner_choice = sl.selectbox("Winner", winner)
            save_delete_button = sl.button("Enregistrer et supprimer les résultats")
        # Save match data to historical data
        if save_delete_button:

            # Match Data
            historical_worksheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/14vdIL4MwuOHDxsY6bb3rfkjbbVd4iXw2ZcIwG8rNBfo/edit").sheet1
            historical_data = pl.DataFrame(historical_worksheet.get_all_records())

            # If empty, create empty dataframe
            if historical_data.height == 0:
                historical_data = pl.DataFrame(schema = ["Lieu du match", "Nom de l'adversaire", "Temps", "Mi-Temps", "Série", "Possession",  "Plaquage", "Action", "Zone", "Nantes Score", "Adversaire Score", "Winner"])
        
            match_data["Winner"] = winner_choice
            historical_data = historical_data.update(match_data)
            historical_worksheet.update([historical_data.columns] + historical_data.to_numpy().tolist())
            match_worksheet.clear()
            sl.experimental_rerun()

    return
if __name__ == "__main__":
    main()