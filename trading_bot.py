# === Script Fusionné : Bot PEA Intelligent (Analyse + IA + Automatisation Optionnelle) ===

# option a activer ou desactivé vente achat auto
ENABLE_AUTONOMOUS_TRADING = True  # True pour activer achat/vente
# option a activer ou desactivé analyse Gémini
ENABLE_AI_ANALYSIS = True         # True pour activer l’analyse IA
# Mettez à False pour désactiver la recherche d'actualités via Google_Search.
ENABLE_NEWS_SEARCH = False

# === Script PEA Professionnel Fusionné : Analyse, IA, Automatisation et Résilience Réseau ===

import yfinance as yf
import pandas as pd
import json
from datetime import datetime
from os.path import exists, join
import warnings
import google.generativeai as genai
import os
import math

# Désactiver les FutureWarnings de pandas pour un affichage plus propre
warnings.simplefilter(action='ignore', category=FutureWarning)

# --- Configuration de l'API Gemini ---
# Clé d'API fournie par l'utilisateur
genai.configure(api_key="AIzaSyDCONyUJr5Fdg9PM997oOpsfG5DZHUAU9E")

# --- Paramètres de la stratégie améliorée ---

# Dictionnaire de profils de stratégie. Choisissez-en un en modifiant la variable ci-dessous.
STRATEGY_PROFILES = {
    "prudent": {
        "EMA_SHORT": 5,
        "EMA_LONG": 20,
        "EMA_TREND_FILTER": 100, # Filtre de tendance très strict pour les tendances longues
        "RSI_PERIOD": 14,
        "RSI_OVERBOUGHT": 65,     # Seuil d'achat plus bas pour éviter le surachat
        "RSI_OVERSOLD": 35,       # Seuil de vente plus haut
        "VOLUME_AVG_PERIOD": 20,
        "ATR_PERIOD": 14,
        "ATR_MULTIPLIER_SL": 3.0,    # Stop-loss plus large pour laisser plus de marge
        "PROFIT_TARGET_PERCENT": 0.08, # Prise de profit plus rapide
    },
    "debug_simple": {
        "EMA_SHORT": 5,
        "EMA_LONG": 20,
        "EMA_TREND_FILTER": 1,         # désactivé, 0 n'est pas une valeur valide pour le span
        "RSI_PERIOD": 14,
        "RSI_OVERBOUGHT": 100,         # désactivé
        "RSI_OVERSOLD": 0,             # désactivé
        "VOLUME_AVG_PERIOD": 1,        # désactivé
        "ATR_PERIOD": 14,
        "ATR_MULTIPLIER_SL": 2.0,
        "PROFIT_TARGET_PERCENT": 0.05  # juste pour valider le TP
    },
    "normal": {
        "EMA_SHORT": 5,
        "EMA_LONG": 50,
        "EMA_TREND_FILTER": 50, # Un bon équilibre pour le filtre de tendance
        "RSI_PERIOD": 14,
        "RSI_OVERBOUGHT": 70,     # Seuil standard pour le RSI
        "RSI_OVERSOLD": 30,
        "VOLUME_AVG_PERIOD": 20,
        "ATR_PERIOD": 14,
        "ATR_MULTIPLIER_SL": 2.0,    # Stop-loss modéré
        "PROFIT_TARGET_PERCENT": 0.10, # Prise de profit équilibrée
    },
    "agressif": {
        "EMA_SHORT": 5,
        "EMA_LONG": 30,
        "EMA_TREND_FILTER": 30, # Filtre de tendance plus court pour les mouvements rapides
        "RSI_PERIOD": 14,
        "RSI_OVERBOUGHT": 75,     # Seuil d'achat plus haut pour suivre les tendances fortes
        "RSI_OVERSOLD": 25,
        "VOLUME_AVG_PERIOD": 20,
        "ATR_PERIOD": 14,
        "ATR_MULTIPLIER_SL": 1.5,    # Stop-loss plus serré
        "PROFIT_TARGET_PERCENT": 0.15, # Prise de profit plus élevée
    },
    "long_term": {
        "EMA_SHORT": 50, # EMA plus longue pour les tendances de fond
        "EMA_LONG": 100, # EMA très longue, signal d'achat/vente très puissant
        "EMA_TREND_FILTER": 100, # Filtre de tendance sur la EMA 200
        "RSI_PERIOD": 14,
        "RSI_OVERBOUGHT": 85,     # Seuil très haut pour ne pas être gêné par les petites variations
        "RSI_OVERSOLD": 15,
        "VOLUME_AVG_PERIOD": 50,
        "ATR_PERIOD": 50,
        "ATR_MULTIPLIER_SL": 4.0,    # Stop-loss très large pour ne pas être éjecté prématurément
        "PROFIT_TARGET_PERCENT": 0.50, # Objectif de profit à long terme
    },
    "ai_indice": {
        "EMA_SHORT": 9,                  # EMA rapide pour détecter les débuts de tendance
        "EMA_LONG": 21,                  # EMA plus lente pour confirmer la tendance
        "EMA_TREND_FILTER": 100,         # Filtre de tendance long terme (tu peux aussi tester 200)

        "RSI_PERIOD": 14,                # Classique mais efficace
        "RSI_OVERBOUGHT": 70,            # Seuil de surachat plus standard
        "RSI_OVERSOLD": 30,              # Seuil de survente plus standard

        "VOLUME_AVG_PERIOD": 50,         # Période inchangée pour le volume moyen
        "ATR_PERIOD": 14,                # ATR plus réactif pour s’adapter à la volatilité actuelle
        "ATR_MULTIPLIER_SL": 1.5,        # Stop-loss plus serré mais basé sur volatilité
        "ATR_MULTIPLIER_TP": 3.0,        # Objectif de profit à 3× l’ATR (meilleur ratio risque/rendement)

#        "RISK_PER_TRADE": 0.01,          // Risque fixe de 1% du capital par position (gestion de risque)
        "PROFIT_TARGET_PERCENT": 99999    # Remplacé par ATR_MULTIPLIER_TP pour un TP dynamique

    },
    "buy_and_hold": {
        "EMA_SHORT": 50,  # Achat sur une tendance de fond confirmée
        "EMA_LONG": 200,
        "EMA_TREND_FILTER": 200,
        "RSI_PERIOD": 14,
        "RSI_OVERBOUGHT": 85,
        "RSI_OVERSOLD": 15,
        "VOLUME_AVG_PERIOD": 50,
        "ATR_PERIOD": 50,
        "ATR_MULTIPLIER_SL": 0.0,    # Désactivation du stop-loss pour une stratégie de conservation
        "PROFIT_TARGET_PERCENT": 99999, # Objectif de profit extrêmement élevé (désactivé en pratique)
    },
}

