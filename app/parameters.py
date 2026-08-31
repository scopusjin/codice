# app/parameters.py
# -*- coding: utf-8 -*-
"""
Dizionari statici per:
- macchie ipostatiche
- rigidità cadaverica
- parametri tanatologici aggiuntivi
- nomi brevi per etichette grafiche
- costante INF_HOURS condivisa
"""

from app.tanatology_texts_it import (
    TESTI_MACCHIE_LEGACY,
    RIGIDITA_DESCRIZIONI_LEGACY,
    SPECIAL_DESCRIPTIONS_LEGACY_BY_PARAM_LABEL,
    NOMI_BREVI_LEGACY,
)

INF_HOURS = 200  # usato per “infinito” sui range aperti


# --- Macchie ipostatiche ---
opzioni_macchie = {
    "Non valutate": None,
    "Non ancora comparse": (0, 3),
    "In via di confluenza": (1, 4),
    "Completamente migrabili": (0, 6),
    "Parzialmente migrabili": (4, 24),
    "Migrabili perlomeno parzialmente": (0, 24),
    "Fisse": (4, INF_HOURS),
    "Non valutabili/Non attendibili": None,
}

macchie_medi = {
    "Non valutate": None,
    "Non ancora comparse": (0, 0.33),
    "In via di confluenza": (1.5, 3.5),
    "Completamente migrabili": (0.33, 6),
    "Parzialmente migrabili": (6, 12),
    "Migrabili perlomeno parzialmente": None,
    "Fisse": (12, INF_HOURS),
    "Non valutabili/Non attendibili": None,
}

testi_macchie = dict(TESTI_MACCHIE_LEGACY)


# --- Rigidità cadaverica ---
opzioni_rigidita = {
    "Non valutata": None,  # default
    "Non ancora apprezzabile": (0, 7),  # rinomina di "Non ancora comparsa"
    "Presente e in via di intensificazione e generalizzazione": (0.5, 20),  # rinomina
    "Presente, intensa e generalizzata": (2, 96),  # rinomina
    "In via di risoluzione": (24, 192),
    "Risolta": (24, INF_HOURS),  # rinomina di "Ormai risolta"
    "Non valutabile/Non attendibile": None,
}
rigidita_medi = {
    "Non valutata": None,
    "Non ancora apprezzabile": (0, 3),
    "Presente e in via di intensificazione e generalizzazione": (2, 10),
    "Presente, intensa e generalizzata": (10, 85),
    "In via di risoluzione": (29, 140),
    "Risolta": (76, INF_HOURS),
}
rigidita_descrizioni = dict(RIGIDITA_DESCRIZIONI_LEGACY)


