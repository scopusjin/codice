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

INF_HOURS = 200  # usato per “infinito” sui range aperti


# --- Macchie ipostatiche ---
opzioni_macchie = {
    "Non valutate": None,
    "Non ancora comparse": (0, 3),
    "In via di confluenza": (1, 4),
    "Completamente migrabili": (0, 6),
    "Parzialmente migrabili": (4, 24),
    "Migrabili perlomeno parzialmente": (0, 24),
    "Fisse": (10, INF_HOURS),
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

testi_macchie = {
    "Non valutate": (
        "Le macchie ipostatiche non sono state valutate."
    ),
    "Non ancora comparse": (
        "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, "
        "non fossero ancora comparse. Secondo i limiti minimi e massimi segnalati in letteratura scientifica, questo indica "
        "che sono trascorse meno di 3 ore dal decesso (generalmente compaiono entro 15-20 minuti)."
    ),
    "In via di confluenza": (
        "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, fossero comparse ma ancora in via di confluenza. "
        "Secondo i limiti minimi e massimi segnalati in letteratura scientifica, questo indica che fossero trascorse più di 1 ora ma meno di 4 ore "
        "dal decesso (generalmente tale fase si verifica tra 1 ora 30 minuti e 3 ore 30 minuti)."
    ),
    "Completamente migrabili": (
        "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, "
        "si trovassero in una fase di migrabilità totale. Secondo i limiti minimi e massimi segnalati in letteratura scientifica, questo indica "
        "che fossero trascorse meno di 6 ore dal decesso. "
        "Generalmente le ipostasi compaiono dopo 20 minuti dal decesso."
    ),
    "Parzialmente migrabili": (
        "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, "
        "si trovassero in una fase di migrabilità parziale. Secondo i limiti minimi e massimi segnalati in letteratura scientifica, questo indica "
        "che fossero trascorse tra le 4 ore e le 24 ore dal decesso."
    ),
    "Migrabili perlomeno parzialmente": (
        "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, si trovassero "
        "in una fase di migrabilità perlomeno parziale (modificando la posizione del cadavere si sono "
        "modificate le macchie ipostatiche, ma, per le modalità e le tempistiche di esecuzione "
        "dell’ispezione legale, non è stato possibile dettagliare l’entità del fenomeno). "
        "Sulla base di tali caratteristiche e dei limiti massimi e minimi indicati in letteratura scientifica, questo indica che fossero trascorse "
        "meno di 24 ore dal decesso."
    ),
    "Fisse": (
        "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, si trovassero "
        "in una fase di fissità assoluta. Secondo i limiti minimi e massimi segnalati in letteratura scientifica, questo indica "
        "che fossero trascorse più di 10 ore dal decesso (fino a 30 ore le macchie possono non "
        "modificare la loro posizione alla movimentazione del corpo, ma la loro intensità può affievolirsi)."
    ),
    "Non valutabili/Non attendibili": (
        "Le macchie ipostatiche non sono state valutate o i rilievi non sono considerati attendibili "
        "per la stima dell'epoca della morte."
    ),
}



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
rigidita_descrizioni = {
    "Non valutata": (
        "La rigidità cadaverica non è stata valutata."
    ),
    "Non ancora apprezzabile": (
        "È possibile valutare che la rigidità cadaverica, al momento dell’ispezione legale, non fosse ancora comparsa. "
        "Secondo i limiti massimi segnalati in letteratura scientifica, questo indica che fossero trascorse meno di 7 ore "
        "dal decesso (in genere la rigidità compare entro 2 - 3 ore dal decesso)."
    ),
    "Presente e in via di intensificazione e generalizzazione": (
        "È possibile valutare che la rigidità cadaverica, al momento dell’ispezione legale, fosse in via di formazione, "
        "intensificazione e generalizzazione. Secondo i limiti minimi e massimi segnalati in letteratura scientifica, questo indica che "
        "fossero trascorsi almeno 30 minuti dal decesso ma meno di 20 ore da esso (generalmente la formazione della rigidità "
        "si completa in 6-10 ore)."
    ),
    "Presente, intensa e generalizzata": (
        "È possibile valutare che la rigidità cadaverica, al momento dell’ispezione legale, fosse presente e generalizzata. "
        "Secondo i limiti minimi e massimi segnalati in letteratura scientifica, questo indica che fossero trascorse almeno 2 ore "
        "dal decesso ma meno di 96 ore da esso, cioè meno di 4 giorni (in genere la rigidità inizia a risolversi dopo 57 ore dal decesso,  cioè dopo 2 giorni e mezzo)."
    ),
    "In via di risoluzione": (
        "È possibile valutare che la rigidità cadaverica, al momento dell’ispezione legale, fosse in via di risoluzione. "
        "Secondo i limiti minimi e massimi segnalati in letteratura scientifica, questo indica che fossero trascorse almeno 24 ore "
        "dal decesso ma meno di 192 ore da esso, cioè meno di 8 giorni (in genere la rigidità cadaverica inizia a risolversi "
        "dopo 57 ore dal decesso, cioè dopo 2 giorni e mezzo, e scompare entro 76 ore dal decesso, cioè dopo poco più  di 3 giorni)."
    ),
    "Risolta": (
        "È possibile valutare che la rigidità cadaverica, al momento dell’ispezione legale, fosse ormai risolta. "
        "Secondo i limiti minimi e massimi segnalati in letteratura scientifica, questo indica che fossero trascorse almeno 24 ore "
        "dal decesso (in genere la rigidità scompare entro 76 ore dal decesso, cioè dopo poco più  di 3 giorni)."
    ),
    "Non valutabile/Non attendibile": (
        "La rigidità cadaverica non è stata valutata o i rilievi non sono considerati attendibili "
        "per la stima dell'epoca della morte."
    ),
}

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
        "descrizioni": {
            "Fase VI": (
                "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione "
                "generalizzata dei muscoli della fronte, dell’orbita, della guancia. Tale reazione di eccitabilità "
                "muscolare elettrica residua suggerisce che il decesso fosse avvenuto tra 1 e 6 ore prima delle valutazioni "
                "del dato tanatologico."
            ),
            "Fase V": (
                "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione generalizzata "
                "dei muscoli della fronte e dell’orbita. Tale reazione di eccitabilità muscolare elettrica residua  suggerisce "
                "che il decesso fosse avvenuto tra le 2 e le 7 ore prima delle valutazioni del dato tanatologico."
            ),
            "Fase IV": (
                "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione generalizzata "
                "dei muscoli orbicolari (superiori e inferiori). Tale reazione di eccitabilità muscolare elettrica residua  "
                "suggerisce che il decesso fosse avvenuto tra le 3 e le 8 ore prima delle valutazioni del dato tanatologico."
            ),
            "Fase III": (
                "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione dei muscoli "
                "dell’intera palpebra superiore. Tale reazione di eccitabilità muscolare elettrica residua  suggerisce che il "
                "decesso fosse avvenuto tra le 3 ore e 30 minuti e le 13 ore prima delle valutazioni del dato tanatologico."
            ),
            "Fase II": (
                "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione dei muscoli di meno di "
                "2/3 della palpebra superiore. Tale reazione di eccitabilità muscolare elettrica residua  suggerisce che il decesso "
                "fosse avvenuto tra le 5 e le 16 ore prima delle valutazioni del dato tanatologico."
            ),
            "Fase I": (
                "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione accennata di una minima "
                "porzione della palpebra superiore (meno di 1/3). Tale reazione di eccitabilità muscolare elettrica residua suggerisce "
                "che il decesso fosse avvenuto tra le 5 e le 22 ore prima delle valutazioni del dato tanatologico."
            ),
            "Non valutabile/non attendibile": (
                "Non è stato possibile valutare l'eccitabilità muscolare elettrica residua sopraciliare o il suo rilievo "
                "non è da considerarsi attendibile."
            ),
            "Nessuna reazione": (
                "L’applicazione di uno stimolo elettrico in regione sopraciliare non ha prodotto contrazioni muscolari. Tale risultato "
                "permette solamente di stimare che, al momento della valutazione del dato tanatologico, fossero trascorse più di 5 ore dal decesso"
            ),
        },
    },

    "Eccitabilità elettrica peribuccale": {
        "opzioni": [
            "Non valutata", "Marcata ed estesa (+++)", "Discreta (++)",
            "Accennata (+)", "Nessuna reazione", "Non valutabile/non attendibile"
        ],
        "range": {
            "Non valutata": None,
            "Nessuna reazione": (6, INF_HOURS),
            "Non valutabile/non attendibile": None,
            "Marcata ed estesa (+++)": (0, 2.5),
            "Discreta (++)": (1, 5),
            "Accennata (+)": (2, 6),
        },
        "descrizioni": {
            "Marcata ed estesa (+++)": (
                "L’applicazione di uno stimolo elettrico in regione peribuccale ha prodotto una contrazione marcata ai muscoli "
                "peribuccali e ai muscoli facciali. Tale reazione di eccitabilità muscolare elettrica residua suggerisce che il "
                "decesso fosse avvenuto meno di 2 ore e mezzo prima delle valutazioni del dato tanatologico."
            ),
            "Discreta (++)": (
                "L’applicazione di uno stimolo elettrico in regione peribuccale ha prodotto una contrazione discreta ai muscoli "
                "peribuccali. Tale reazione di eccitabilità muscolare elettrica residua suggerisce che il decesso fosse avvenuto "
                "tra 1 e 5 ore prima delle valutazioni del dato tanatologico."
            ),
            "Accennata (+)": (
                "L’applicazione di uno stimolo elettrico in regione peribuccale ha prodotto una contrazione solo accennata dei muscoli "
                "peribuccali. Tale reazione di eccitabilità muscolare elettrica residua suggerisce che il decesso fosse avvenuto tra le 2 "
                "e le 6 ore prima delle valutazioni del dato tanatologico."
            ),
            "Non valutabile/non attendibile": (
                "Non è stato possibile valutare l'eccitabilità muscolare elettrica residua peribuccale o i rilievi non sono attendibili "
                "per la stima dell'epoca della morte."
            ),
            "Nessuna reazione": (
                "L’applicazione di uno stimolo elettrico in regione peribuccale non ha prodotto contrazioni muscolari. Tale risultato "
                "permette solamente di stimare che, al momento della valutazione del dato tanatologico, fossero trascorse più di 6 ore dal decesso."
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
        "descrizioni": {
            "Formazione di una piccola tumefazione persistente": (
                "L’eccitabilità muscolare meccanica residua, nel momento dell’ispezione legale, era caratterizzata dalla formazione "
                "di una piccola tumefazione persistente del muscolo bicipite del braccio, in risposta alla percussione. Tale reazione "
                "suggerisce che il decesso fosse avvenuto meno di 12 ore prima delle valutazioni del dato tanatologico."
            ),
            "Formazione di una tumefazione reversibile": (
                "L’eccitabilità muscolare meccanica residua, nel momento dell’ispezione legale, era caratterizzata dalla formazione "
                "di una tumefazione reversibile del muscolo bicipite del braccio, in risposta alla percussione. Tale reazione suggerisce "
                "che il decesso fosse avvenuto tra le 2 e le 5 ore prima delle valutazioni del dato tanatologico."
            ),
            "Contrazione reversibile dell’intero muscolo": (
                "L’eccitabilità muscolare meccanica residua, nel momento dell’ispezione legale, era caratterizzata dalla contrazione "
                "reversibile dell’intero muscolo bicipite del braccio, in risposta alla percussione. Tale reazione suggerisce che il decesso "
                "fosse avvenuto meno di 2 ore prima delle valutazioni del dato tanatologico."
            ),
            "Non valutabile/non attendibile": (
                "Non è stato possibile valutare l'eccitabilità muscolare meccanica o i rilievi non sono attendibili per la stima "
                "dell'epoca della morte."
            ),
            "Nessuna reazione": (
                "L’applicazione di uno stimolo meccanico al muscolo del braccio non ha prodotto contrazioni muscolari evidenti. "
                "Tale risultato permette solamente di stimare che, al momento della valutazione del dato tanatologico, fossero trascorse "
                "più di 1 ora e 30 minuti dal decesso."
            ),
        },
    },

    "Eccitabilità chimica pupillare": {
        "opzioni": ["Non valutata", "Non valutabile/non attendibile", "Positiva", "Negativa"],
        "range": {
            "Non valutata": None,
            "Non valutabile/non attendibile": None,
            "Positiva": (0, 30),
            "Negativa": (5, INF_HOURS),
        },
        "descrizioni": {
            "Positiva": (
                "L’eccitabilità pupillare chimica residua, nel momento dell’ispezione legale, era caratterizzata da una risposta dei muscoli "
                "pupillari dell’occhio (con aumento del diametro della pupilla) all’instillazione intraoculare di atropina. Tale reazione "
                "suggerisce che il decesso fosse avvenuto meno di 30 ore prima delle valutazioni medico legali."
            ),
            "Negativa": (
                "L’eccitabilità pupillare chimica residua, nel momento dell’ispezione legale, era caratterizzata da una assenza di risposta "
                "dei muscoli pupillari dell’occhio (con aumento del diametro della pupilla) all'instillazione intraoculare di atropina. "
                "Tale reazione suggerisce che il decesso fosse avvenuto più di 5 ore prima delle valutazioni medico legali."
            ),
            "Non valutabile/non attendibile": (
                "L'eccitabilità chimica pupillare non era valutabile o i rilievi non sono considerabili attendibili per la stima dell'epoca della morte."
            ),
        },
    },
}

# --- Nomi brevi per etichette nel grafico ---
nomi_brevi = {
    "Macchie ipostatiche": "Ipostasi",
    "Rigidità cadaverica": "Rigor",
    "Raffreddamento cadaverico": "Raffreddamento",
    "Eccitabilità elettrica peribuccale": "Ecc. elettrica peribuccale",
    "Eccitabilità elettrica sopraciliare": "Ecc. elettrica sopraciliare",
    "Eccitabilità chimica pupillare": "Ecc. pupillare",
    "Eccitabilità muscolare meccanica": "Ecc. meccanica",
}

__all__ = [
    "INF_HOURS",
    "opzioni_macchie", "macchie_medi", "testi_macchie",
    "opzioni_rigidita", "rigidita_medi", "rigidita_descrizioni",
    "dati_parametri_aggiuntivi", "nomi_brevi",
]