# --- CHOIX DU PROFIL DE STRATÉGIE ---
# Modifiez cette ligne pour choisir votre profil de stratégie
STRATEGY_PROFILE = "debug_simple"

# Affectation dynamique des paramètres en fonction du profil choisi
params = STRATEGY_PROFILES[STRATEGY_PROFILE]
EMA_SHORT = params["EMA_SHORT"]
EMA_LONG = params["EMA_LONG"]
EMA_TREND_FILTER = params["EMA_TREND_FILTER"]
RSI_PERIOD = params["RSI_PERIOD"]
RSI_OVERBOUGHT = params["RSI_OVERBOUGHT"]
RSI_OVERSOLD = params["RSI_OVERSOLD"]
VOLUME_AVG_PERIOD = params["VOLUME_AVG_PERIOD"]
ATR_PERIOD = params["ATR_PERIOD"]
ATR_MULTIPLIER_SL = params["ATR_MULTIPLIER_SL"]
PROFIT_TARGET_PERCENT = params["PROFIT_TARGET_PERCENT"]

# --- Définition du chemin des fichiers ---
CHEMIN_FICHIERS = '/config/script/pea/'
FICHIER_LOG_PROMPT = join(CHEMIN_FICHIERS, 'prompt_analyse.log')
FICHIER_HA_DATA = join(CHEMIN_FICHIERS, 'home_assistant_data.json') # Nouveau fichier pour Home Assistant
FICHIER_HISTORIQUE_LOG = join(CHEMIN_FICHIERS, 'historique_pea.log') # Nouveau fichier de log pour l'historique
FICHIER_POSITIONS = join(CHEMIN_FICHIERS, 'positions.json') # Définition du chemin du fichier de positions
FICHIER_SYNTHESE_PORTEFEUILLE = join(CHEMIN_FICHIERS, 'synthese_portefeuille.log')

# --- Fonctions utilitaires pour lire et écrire les fichiers ---
def read_positions(file_path):
    """Lit les positions du PEA à partir d'un fichier JSON."""
    if not exists(file_path):
        print(f"[❌] Fichier de positions non trouvé : {file_path}")
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[❌] Erreur de format dans le fichier JSON : {e}")
        return None

def write_positions(file_path, data):
    """Écrit les positions du PEA dans un fichier JSON."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"[✅] Fichier de positions mis à jour : {file_path}")
        return True
    except Exception as e:
        print(f"[❌] Erreur lors de l'écriture du fichier de positions : {e}")
        return False

def read_watchlist(file_path):
    """Lit les tickers de la watchlist à partir d'un fichier texte."""
    if not exists(file_path):
        print(f"[❌] Fichier de watchlist non trouvé : {file_path}")
        return []
    with open(file_path, 'r') as f:
        tickers = {line.strip() for line in f if line.strip()}
        return list(tickers)

def get_news_with_Google_Search(ticker):
    """
    Récupère des actualités récentes pour un ticker via Google_Search.
    Cette fonction utilise l'outil 'Google_Search' pour obtenir des données réelles.
    """
    print(f"    -> Recherche d'actualités récentes pour {ticker}...")
    try:
        # Appel réel de l'outil Google_Search
        # Assurez-vous que Google_Search est correctement configuré et importé
        search_results = Google_Search(queries=[f"actualités {ticker} finance"])

        # S'assurer que le résultat n'est pas vide avant de l'analyser
        if not search_results or not search_results[0].results:
            return [f"Aucune actualité récente trouvée pour {ticker}."]

        # Extraction des titres ou des extraits pertinents
        headlines = [r.snippet for r in search_results[0].results if r.snippet]
        if not headlines:
            return [f"Aucune actualité récente trouvée pour {ticker}."]
        return headlines
    except Exception as e:
        print(f"[❌] Erreur lors de la recherche d'actualités: {e}")
        return ["Impossible de récupérer les actualités."]

