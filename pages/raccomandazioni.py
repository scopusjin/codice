# pages/raccomandazioni.py
import streamlit as st

st.title("Raccomandazioni")

st.markdown(
"""
**Il metodo di Henssge non può essere applicato nelle seguenti circostanze:**
- Non è possibile stabilire che il luogo di rinvenimento del corpo coincida con il luogo del decesso.  
- Presenza di una fonte di calore nelle immediate vicinanze del corpo.  
- Presenza di riscaldamento a pavimento sotto il corpo.  
- Ipotermia accertata o sospetta (temperatura corporea iniziale inferiore a 35 °C).  
- Impossibilità di determinare la temperatura ambientale media.  
- Impossibilità di stimare il fattore correttivo di Henssge.  
- Aumento significativo della temperatura ambientale (da valori bassi a elevati).  

Per il fattore di correzione, tenere conto solo degli indumenti e delle coperture a livello delle porzioni caudali del tronco del cadavere.
Il sistema che suggerisce il fattore di correzione è ispirato agli studi di Henssge e alle tabelle realizzate da Wolf Schweitzer, MD (Istituto di medicina legale, Università di Zurigo), ma è da considerarsi del tutto indicativo. Si consiglia di utilizzare varie combinazioni e un range di fattori. 
"""
)

import streamlit as st

# ... codice della pagina secondaria ...

# --- link di ritorno alla home ---
if st.button("⬅️ Torna alla pagina principale"):
    st.switch_page("app.py")

