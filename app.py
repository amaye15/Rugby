import streamlit as sl
import datetime as dt
import gspread
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def main():
    # Connect to Google
    gc = gspread.service_account(filename="cred.json")

    ### Image ###
    _, center, _ = sl.columns([1, 1, 1])
    with center:
        sl.image("logo.png")

    ### Title ###
    sl.title("Les Vikings - Rugby XIII")

    ### Side Bar ###
    menu = ["Nouveau", "Précédent"]
    menu_choice = sl.sidebar.selectbox("Match", menu)

    ### New Game ###
    if menu_choice == "Nouveau":
        # Title
        sl.header("Nouveau Match !!! \n Ajoutez les informations suivantes pendant le match. ")
        
        # Match Data
        match_worksheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1F0NI-6_oi_geBDIJge9b6FXipMUyDw3XR90rHDALCx8/edit").sheet1
        match_data = pd.DataFrame(match_worksheet.get_all_records())

        # If empty, create empty dataframe
        if match_data.empty:
            match_data = pd.DataFrame(columns=["Lieu du match", "Nom de l'adversaire", "Temps", "Mi-Temps", "Série", "Possession",  "Evénement", "Action", "Zone"])
        
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
            action = ["Plaquage", "Coup de pied", "Pénalité/Faute",
                      "Essai (4pt)", "Essai et Transformation (6pt)", 
                      "Sortie de balle", "Plaquage (en but)"]
            action_choice = sl.selectbox("Action", action)

        with right:
            # Zone of field
            zone = ["Nantes 40m", "Adversaire 40m", "Milieu"]
            zone_choice = sl.selectbox("Zone", zone)
        
        # Update Results
        if sl.button("Mise à jour des résultats"):
            
            # Automatically determine series
            if match_data.empty:
                series = 1
            elif match_data["Possession"].values[-1] == ball_choice:
                series = match_data["Série"].values[-1]
            else:
                series = match_data["Série"].values[-1] + 1

            # Automatically determine series
            if match_data.empty:
                event = 1
            elif match_data["Possession"].values[-1] == ball_choice and match_data["Action"].values[-1] == "Plaquage" and action_choice == "Plaquage":
                event = match_data["Evénement"].values[-1] + 1
            elif match_data["Possession"].values[-1] == ball_choice and match_data["Action"].values[-1] == "Plaquage" and action_choice == "Coup de pied":
                event = match_data["Evénement"].values[-1] + 1
            elif match_data["Possession"].values[-1] == ball_choice and match_data["Action"].values[-1] == "Plaquage" and action_choice == "Essai (4pt)":
                event = match_data["Evénement"].values[-1] + 1
            elif match_data["Possession"].values[-1] == ball_choice and match_data["Action"].values[-1] == "Plaquage" and action_choice == "Essai et Transformation (6pt)":
                event = match_data["Evénement"].values[-1] + 1
            else:
                event = 1

            # Automatically determine half
            if match_data.empty:
                half = "Première"
            elif ((dt.datetime.now() - pd.to_datetime(match_data["Temps"].values[0])).total_seconds() / 60) < 40:
                half = "Première"
            else:
                half = "Deuxième"

            # Add Data
            match_data = match_data.append({"Lieu du match": place_choice,
                         "Nom de l'adversaire": team_choice,
                         "Temps": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                         "Mi-Temps": half,
                         "Série": series,
                         "Possession": ball_choice,
                         "Evénement": event, 
                         "Action": action_choice, 
                         "Zone": zone_choice}, ignore_index=True)
            match_worksheet.update([match_data.columns.values.tolist()] + match_data.values.tolist())
            # Refresh Page
            sl.experimental_rerun()
        # Show Data
        sl.subheader("\n Résultats")
        sl.dataframe(match_data[["Série", "Evénement", "Possession", "Action", "Zone"]], use_container_width=True)
        
        ### Delete Row ###
        left, _, _ = sl.columns([1.3, 2, 2])
        with left:
            row = match_data.index.tolist()
            row_choice = sl.selectbox("Ligne", row)
            delete_button = sl.button("Supprimer une ligne")
            sl.text("Note : le changement n'apparaîtra pas tant que vous n'aurez pas ajouté une nouvelle ligne.")
        # Delete button
        if delete_button: 
            match_worksheet.delete(row_choice)
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
            historical_data = pd.DataFrame(historical_worksheet.get_all_records())

            # If empty, create empty dataframe
            if historical_data.empty:
                historical_data = pd.DataFrame(columns=["Lieu du match", "Nom de l'adversaire", "Temps", "Mi-Temps", "Série", "Possession",  "Plaquage", "Action", "Zone", "Winner"])
        
            match_data["Winner"] = winner_choice
            historical_data = historical_data.append(match_data, ignore_index=True)
            historical_worksheet.update([historical_data.columns.values.tolist()] + historical_data.values.tolist())
            sl.experimental_rerun()

    return
if __name__ == "__main__":
    main()