def analyser_marche_par_ia(ticker, info, df, news_headlines, seuil_rentabilite=None, prix_achat=None, prix_ouverture=None):
    """
    Génère une analyse de marché détaillée en utilisant l'API Gemini.
    Le prompt est construit avec des données réelles pour une analyse précise.
    En cas de dépassement de quota ou si l'analyse IA est désactivée, le prompt est sauvegardé dans un fichier log.
    """
    print("    -> Génération de l'analyse de marché par l'IA...")

    # Extraction des indicateurs clés avec gestion des valeurs manquantes
    pe_ratio = info.get('trailingPE')
    roe = info.get('returnOnEquity')
    sector = info.get('sector')
    prix_actuel = float(df['Close'].iloc[-1])
    ema_short = float(df['EMA_SHORT'].iloc[-1])
    ema_long = float(df['EMA_LONG'].iloc[-1])
    ema_trend = float(df['EMA_TREND_FILTER'].iloc[-1])
    rsi = float(df['RSI'].iloc[-1])
    atr = float(df['ATR'].iloc[-1])

    pe_ratio_str = f"{pe_ratio:.2f}" if pe_ratio is not None else "Non disponible"
    roe_str = f"{roe:.2%}" if roe is not None else "Non disponible"
    sector_str = sector if sector else "Non disponible"

    # Construction du prompt pour l'IA
    prompt = f"""
    En tant que professionnel de la finance, je vous demande d'effectuer une analyse complète pour l'action {ticker}.
    Voici les données clés pour votre analyse :

    Analyse Fondamentale :
    - Secteur : {sector_str}
    - Ratio C/B (PER) : {pe_ratio_str}
    - ROE : {roe_str}

    Analyse Technique :
    """
    if prix_achat is not None:
        prompt += f"- Prix d'achat : {prix_achat:.2f} €\n"

    if prix_ouverture is not None:
        prompt += f"- Prix à l'ouverture : {prix_ouverture:.2f} €\n"

    prompt += f"""- Prix actuel : {prix_actuel:.2f} €
    - EMA{EMA_SHORT} : {ema_short:.2f} €
    - EMA{EMA_LONG} : {ema_long:.2f} €
    - EMA_Trend_Filter ({EMA_TREND_FILTER}) : {ema_trend:.2f} €
    - RSI ({RSI_PERIOD} jours) : {rsi:.2f}
    - ATR ({ATR_PERIOD} jours) : {atr:.2f}

    Actualités Récentes :
    {''.join([f'- {h}\n' for h in news_headlines])}

    Votre tâche est de générer un rapport structuré et professionnel qui inclut :
    1.  Une section "Actualités et Sentiment du Marché" qui synthétise les actualités fournies et dégage un sentiment général.
    2.  Une section "Conclusion et Recommandation" qui propose une recommandation claire (Acheter, Conserver, Vendre) en justifiant votre choix sur la base des trois piliers de l'analyse (fondamentale, technique, actualités).
    3.  Des conseils stratégiques supplémentaires pour un investisseur.
    4.  Si toutefois tu voulais acheter, à quel prix plancher le ferais-tu ?
    """

    if seuil_rentabilite is not None:
        prompt += f"\n5. Le seuil de rentabilité net de votre position actuelle est de {seuil_rentabilite:.2f} €. Veuillez prendre en compte cette information pour vos recommandations. "

    prompt += "\nLe rapport doit être concis et percutant."

    if not ENABLE_AI_ANALYSIS:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            with open(FICHIER_LOG_PROMPT, 'a', encoding='utf-8') as f:
                f.write(f"--- PROMPT POUR {ticker} ({timestamp}) ---\n")
                f.write(prompt)
                f.write("\n" + "="*80 + "\n\n")
            print(f"[⚠️] Analyse de l'IA désactivée. Le prompt pour {ticker} a été sauvegardé dans '{FICHIER_LOG_PROMPT}'.")
            return f"Analyse de l'IA désactivée. Le prompt a été sauvegardé pour une exécution manuelle."
        except Exception as file_error:
            print(f"[❌] Erreur lors de l'écriture dans le fichier de log : {file_error}")
            return "Analyse de l'IA désactivée. Erreur lors de la sauvegarde du prompt."

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Gérer l'erreur de dépassement de quota
        if "quota" in str(e).lower() or "429" in str(e):
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            try:
                # Écriture dans le fichier log en mode 'append'
                with open(FICHIER_LOG_PROMPT, 'a', encoding='utf-8') as f:
                    f.write(f"--- PROMPT POUR {ticker} ({timestamp}) ---\n")
                    f.write(prompt)
                    f.write("\n" + "="*80 + "\n\n")
                print(f"[⚠️] Quota de l'API dépassé. Le prompt pour {ticker} a été sauvegardé dans '{FICHIER_LOG_PROMPT}'.")
                return f"Analyse de l'IA sautée en raison du quota dépassé. Le prompt a été sauvegardé pour une exécution manuelle."
            except Exception as file_error:
                print(f"[❌] Erreur lors de l'écriture dans le fichier de log : {file_error}")
                return "Analyse de l'IA sautée en raison du quota. Erreur lors de la sauvegarde du prompt."
        else:
            print(f"[❌] Erreur lors de la génération de l'analyse par l'IA: {e}")
            return "Analyse de marché non disponible."