# --- Parametri tanatologici aggiuntivi ---
dati_parametri_aggiuntivi = {
    "Eccitabilità elettrica sopraciliare": {
        "opzioni": [
            "Non valutata", "Fase I", "Fase II", "Fase III", "Fase IV", "Fase V", "Fase VI",
            "Nessuna reazione", "Non valutabile/non attendibile"
        ],
        "range": {
            "Non valutata": None,
            "Nessuna reazione": (5, INF_HOURS),
            "Non valutabile/non attendibile": None,
            "Fase VI": (1, 6),
            "Fase V": (2, 7),
            "Fase IV": (3, 8),
            "Fase III": (3.5, 13),
            "Fase II": (5, 16),
            "Fase I": (5, 22),
        },
        "descrizioni": dict(
            SPECIAL_DESCRIPTIONS_LEGACY_BY_PARAM_LABEL["Eccitabilità elettrica sopraciliare"]
        ),
    },

    "Eccitabilità elettrica peribuccale": {
        "opzioni": [
            "Non valutata", "Muscoli facciali (+++)", "Muscoli peribuccali (++)",
            "Reazione focale (+)", "Nessuna reazione", "Non valutabile/non attendibile"
        ],
        "range": {
            "Non valutata": None,
            "Nessuna reazione": (3, INF_HOURS),
            "Non valutabile/non attendibile": None,
            "Muscoli facciali (+++)": (0, 11),
            "Muscoli peribuccali (++)": (0, 11),
            "Reazione focale (+)": (0, 11),
        },
        "descrizioni": {
            "Muscoli facciali (+++)": (
                "L’applicazione di uno stimolo elettrico in regione peribuccale ha prodotto una contrazione "
                "generalizzata della muscolatura facciale. Tale reazione di eccitabilità muscolare elettrica residua "
                "suggerisce che il decesso fosse avvenuto non oltre 11 ore prima della valutazione del dato tanatologico "
                "(secondo un metodo meno recente, una simile reazione si osserva indicativamente entro circa 2 ore e "
                "30 minuti dal decesso)."
            ),
            "Muscoli peribuccali (++)": (
                "L’applicazione di uno stimolo elettrico in regione peribuccale ha prodotto una contrazione limitata "
                "alla muscolatura peribuccale. Tale reazione di eccitabilità muscolare elettrica residua suggerisce che "
                "il decesso fosse avvenuto non oltre 11 ore prima della valutazione del dato tanatologico (secondo un "
                "metodo meno recente, una simile reazione si osserva indicativamente tra 1 e 5 ore dal decesso)."
            ),
            "Reazione focale (+)": (
                "L’applicazione di uno stimolo elettrico in regione peribuccale ha prodotto una reazione focale in "
                "prossimità degli elettrodi. Tale reazione di eccitabilità muscolare elettrica residua suggerisce che il "
                "decesso fosse avvenuto non oltre 11 ore prima della valutazione del dato tanatologico (secondo un metodo "
                "meno recente, una simile reazione si osserva indicativamente tra 2 e 6 ore dal decesso)."
            ),
            "Nessuna reazione": (
                "L’applicazione di uno stimolo elettrico in regione peribuccale non ha prodotto contrazioni muscolari "
                "apprezzabili. L’assenza di eccitabilità muscolare elettrica residua suggerisce che fossero trascorse "
                "almeno 3 ore dal decesso al momento della valutazione del dato tanatologico."
            ),
            "Non valutabile/non attendibile": (
                "Non è stato possibile valutare l'eccitabilità muscolare elettrica residua peribuccale o i rilievi non "
                "sono attendibili per la stima dell'epoca della morte."
            ),
        },
    },

    "Eccitabilità muscolare meccanica": {
        "opzioni": [
            "Non valutata",
            "Contrazione reversibile dell’intero muscolo",
            "Formazione di una tumefazione reversibile",
            "Formazione di una piccola tumefazione persistente",
            "Nessuna reazione",
            "Non valutabile/non attendibile",
        ],
        "range": {
            "Non valutata": None,
            "Nessuna reazione": (1.5, INF_HOURS),
            "Non valutabile/non attendibile": None,
            "Formazione di una piccola tumefazione persistente": (0, 12),
            "Formazione di una tumefazione reversibile": (2, 5),
            "Contrazione reversibile dell’intero muscolo": (0, 2),
        },
        "descrizioni": dict(
            SPECIAL_DESCRIPTIONS_LEGACY_BY_PARAM_LABEL["Eccitabilità muscolare meccanica"]
        ),
    },

    "Eccitabilità chimica pupillare": {
        "opzioni": [
            "Non valutata",
            "Dilatazione con atropina",
            "Nessuna variazione con atropina",
            "Dilatazione con tropicamide",
            "Nessuna variazione con tropicamide",
            "Riduzione con acetilcolina",
            "Nessuna variazione con acetilcolina",
            "Non valutabile/non attendibile",
        ],
        "range": {
            "Non valutata": None,
            "Dilatazione con atropina": (0, 10),
            "Nessuna variazione con atropina": (3, INF_HOURS),
            "Dilatazione con tropicamide": (0, 30),
            "Nessuna variazione con tropicamide": (5, INF_HOURS),
            "Riduzione con acetilcolina": (0, 46),
            "Nessuna variazione con acetilcolina": (14, INF_HOURS),
            "Non valutabile/non attendibile": None,
        },
        "descrizioni": {
            "Dilatazione con atropina": (
                "L’instillazione di atropina ha determinato una dilatazione pupillare. "
                "La persistenza di tale eccitabilità chimica dell’iride suggerisce che il decesso fosse avvenuto "
                "meno di 10 ore prima della valutazione del dato tanatologico."
            ),
            "Nessuna variazione con atropina": (
                "L’instillazione di atropina non ha determinato variazioni apprezzabili del diametro pupillare. "
                "L’assenza di reazione suggerisce che fossero trascorse almeno 3 ore dal decesso al momento della "
                "valutazione del dato tanatologico."
            ),
            "Dilatazione con tropicamide": (
                "L’instillazione di tropicamide ha determinato una dilatazione pupillare. "
                "La persistenza di tale eccitabilità chimica dell’iride suggerisce che il decesso fosse avvenuto "
                "meno di 30 ore prima della valutazione del dato tanatologico."
            ),
            "Nessuna variazione con tropicamide": (
                "L’instillazione di tropicamide non ha determinato variazioni apprezzabili del diametro pupillare. "
                "L’assenza di reazione suggerisce che fossero trascorse almeno 5 ore dal decesso al momento della "
                "valutazione del dato tanatologico."
            ),
            "Riduzione con acetilcolina": (
                "L’instillazione di acetilcolina ha determinato una riduzione del diametro pupillare. "
                "La persistenza di tale eccitabilità chimica dell’iride suggerisce che il decesso fosse avvenuto "
                "meno di 46 ore prima della valutazione del dato tanatologico."
            ),
            "Nessuna variazione con acetilcolina": (
                "L’instillazione di acetilcolina non ha determinato variazioni apprezzabili del diametro pupillare. "
                "L’assenza di reazione suggerisce che fossero trascorse almeno 14 ore dal decesso al momento della "
                "valutazione del dato tanatologico."
            ),
        },
    },
}

# Range descrittivi del metodo Popwassilew–Palm: solo per il segmento verde del grafico.
# Non partecipano all'intersezione prudente, che usa i limiti Klein/Henssge sopra.
peribuccale_popwassilew_palm_ranges = {
    "Muscoli facciali (+++)": (0, 2.5),
    "Muscoli peribuccali (++)": (1, 5),
    "Reazione focale (+)": (2, 6),
}

# --- Nomi brevi per etichette nel grafico ---
nomi_brevi = dict(NOMI_BREVI_LEGACY)

__all__ = [
    "INF_HOURS",
    "opzioni_macchie", "macchie_medi", "testi_macchie",
    "opzioni_rigidita", "rigidita_medi", "rigidita_descrizioni",
    "dati_parametri_aggiuntivi", "peribuccale_popwassilew_palm_ranges", "nomi_brevi",
]
