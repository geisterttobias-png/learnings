import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Instandhaltung Pro", page_icon="🏭", layout="wide")

st.title("🏭 Smart Maintenance Dashboard")

# --- DATEN LADEN & VORBEREITEN ---
try:
    df = pd.read_csv("stoerungen.csv", names=["Zeit", "Maschine", "Priorität", "Melder", "Problem"])
except FileNotFoundError:
    df = pd.DataFrame(columns=["Zeit", "Maschine", "Priorität", "Melder", "Problem"])

# --- DASHBOARD KOPFZEILE (KPIs) ---
# Wir berechnen hier die wichtigen Kennzahlen
total_tickets = len(df)
# Wir filtern: Wie viele Zeilen haben "HOCH" als Priorität?
kritische_tickets = len(df[df["Priorität"] == "HOCH 🔥"])
# Wir zählen, wie viele verschiedene Maschinen betroffen sind
betroffene_maschinen = df["Maschine"].nunique()

st.header("Überblick")
col1, col2, col3 = st.columns(3)

# st.metric zeigt große, schicke Zahlen an
col1.metric("Gesamt Tickets", total_tickets)
col2.metric("Kritische Tickets", kritische_tickets, delta_color="inverse")
col3.metric("Betroffene Anlagen", betroffene_maschinen)

st.divider() # Ein visueller Trennstrich

# --- HAUPTBEREICH ---
tab1, tab2, tab3 = st.tabs(["📝 Neue Meldung", "📋 Live-Monitor", "📊 Deep Dive Analyse"])

# TAB 1: EINGABE (Fast wie vorher)
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        maschine = st.selectbox("Maschine", ["Hydraulikpresse A", "Schweißroboter B", "Förderband 1", "Verpackung"])
        prio = st.selectbox("Priorität", ["Niedrig", "Mittel", "HOCH 🔥"])
    with c2:
        melder = st.text_input("Name")
        problem = st.text_area("Problem")

    if st.button("Speichern", type="primary"):
        zeit = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        with open("stoerungen.csv", "a") as f:
            f.write(f"{zeit},{maschine},{prio},{melder},{problem}\n")
        st.success("Gespeichert! Bitte Seite neu laden (R drücken) für Update.")

# TAB 2: MONITOR (Mit Farb-Highlighting)
with tab2:
    st.subheader("Aktuelle Tickets")
    
    if not df.empty:
        # DATA SCIENCE TRICK:
        # Wir definieren eine Funktion, die Zeilen rot färbt, wenn sie "HOCH" sind.
        def highlight_critical(row):
            if row["Priorität"] == "HOCH 🔥":
                return ['background-color: #ffcccc'] * len(row)
            else:
                return [''] * len(row)

        # Wir wenden den Style auf die Tabelle an
        st.dataframe(df.style.apply(highlight_critical, axis=1), use_container_width=True)
    else:
        st.info("Keine offenen Tickets.")

# TAB 3: GRAFIKEN
with tab3:
    if not df.empty:
        c1, c2 = st.columns(2)
        
        with c1:
            st.caption("Verteilung nach Maschinen")
            st.bar_chart(df["Maschine"].value_counts())
            
        with c2:
            st.caption("Verteilung nach Priorität")
            # Ein Pie-Chart (Kreisdiagramm) wäre schön, Streamlit macht das standardmäßig als BarChart
            # Aber wir können die Daten einfach als Area Chart anzeigen für Abwechslung
            st.area_chart(df["Priorität"].value_counts())