def log_action(ticker, signal, justification):
    """
    Enregistre les actions de trading simulées dans un fichier log dédié.
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] Ticker: {ticker} | Action: {signal} | Justification: {justification}\n"

    try:
        with open(FICHIER_HISTORIQUE_LOG, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"[❌] Erreur lors de l'écriture dans le fichier de log des actions : {e}")

def decide_and_execute_trade(ticker, df, positions_data):
    """
    SIMULATION de la décision et de l'exécution d'une transaction basée sur les EMA, le RSI et l'ATR.
    Cette fonction est une simulation et n'est pas connectée à une API de trading réelle.
    """
    ema_short_val = float(df['EMA_SHORT'].iloc[-1])
    ema_long_val = float(df['EMA_LONG'].iloc[-1])
    ema_trend_val = float(df['EMA_TREND_FILTER'].iloc[-1])
    prix_actuel = float(df['Close'].iloc[-1])
    rsi_val = float(df['RSI'].iloc[-1])

    position_info = positions_data['positions'].get(ticker)

    signal = "Garder"
    justification = "Pas de signal fort."

    print(f"\n--- 🤖 Analyse de décision pour {ticker} (Stratégie: {STRATEGY_PROFILE}) ---")
    print(f"  [i] Valeurs actuelles: Prix={prix_actuel:.2f}, EMA{EMA_SHORT}={ema_short_val:.2f}, EMA{EMA_LONG}={ema_long_val:.2f}, EMA_TREND({EMA_TREND_FILTER})={ema_trend_val:.2f}, RSI={rsi_val:.2f}")

    # --- Logique de Vente (Sell, Stop-loss ou Take-profit) ---
    if position_info and position_info['quantite'] > 0:
        print("  [i] Détection d'une position existante. Analyse des conditions de vente...")
        prix_achat = position_info['achat']
        atr_value = float(df['ATR'].iloc[-1])
        stop_loss_seuil = prix_achat - (atr_value * ATR_MULTIPLIER_SL)
        profit_target = prix_achat * (1 + PROFIT_TARGET_PERCENT)

        print(f"    - Prix d'achat: {prix_achat:.2f} €, Stop-Loss: {stop_loss_seuil:.2f} €, Take-Profit: {profit_target:.2f} €")

        # Condition 1: Stop-loss
        if prix_actuel <= stop_loss_seuil and ATR_MULTIPLIER_SL > 0:
            signal = "Vendre (Stop-Loss)"
            justification = f"Le prix actuel ({prix_actuel:.2f} €) a atteint le stop-loss basé sur l'ATR ({stop_loss_seuil:.2f} €)."
            print(f"    [✅] Condition de Stop-Loss remplie.")
        # Condition 2: Take-profit
        elif prix_actuel >= profit_target:
            signal = "Vendre (Take-Profit)"
            justification = f"Le prix actuel ({prix_actuel:.2f} €) a atteint l'objectif de profit ({profit_target:.2f} €)."
            print(f"    [✅] Condition de Take-Profit remplie.")
        # Condition 3: Croisement EMA baissier
        elif ema_short_val < ema_long_val and df['EMA_SHORT'].iloc[-2] >= df['EMA_LONG'].iloc[-2] and rsi_val > RSI_OVERSOLD:
            signal = "Vendre"
            justification = f"EMA{EMA_SHORT}({ema_short_val:.2f}) vient de croiser en dessous de EMA{EMA_LONG}({ema_long_val:.2f}) et le RSI est à {rsi_val:.2f}."
            print(f"    [✅] Condition de croisement EMA baissier remplie.")
        else:
            print("    [❌] Aucune condition de vente remplie. Maintien de la position.")

    # --- Logique d'Achat ---
    else:
        print("  [i] Aucune position existante. Analyse des conditions d'achat...")
        # Condition 1: Tendance de fond haussière
        if prix_actuel > ema_trend_val:
            print(f"    [✅] Condition de tendance de fond haussière remplie (Prix {prix_actuel:.2f} > EMA{EMA_TREND_FILTER} {ema_trend_val:.2f}).")
            # Condition 2: Croisement EMA haussier et RSI non suracheté
            if ema_short_val > ema_long_val and df['EMA_SHORT'].iloc[-2] <= df['EMA_LONG'].iloc[-2] and rsi_val < RSI_OVERBOUGHT:
                signal = "Acheter"
                justification = f"Tendance haussière confirmée (prix > EMA{EMA_TREND_FILTER}). EMA{EMA_SHORT} a croisé EMA{EMA_LONG} et le RSI est à {rsi_val:.2f}."
                print(f"    [✅] Condition de croisement EMA haussier remplie (EMA{EMA_SHORT} > EMA{EMA_LONG}) avec RSI ({rsi_val:.2f}) < {RSI_OVERBOUGHT}.")
            else:
                print(f"    [❌] Condition de croisement EMA haussier non remplie ou RSI en surachat.")
                print(f"       - Croisement EMA{EMA_SHORT} > EMA{EMA_LONG}: {ema_short_val > ema_long_val}")
                print(f"       - Croisement précédent: {df['EMA_SHORT'].iloc[-2] <= df['EMA_LONG'].iloc[-2]}")
                print(f"       - RSI < {RSI_OVERBOUGHT}: {rsi_val < RSI_OVERBOUGHT}")
        else:
            print(f"    [❌] Condition de tendance de fond haussière non remplie (Prix {prix_actuel:.2f} <= EMA{EMA_TREND_FILTER} {ema_trend_val:.2f}).")


    print(f"\n--- 🤖 Signal de trading autonome pour {ticker} ---")
    print(f"Stratégie utilisée : {STRATEGY_PROFILE}")
    print(f"Signal: {signal}")
    print(f"Justification: {justification}")

    if ENABLE_AUTONOMOUS_TRADING:
        # --- LOGIQUE D'EXÉCUTION SIMULÉE ---
        if signal.startswith("Acheter"):
            montant_a_investir = positions_data['liquidite'] * INVESTMENT_PERCENT_PER_TRADE

            if montant_a_investir > prix_actuel + AVERAGE_TRANSACTION_FEE:
                quantite_achat = math.floor((montant_a_investir - AVERAGE_TRANSACTION_FEE) / prix_actuel)

                if quantite_achat > 0:
                    cout_total_achat = (prix_actuel * quantite_achat) + AVERAGE_TRANSACTION_FEE

                    prix_achat_moyen_actuel = position_info['achat'] if position_info and 'achat' in position_info else 0
                    quantite_actuelle = position_info['quantite'] if position_info and 'quantite' in position_info else 0

                    if quantite_actuelle > 0:
                        nouveau_prix_achat = ((prix_achat_moyen_actuel * quantite_actuelle) + (prix_actuel * quantite_achat)) / (quantite_actuelle + quantite_achat)
                    else:
                        nouveau_prix_achat = prix_actuel

                    nouvelle_quantite = quantite_actuelle + quantite_achat

                    positions_data['liquidite'] -= cout_total_achat
                    positions_data['positions'][ticker] = {'achat': nouveau_prix_achat, 'quantite': nouvelle_quantite}

                    print(f"[✅] SIMULATION: Ordre d'achat de {quantite_achat} titres de {ticker} exécuté.")
                    log_action(ticker, f"Acheter (exécuté - {quantite_achat} titres)", justification)
                else:
                    print(f"[⚠️] SIMULATION: Montant à investir insuffisant pour acheter un titre de {ticker}. Achat non exécuté.")
                    log_action(ticker, "Acheter (non exécuté - montant)", justification)
            else:
                print(f"[⚠️] SIMULATION: Montant à investir insuffisant pour acheter un titre de {ticker}. Achat non exécuté.")
                log_action(ticker, "Acheter (non exécuté - montant)", justification)

        elif signal.startswith("Vendre"):
            if position_info and position_info['quantite'] > 0:
                quantite_vente = position_info['quantite']
                gain_vente_net = (prix_actuel * quantite_vente) - AVERAGE_TRANSACTION_FEE

                positions_data['liquidite'] += gain_vente_net
                positions_data['positions'][ticker]['quantite'] = 0
                positions_data['positions'][ticker]['achat'] = 0

                print(f"[✅] SIMULATION: Ordre de vente de {quantite_vente} titres de {ticker} exécuté.")
                log_action(ticker, f"Vendre (exécuté - {quantite_vente} titres)", justification)
            else:
                print(f"[⚠️] SIMULATION: Aucune position à vendre pour {ticker}. Vente non exécutée.")
                log_action(ticker, "Vendre (non exécuté - pas de position)", justification)
        else:
            print("L'exécution des ordres est activée. Aucune action n'a été prise.")
            log_action(ticker, signal, justification)
    else:
        print("L'exécution des ordres est désactivée. Aucune action n'a été prise.")
        log_action(ticker, signal, justification)

    return signal, justification

# --- Fonction principale d'analyse professionnelle ---
def analyser_titre_professionnel(ticker, positions_data):
    """
    Effectue une analyse multifactorielle d'une action pour un portefeuille ou une watchlist.
    L'analyse inclus des aspects techniques, fondamentaux, et de gestion du risque.
    """
    print(f"\n{'='*60}\nAnalyse professionnelle pour {ticker}\n{'='*60}")

    df = None
    info = None
    position_info = positions_data['positions'].get(ticker)
    ha_data = { # Initialisation du dictionnaire pour Home Assistant
        "ticker": ticker,
        "prix_actuel": None,
        "prix_ouverture": None,
        "evolution_jour_eur": None,
        "evolution_jour_pct": None,
        "secteur": None,
        "per": None,
        "roe": None,
        "ema_short": None,
        "ema_long": None,
        "ema_trend_filter": None,
        "rsi": None,
        "atr": None,
        "prix_achat": None,
        "quantite": None,
        "seuil_rentabilite": None,
        "stop_loss_seuil": None,
        "profit_target_seuil": None,
        "alerte_stop_loss": False,
        "recommandation_ia": None,
        "news_summary": None,
        "signal_trading": "Garder",
        "justification_trading": "Non analysé."
    }

    try:
        # Nettoyage du ticker pour enlever le préfixe de la bourse si présent
        cleaned_ticker = ticker.split(':')[-1].strip()
        # Téléchargement des données historiques et des informations fondamentales
        stock = yf.Ticker(cleaned_ticker)
        # On télécharge plus de données pour les EMA plus longues et l'ATR
        df = stock.history(period='6mo', interval='1d', auto_adjust=True)
        info = stock.info
    except Exception as e:
        print(f"[❌] Erreur lors de la récupération des données pour {ticker} (utilisant le ticker {cleaned_ticker}): {e}")
        return ha_data # Retourne les données HA même en cas d'erreur de récupération

    # Vérifications de robustesse
    if df is None or df.empty or 'Close' not in df.columns:
        print(f"[⛔️] Données historiques insuffisantes ou invalides pour {ticker}. Impossible de continuer l'analyse.")
        return ha_data

    # Correction : Filtrage explicite pour les valeurs non-NaN
    df = df[df['Close'].notna()]
    if len(df) < max(EMA_LONG, EMA_TREND_FILTER, ATR_PERIOD, RSI_PERIOD, VOLUME_AVG_PERIOD) + 1:
        print(f"[⛔️] Données insuffisantes après nettoyage pour {ticker} (minimum {max(EMA_LONG, EMA_TREND_FILTER, ATR_PERIOD, RSI_PERIOD, VOLUME_AVG_PERIOD) + 1} jours nécessaires). {len(df)} jours disponibles.")
        return ha_data

    # Calcul et extraction des indicateurs techniques
    try:
        prix_ouverture = float(df['Open'].iloc[-1])
        prix_actuel = float(df['Close'].iloc[-1])
        df['EMA_SHORT'] = df['Close'].ewm(span=EMA_SHORT, adjust=False).mean()
        df['EMA_LONG'] = df['Close'].ewm(span=EMA_LONG, adjust=False).mean()
        df['EMA_TREND_FILTER'] = df['Close'].ewm(span=EMA_TREND_FILTER, adjust=False).mean()

        # Calcul du RSI (Relative Strength Index)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=RSI_PERIOD).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=RSI_PERIOD).mean()
        with pd.option_context('mode.use_inf_as_na', True):
            rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # Calcul de l'ATR (Average True Range)
        df['tr'] = df[['High', 'Low', 'Close']].max(axis=1) - df[['High', 'Low', 'Close']].min(axis=1)
        df['ATR'] = df['tr'].ewm(span=ATR_PERIOD, adjust=False).mean()

        # Calcul du MACD (Moving Average Convergence Divergence)
        exp12 = df['Close'].ewm(span=12, adjust=False).mean()
        exp26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp12 - exp26
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

        # --- Affichage des indicateurs techniques et fondamentaux ---
        print("\n--- 📊 Indicateurs Clés ---")
        pe_ratio = info.get('trailingPE')
        roe = info.get('returnOnEquity')
        sector = info.get('sector')
        ema_short = float(df['EMA_SHORT'].iloc[-1])
        ema_long = float(df['EMA_LONG'].iloc[-1])
        ema_trend = float(df['EMA_TREND_FILTER'].iloc[-1])
        rsi = float(df['RSI'].iloc[-1])
        atr = float(df['ATR'].iloc[-1])

        # Remplir ha_data avec les informations de base
        ha_data["prix_actuel"] = prix_actuel
        ha_data["prix_ouverture"] = prix_ouverture
        ha_data["secteur"] = sector
        ha_data["per"] = pe_ratio
        ha_data["roe"] = roe
        ha_data["ema_short"] = ema_short
        ha_data["ema_long"] = ema_long
        ha_data["ema_trend_filter"] = ema_trend
        ha_data["rsi"] = rsi
        ha_data["atr"] = atr

        prix_achat_moyen = None
        if position_info and 'achat' in position_info:
            prix_achat_moyen = position_info['achat']
            ha_data["prix_achat"] = prix_achat_moyen
            ha_data["quantite"] = position_info['quantite']
            print(f"Prix d'achat      : {prix_achat_moyen:.2f} €")

        evolution = prix_actuel - prix_ouverture
        evolution_pct = (evolution / prix_ouverture) * 100 if prix_ouverture != 0 else 0

        evolution_str = ""
        if evolution > 0:
            evolution_str = f"▲ +{evolution:.2f} € (+{evolution_pct:.2f}%)"
        elif evolution < 0:
            evolution_str = f"▼ {evolution:.2f} € ({evolution_pct:.2f}%)"
        else:
            evolution_str = "● Stable"

        ha_data["evolution_jour_eur"] = evolution
        ha_data["evolution_jour_pct"] = evolution_pct

        print(f"Prix à l'ouverture: {prix_ouverture:.2f} €")
        print(f"Prix actuel       : {prix_actuel:.2f} €")
        print(f"Évolution du jour : {evolution_str}")

        seuil_rentabilite_unitaire = None
        stop_loss_seuil = None
        profit_target_seuil = None

        if position_info and 'achat' in position_info and 'quantite' in position_info and position_info['quantite'] > 0:
            cout_total_achat = position_info['achat'] * position_info['quantite'] + AVERAGE_TRANSACTION_FEE
            frais_vente = AVERAGE_TRANSACTION_FEE
            seuil_rentabilite_total = cout_total_achat + frais_vente
            seuil_rentabilite_unitaire = seuil_rentabilite_total / position_info['quantite']
            ha_data["seuil_rentabilite"] = seuil_rentabilite_unitaire
            print(f"Seuil de rentabilité: {seuil_rentabilite_unitaire:.2f} €")

            stop_loss_seuil = prix_achat_moyen - (atr * ATR_MULTIPLIER_SL)
            ha_data["stop_loss_seuil"] = stop_loss_seuil
            if prix_actuel < stop_loss_seuil and ATR_MULTIPLIER_SL > 0:
                ha_data["alerte_stop_loss"] = True
                print(f"[🚨] Le prix actuel ({prix_actuel:.2f} €) est en dessous de votre stop-loss ({stop_loss_seuil:.2f} €) !")

            profit_target_seuil = prix_achat_moyen * (1 + PROFIT_TARGET_PERCENT)
            ha_data["profit_target_seuil"] = profit_target_seuil


        print(f"Secteur           : {sector if sector else 'Non disponible'}")
        print(f"Ratio C/B (PER)   : {pe_ratio:.2f}" if pe_ratio else "Ratio C/B : Non disponible")
        print(f"ROE               : {roe:.2%}" if roe else "ROE : Non disponible")
        print(f"EMA{EMA_SHORT}              : {ema_short:.2f} €")
        print(f"EMA{EMA_LONG}             : {ema_long:.2f} €")
        print(f"EMA_TREND_FILTER{EMA_TREND_FILTER} : {ema_trend:.2f} €")
        print(f"RSI ({RSI_PERIOD} jours)    : {rsi:.2f}")
        print(f"ATR ({ATR_PERIOD} jours)    : {atr:.2f}")

        if stop_loss_seuil is not None:
             print(f"Stop-Loss (ATR)    : {stop_loss_seuil:.2f} €")
        if profit_target_seuil is not None:
             print(f"Profit Target      : {profit_target_seuil:.2f} €")

        if ENABLE_NEWS_SEARCH:
            news_headlines = get_news_with_Google_Search(ticker)
        else:
            news_headlines = ["La recherche d'actualités est désactivée."]
            print("[⚠️] La recherche d'actualités est désactivée. L'analyse de l'IA sera basée uniquement sur les autres indicateurs.")

        signal_trading, justification_trading = decide_and_execute_trade(ticker, df, positions_data)
        ha_data["signal_trading"] = signal_trading
        ha_data["justification_trading"] = justification_trading

        ai_analysis_result = analyser_marche_par_ia(ticker, info, df, news_headlines, seuil_rentabilite_unitaire, prix_achat=prix_achat_moyen, prix_ouverture=prix_ouverture)
        ha_data["recommandation_ia"] = ai_analysis_result

        print("\n" + "="*60)
        print("Analyse complète par l'IA")
        print("="*60)
        print(ai_analysis_result)

        return ha_data

    except Exception as e:
        print(f"[❌] Erreur inattendue lors de l'analyse de {ticker} : {e}")
        return ha_data

# --- Exécution principale du script ---
if __name__ == "__main__":

    chemin_positions = join(CHEMIN_FICHIERS, 'positions.json')
    chemin_watchlist = join(CHEMIN_FICHIERS, 'watchlist_pea.txt')

    if exists(FICHIER_LOG_PROMPT):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{FICHIER_LOG_PROMPT}.{timestamp}.bak"
        os.rename(FICHIER_LOG_PROMPT, backup_file)
        print(f"[✅] Fichier de log précédent sauvegardé en : {backup_file}")

    positions_data = read_positions(chemin_positions)
    watchlist_tickers = read_watchlist(chemin_watchlist)

    all_tickers = set(watchlist_tickers)
    if positions_data and 'positions' in positions_data:
        all_tickers.update(positions_data['positions'].keys())

    print("=" * 60)
    print(f"RAPPORT D'ANALYSE DU PORTEFEUILLE PEA ({datetime.today().strftime('%d/%m/%Y')})")
    print("=" * 60)

    if positions_data and 'liquidite' in positions_data:
        print(f"[💰] Liquidité disponible : {positions_data['liquidite']:.2f} €\n")

    if not all_tickers:
        print("[ℹ️] Aucune action trouvée dans les fichiers 'positions.json' et 'watchlist_pea.txt'.")
        print("Veuillez les renseigner pour commencer l'analyse.")
    else:
        all_analyzed_data_for_ha = {}
        portefeuille_performances = {}

        for ticker in sorted(list(all_tickers)):
            ticker_ha_data = analyser_titre_professionnel(ticker, positions_data)

            if ticker_ha_data:
                all_analyzed_data_for_ha[ticker] = ticker_ha_data

                position_info = positions_data['positions'].get(ticker)
                if position_info and 'quantite' in position_info and 'achat' in position_info and ticker_ha_data['prix_actuel'] is not None:
                    portefeuille_performances[ticker] = {
                        'quantite': position_info['quantite'],
                        'prix_achat_moyen': position_info['achat'],
                        'prix_actuel': ticker_ha_data['prix_actuel']
                    }
                elif position_info:
                    print(f"[⚠️] Les données de position pour '{ticker}' sont incomplètes dans 'positions.json' et seront ignorées dans la synthèse du portefeuille.")

    if positions_data:
        write_positions(FICHIER_POSITIONS, positions_data)

    print("\n" + "=" * 60)
    print("Analyse complète terminée.")

    total_valeur_portefeuille = 0
    total_investissement_initial = 0

    if portefeuille_performances:

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_content = f"============================================================\n"
        log_content += f"SYNTHÈSE DU PORTEFEUILLE ({timestamp})\n"
        log_content += f"============================================================\n"

        print("\n" + "=" * 60)
        print("SYNTHÈSE DU PORTEFEUILLE")
        print("=" * 60)
        print(f"Stratégie utilisée : {STRATEGY_PROFILE}") # Nouvelle ligne ajoutée ici
        for ticker, perf_data in portefeuille_performances.items():
            valeur_actuelle = perf_data['quantite'] * perf_data['prix_actuel']
            investissement_initial = perf_data['quantite'] * perf_data['prix_achat_moyen']
            gain_perte = valeur_actuelle - investissement_initial
            rendement_pct = (gain_perte / investissement_initial) * 100 if investissement_initial != 0 else 0

            total_valeur_portefeuille += valeur_actuelle
            total_investissement_initial += investissement_initial

            signe_gain = "▲" if gain_perte > 0 else "▼" if gain_perte < 0 else "●"

            line = f"- {ticker} : {signe_gain} {gain_perte:.2f} € ({rendement_pct:.2f}%)"
            print(line)
            log_content += line + "\n"

        total_gain_perte_portefeuille = total_valeur_portefeuille - total_investissement_initial
        total_rendement_pct = (total_gain_perte_portefeuille / total_investissement_initial) * 100 if total_investissement_initial != 0 else 0

        print("\n--- Totaux du portefeuille ---")
        log_content += "\n--- Totaux du portefeuille ---\n"
        print(f"Valeur actuelle du portefeuille : {total_valeur_portefeuille:.2f} €")
        log_content += f"Valeur actuelle du portefeuille : {total_valeur_portefeuille:.2f} €\n"

        signe_total = "▲" if total_gain_perte_portefeuille > 0 else "▼" if total_gain_perte_portefeuille < 0 else "●"

        print(f"Gain/Perte total : {signe_total} {total_gain_perte_portefeuille:.2f} €")
        log_content += f"Gain/Perte total : {signe_total} {total_gain_perte_portefeuille:.2f} €\n"
        print(f"Rendement total : {total_rendement_pct:.2f} %")
        log_content += f"Rendement total : {total_rendement_pct:.2f} %\n"
        print("\n" + "=" * 60)
        log_content += "=" * 60 + "\n\n"

        try:
            with open(FICHIER_SYNTHESE_PORTEFEUILLE, 'a', encoding='utf-8') as f:
                f.write(log_content)
            print(f"[✅] Synthèse du portefeuille enregistrée dans : {FICHIER_SYNTHESE_PORTEFEUILLE}")
        except Exception as e:
            print(f"[❌] Erreur lors de l'écriture de la synthèse dans le fichier log : {e}")
    else:
        print("[ℹ️] Aucune position valide trouvée pour la synthèse du portefeuille.")

    ha_output_data = {
        "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "global_portfolio": {
            "liquidite": positions_data.get('liquidite', 0.0) if positions_data else 0.0,
            "valeur_actuelle_portefeuille": total_valeur_portefeuille,
            "gain_perte_total": total_gain_perte_portefeuille,
            "rendement_total_pct": total_rendement_pct
        },
        "actions": all_analyzed_data_for_ha
    }

    try:
        with open(FICHIER_HA_DATA, 'w', encoding='utf-8') as f:
            json.dump(ha_output_data, f, indent=4)
        print(f"\n[✅] Données pour Home Assistant sauvegardées dans : {FICHIER_HA_DATA}")
    except Exception as e:
        print(f"[❌] Erreur lors de la sauvegarde des données pour Home Assistant : {e}")

    print("\n" + "=" * 60)
    print("Exécution du script terminée.")
    print("=" * 60) /// j ai un probleme avec les parametres de stratégie  je voudrais que tu intégre cette notion 🔧 Stratégie de debug minimaliste pour test
json
Copier
Modifier
"debug_simple": {
    "EMA_SHORT": 5,
    "EMA_LONG": 20,
    "EMA_TREND_FILTER": 0,         // désactivé
    "RSI_PERIOD": 14,
    "RSI_OVERBOUGHT": 100,         // désactivé
    "RSI_OVERSOLD": 0,             // désactivé
    "VOLUME_AVG_PERIOD": 1,        // désactivé
    "ATR_PERIOD": 14,
    "ATR_MULTIPLIER_SL": 2.0,
    "PROFIT_TARGET_PERCENT": 0.05  // juste pour valider le TP
}


📊 Conclusion
Il est normal que ton bot ne trouve aucun trade si :

Tes critères sont trop contraignants

Tu es dans une période de marché plate

Le timeframe est mal adapté à la stratégie

Il y a un bug silencieux dans ta logique

intégrer des logs intelligents dans ton code pour comprendre ce qui empêche les signaux d’être déclenchés.
