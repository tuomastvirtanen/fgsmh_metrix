import html
import os

import pandas as pd
import requests


def nayta_logo():
    """Tulostaa FGSMH-logon ja laskentasäännöt."""
    os.system("cls" if os.name == "nt" else "clear")
    print(r"""
     /$$$$$$$$  /$$$$$$   /$$$$$$  /$$      /$$ /$$   /$$
    | $$_____/ /$$__  $$ /$$__  $$| $$$    /$$$| $$  | $$
    | $$      | $$  \__/| $$  \__/| $$$$  /$$$$| $$  | $$
    | $$$$$   | $$ /$$$$|  $$$$$$ | $$ $$/$$ $$| $$$$$$$$
    | $$__/   | $$|_  $$ \____  $$| $$  $$$| $$| $$__  $$
    | $$      | $$  \ $$ /$$  \ $$| $$\  $ | $$| $$  | $$
    | $$      |  $$$$$$/|  $$$$$$/| $$ \/  | $$| $$  | $$
    |__/       \______/  \______/ |__/     |__/|__/  |__/
    """)
    print("=" * 75)
    print("     M E T R I X   P I S T E L A S K U R I   (v2026.04.06)")
    print("=" * 75)
    print("     Säännöt: (N-Sija) + 1p osallistuminen. Max 8 parasta kisaa.")
    print("-" * 75)


def hae_metrix_data(kilpailu_id):
    """Hakee datan Metrixin rajapinnasta."""
    url = f"https://discgolfmetrix.com/api.php?content=result&id={kilpailu_id}"
    try:
        print(f"🌐 Haetaan kisan {kilpailu_id} tiedot...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Virhe rajapintahassa: {e}")
        return None


def parsi_yksittainen_kisa_sarjamuotoon(comp):
    """Muuntaa yksittäisen kisan datan sarjamuotoon."""
    kisan_nimi = html.unescape(comp.get("Name", "Yksittäinen kisa"))
    results = comp.get("Results", [])
    event_names = [kisan_nimi]
    rows = []
    for player in results:
        row = {
            "UserID": str(player.get("UserID", "")),
            "Nimi": player.get("Name", "Tuntematon"),
            "Maa": player.get("CountryCode", "FI"),
            kisan_nimi: player.get("Sum"),
        }
        rows.append(row)
    return pd.DataFrame(rows), event_names, kisan_nimi


def parsi_perustulokset(json_data):
    """Parsii JSON-datan ja tunnistaa onko kyseessä sarja vai yksittäinen kisa."""
    comp = json_data.get("Competition", {})
    if "TourResults" in comp:
        print("📊 Tunnistettu: Sarjakilpailu / Liiga")
        events = comp.get("Events", [])
        event_names = [html.unescape(e["Name"]) for e in events]
        tour_results = comp.get("TourResults", [])
        rows = []
        for player in tour_results:
            row = {
                "UserID": str(player["UserID"]),
                "Nimi": player["Name"],
                "Maa": player["CountryCode"],
            }
            results = player["EventResults"]
            for i, name in enumerate(event_names):
                row[name] = results[i] if i < len(results) else None
            rows.append(row)
        kisan_nimi = html.unescape(comp.get("Name", "Kisa"))
        return pd.DataFrame(rows), event_names, kisan_nimi
    else:
        print("🎯 Tunnistettu: Yksittäinen kilpailu")
        return parsi_yksittainen_kisa_sarjamuotoon(comp)


def laske_sarjapisteet(df, event_columns, max_events=8):
    """Laskee sijoituspisteet ja osallistumisbonukset."""
    rank_points_df = pd.DataFrame(index=df.index)
    participation_count = pd.Series(0, index=df.index)

    for event in event_columns:
        scores = pd.to_numeric(df[event], errors="coerce")
        valid_mask = scores.notna()
        participated_scores = scores[valid_mask]

        if participated_scores.empty:
            rank_points_df[event] = 0.0
            continue

        N = len(participated_scores)
        ranks = participated_scores.rank(method="min", ascending=True)
        event_rank_points = N - ranks

        rank_points_df.loc[valid_mask, event] = event_rank_points
        rank_points_df.loc[~valid_mask, event] = 0.0
        participation_count[valid_mask] += 1

    top_8_rank_sum = rank_points_df[event_columns].apply(
        lambda row: row.nlargest(max_events).sum(), axis=1
    )

    results = df[["UserID", "Nimi"]].copy()

    # LISÄYS: Lisätään osakilpailukohtaiset pisteet sarakkeiksi Exceliä varten
    for event in event_columns:
        results[f"Pisteet: {event}"] = rank_points_df[event]

    results["Sijoituspisteet_8_parasta"] = top_8_rank_sum
    results["Osallistumiset_yht"] = participation_count
    results["Kokonaispisteet"] = top_8_rank_sum + participation_count
    results["Sarjasijoitus"] = (
        results["Kokonaispisteet"].rank(method="min", ascending=False).astype(int)
    )

    return results.sort_values(by="Kokonaispisteet", ascending=False), rank_points_df


def main():
    nayta_logo()
    kisa_id = input("Syötä Metrix Competition ID: ").strip()
    if not kisa_id:
        return

    json_data = hae_metrix_data(kisa_id)
    if not json_data:
        return

    df_tulokset, event_names, kisan_nimi = parsi_perustulokset(json_data)
    df_sarjataulukko, df_rank_only = laske_sarjapisteet(df_tulokset, event_names)

    tiedostonimi = f"FGSMH_Sarjataulukko_{kisa_id}.xlsx"
    try:
        with pd.ExcelWriter(tiedostonimi, engine="openpyxl") as writer:
            df_sarjataulukko.to_excel(writer, sheet_name="Sarjapisteet", index=False)
            df_tulokset.to_excel(writer, sheet_name="Heitetyt_Tulokset", index=False)

        # TERMINAALITULOSTUS
        print(f"\nSARJATAULUKKO: {kisan_nimi}")

        # Dynaaminen otsikko: K1, K2... osakilpailuille
        header = f"{'SIJA':<5} {'PELAAJA':<20}"
        for i in range(len(event_names)):
            header += f"{'K' + str(i + 1):>4}"
        header += f" {'LKM':>4} {'YHT':>5}"

        print("-" * len(header))
        print(header)
        print("-" * len(header))

        for _, row in df_sarjataulukko.head(30).iterrows():
            line = f"{row['Sarjasijoitus']:<5} {row['Nimi'][:20]:<20}"
            for event in event_names:
                p = row[f"Pisteet: {event}"]
                line += f"{int(p):>4}" if p > 0 else f"{'-':>4}"
            line += (
                f" {int(row['Osallistumiset_yht']):>4} {int(row['Kokonaispisteet']):>5}"
            )
            print(line)

        print("-" * len(header))
        print(f"✅ Tallennettu: {tiedostonimi}")

    except Exception as e:
        print(f"❌ Virhe tallennuksessa: {e}")


if __name__ == "__main__":
    main()
