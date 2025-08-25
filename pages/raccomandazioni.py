# pages/raccomandazioni.py
import streamlit as st

st.title("Raccomandazioni per l’utilizzo dei metodi")

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

Per il fattore di correzione, tenere conto solo degli indumenti e delle copeerture a livello delle porzioni basse del tronco.
Il sistema che suggerisce il fattore di correzione è ispirato agli studi di Henssge e alle tabelle realizzate da Wolf Schweitzer, MD, Institute of Legal Medicine, University of Zuerich, Switzerland, ma è da considerarsi del tutto indicativo. Si consiglia di tilizzare varie combinazioni e un range di fattori. 
"""
)

st.markdown(
    """
    <div style="
        text-align:left;
        font-size:x-small;
        color:#1e90ff;
        margin-top:30px;
    ">
    ⬅️ <a href="/" target="_self" style="color:#1e90ff; text-decoration:none;">
    Torna alla pagina principale</a>
    </div>
    """,
    unsafe_allow_html=True
)

