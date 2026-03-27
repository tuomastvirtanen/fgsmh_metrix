import pandas as pd
import requests
import sys
import os

def nayta_logo():
    """Tulostaa FGSMH-logon ja laskentasäännöt."""
    os.system('cls' if os.name == 'nt' else 'clear')
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
    print("=" * 65)
    print("     M E T R I X   P I S T E L A S K U R I ")
    print("=" * 65)
    print("     Säännöt:")
    print("     1. Sijoituspisteet: (Osallistujat - Sija)")
    print("     2. Jaetut sijat: Molemmat saavat parhaan sijoituksen pisteet")
    print("     3. Sarjapisteet: 8 parasta sijoituspiste-kierrosta")
    print("     4. Osallistumisbonus: +1p per startti loppusummaan")
    print(" ")
    print("     Tuomas Virtanen 2026-03-27")
    print("-" * 65)

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

def parsi_perustulokset(json_data):
    """Parsii JSON-datan perusmuotoon."""
    comp = json_data.get('Competition', {})
    events = comp.get('Events', [])
    event_names = [e['Name'] for e in events]
    tour_results = comp.get('TourResults', [])
    
    rows = []
    for player in tour_results:
        row = {
            'UserID': str(player['UserID']),
            'Nimi': player['Name'],
            'Maa': player['CountryCode']
        }
        results = player['EventResults']
        for i, name in enumerate(event_names):
            val = results[i] if i < len(results) else None
            row[name] = val
        rows.append(row)
    
    return pd.DataFrame(rows), event_names, comp.get('Name', 'Kisa')

def laske_sarjapisteet(df, event_columns, max_events=8):
    """Laskee sijoituspisteet ja osallistumisbonukset."""
    rank_points_df = pd.DataFrame(index=df.index)
    participation_count = pd.Series(0, index=df.index)
    
    print("🧮 Lasketaan kierroskohtaisia sijoituspisteitä...")
    for event in event_columns:
        scores = pd.to_numeric(df[event], errors='coerce')
        valid_mask = scores.notna()
        participated_scores = scores[valid_mask]
        
        if participated_scores.empty:
            rank_points_df[event] = 0.0
            continue
            
        N = len(participated_scores)
        ranks = participated_scores.rank(method='min', ascending=True)
        
        event_rank_points = (N - ranks)
        
        rank_points_df.loc[valid_mask, event] = event_rank_points
        rank_points_df.loc[~valid_mask, event] = 0.0
        
        participation_count[valid_mask] += 1

    top_8_rank_sum = rank_points_df[event_columns].apply(
        lambda row: row.nlargest(max_events).sum(), axis=1
    )
    
    results = df[['UserID', 'Nimi']].copy()
    for event in event_columns:
        results[event] = rank_points_df[event]
        
    results['Sijoituspisteet_8_parasta'] = top_8_rank_sum
    results['Osallistumiset_yht'] = participation_count
    results['Kokonaispisteet'] = top_8_rank_sum + participation_count
    
    # Lasketaan sijoitus kokonaispisteiden perusteella
    results['Sarjasijoitus'] = results['Kokonaispisteet'].rank(method='min', ascending=False).astype(int)
    
    return results.sort_values(by='Kokonaispisteet', ascending=False)

def main():
    nayta_logo()
    
    kisa_id = input("Syötä Metrix Competition ID (esim. 3519469): ").strip()
    if not kisa_id:
        print("❌ ID vaaditaan.")
        return

    json_data = hae_metrix_data(kisa_id)
    
    if not json_data or 'Competition' not in json_data:
        print("❌ Dataa ei saatu. Tarkista ID.")
        return

    df_tulokset, event_names, kisan_nimi = parsi_perustulokset(json_data)
    df_sarjataulukko = laske_sarjapisteet(df_tulokset, event_names, max_events=8)

    tiedostonimi = f"FGSMH_Sarjataulukko_{kisa_id}.xlsx"
    print(f"📁 Tallennetaan: {tiedostonimi}...")
    
    try:
        with pd.ExcelWriter(tiedostonimi, engine='openpyxl') as writer:
            df_sarjataulukko.to_excel(writer, sheet_name='Sarjapisteet', index=False)
            df_tulokset.to_excel(writer, sheet_name='Heitetyt_Tulokset', index=False)
        
        print(f"\n✅ VALMIS!")
        
        # Tulostetaan tekstimuotoinen kooste terminaaliin
        print(f"\nSARJATAULUKKO: {kisan_nimi}")
        print("-" * 65)
        print(f"{'SIJA':<6} {'PELAAJA':<25} {'KISAT':<8} {'PISTEET':<10}")
        print("-" * 65)
        
        # Tulostetaan Top 30 (tai kaikki jos vähemmän)
        for _, row in df_sarjataulukko.head(30).iterrows():
            print(f"{row['Sarjasijoitus']:<6} {row['Nimi']:<25} {int(row['Osallistumiset_yht']):<8} {row['Kokonaispisteet']:<10.0f}")
        
        if len(df_sarjataulukko) > 30:
            print(f"...ja {len(df_sarjataulukko)-30} muuta pelaajaa.")
        print("-" * 65)
        
    except Exception as e:
        print(f"❌ Virhe tallennuksessa: {e}")

if __name__ == "__main__":
    main()