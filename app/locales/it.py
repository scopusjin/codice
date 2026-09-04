# -*- coding: utf-8 -*-
"""Testi tanatologici italiani indicizzati tramite ID stabili.

Questo modulo contiene esclusivamente contenuto testuale/presentazionale.
Range, soglie e criteri scientifici restano nei moduli dati esistenti.
Le viste legacy in fondo al file mantengono la compatibilità con il codice che
usa ancora le etichette italiane come chiavi.
"""

from __future__ import annotations

from app.tanatology_states import (
    LIVOR_NOT_ASSESSED,
    LIVOR_ABSENT,
    LIVOR_CONFLUING,
    LIVOR_FULLY_MIGRATABLE,
    LIVOR_PARTIALLY_MIGRATABLE,
    LIVOR_AT_LEAST_PARTIALLY_MIGRATABLE,
    LIVOR_FIXED,
    LIVOR_UNRELIABLE,
    RIGOR_NOT_ASSESSED,
    RIGOR_ABSENT,
    RIGOR_DEVELOPING,
    RIGOR_FULL,
    RIGOR_RESOLVING,
    RIGOR_RESOLVED,
    RIGOR_UNRELIABLE,
    LIVOR_LABEL_IT,
    RIGOR_LABEL_IT,
)
from app.special_tanatology_states import (
    PARAM_ELECTRICAL_SUPRACILIARY,
    PARAM_ELECTRICAL_PERIORAL,
    PARAM_MECHANICAL_MUSCLE,
    PARAM_CHEMICAL_PUPILLARY,
    OPTION_NOT_ASSESSED,
    OPTION_UNRELIABLE,
    OPTION_NO_REACTION,
    SUPRA_PHASE_I,
    SUPRA_PHASE_II,
    SUPRA_PHASE_III,
    SUPRA_PHASE_IV,
    SUPRA_PHASE_V,
    SUPRA_PHASE_VI,
    PERIORAL_MARKED,
    PERIORAL_MODERATE,
    PERIORAL_SLIGHT,
    MECH_WHOLE_MUSCLE,
    MECH_REVERSIBLE_SWELLING,
    MECH_SMALL_PERSISTENT_SWELLING,
    PUPILLARY_POSITIVE,
    PUPILLARY_NEGATIVE,
    SPECIAL_PARAM_LABEL_IT,
    SPECIAL_OPTION_LABEL_IT,
)


LIVOR_DESCRIPTION_IT_BY_ID = {
    LIVOR_NOT_ASSESSED: (
        "Le macchie ipostatiche non sono state valutate."
    ),
    LIVOR_ABSENT: (
        "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, "
        "non fossero ancora comparse. Secondo i limiti minimi e massimi segnalati in letteratura scientifica, questo indica "
        "che fossero trascorse meno di 3 ore dal decesso (generalmente compaiono entro 15-20 minuti)."
    ),
    LIVOR_CONFLUING: (
        "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, fossero comparse ma ancora in via di confluenza. "
        "Secondo i limiti minimi e massimi segnalati in letteratura scientifica, questo indica che fossero trascorse più di 1 ora ma meno di 4 ore "
        "dal decesso (generalmente tale fase si verifica tra 1 ora 30 minuti e 3 ore 30 minuti)."
    ),
    LIVOR_FULLY_MIGRATABLE: (
        "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, "
        "si trovassero in una fase di migrabilità totale. Secondo i limiti massimi segnalati in letteratura scientifica, questo indica "
        "che fossero trascorse meno di 6 ore dal decesso. "
        "Generalmente le ipostasi compaiono dopo 20 minuti dal decesso."
    ),
    LIVOR_PARTIALLY_MIGRATABLE: (
        "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, "
        "si trovassero in una fase di migrabilità parziale. Secondo i limiti minimi e massimi segnalati in letteratura scientifica, questo indica "
        "che fossero trascorse tra le 4 ore e le 24 ore dal decesso."
    ),
    LIVOR_AT_LEAST_PARTIALLY_MIGRATABLE: (
        "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, si trovassero "
        "in una fase di migrabilità perlomeno parziale (modificando la posizione del cadavere si sono "
        "modificate le macchie ipostatiche, ma, per le modalità e le tempistiche di esecuzione "
        "dell’ispezione legale, non è stato possibile dettagliare l’entità del fenomeno). "
        "Sulla base di tali caratteristiche e dei limiti massimi e minimi indicati in letteratura scientifica, questo indica che fossero trascorse "
        "meno di 24 ore dal decesso."
    ),
    LIVOR_FIXED: (
        "È da ritenersi che le macchie ipostatiche, al momento dell’ispezione legale, si trovassero "
        "in una fase di fissità assoluta. Secondo i limiti minimi segnalati in letteratura scientifica, questo indica "
        "che fossero trascorse più di 4 ore dal decesso (fino a 30 ore le macchie possono non "
        "modificare la loro posizione alla movimentazione del corpo, ma la loro intensità può affievolirsi)."
    ),
    LIVOR_UNRELIABLE: (
        "Le macchie ipostatiche non sono state valutate o i rilievi non sono considerati attendibili "
        "per la stima dell'epoca della morte."
    ),
}


RIGOR_DESCRIPTION_IT_BY_ID = {
    RIGOR_NOT_ASSESSED: (
        "La rigidità cadaverica non è stata valutata."
    ),
    RIGOR_ABSENT: (
        "È possibile valutare che la rigidità cadaverica, al momento dell’ispezione legale, non fosse ancora comparsa. "
        "Secondo i limiti massimi segnalati in letteratura scientifica, questo indica che fossero trascorse meno di 7 ore "
        "dal decesso (in genere la rigidità compare entro 2 - 3 ore dal decesso)."
    ),
    RIGOR_DEVELOPING: (
        "È possibile valutare che la rigidità cadaverica, al momento dell’ispezione legale, fosse in via di formazione, "
        "intensificazione e generalizzazione. Secondo i limiti minimi e massimi segnalati in letteratura scientifica, questo indica che "
        "fossero trascorsi almeno 30 minuti dal decesso ma meno di 20 ore da esso (generalmente la formazione della rigidità "
        "si completa in 6-10 ore)."
    ),
    RIGOR_FULL: (
        "È possibile valutare che la rigidità cadaverica, al momento dell’ispezione legale, fosse presente e generalizzata. "
        "Secondo i limiti minimi e massimi segnalati in letteratura scientifica, questo indica che fossero trascorse almeno 2 ore "
        "dal decesso ma meno di 96 ore da esso, cioè meno di 4 giorni (in genere la rigidità inizia a risolversi dopo 57 ore dal decesso, cioè dopo 2 giorni e mezzo)."
    ),
    RIGOR_RESOLVING: (
        "È possibile valutare che la rigidità cadaverica, al momento dell’ispezione legale, fosse in via di risoluzione. "
        "Secondo i limiti minimi e massimi segnalati in letteratura scientifica, questo indica che fossero trascorse almeno 24 ore "
        "dal decesso ma meno di 192 ore da esso, cioè meno di 8 giorni (in genere la rigidità cadaverica inizia a risolversi "
        "dopo 57 ore dal decesso, cioè dopo 2 giorni e mezzo, e scompare entro 76 ore dal decesso, cioè dopo poco più di 3 giorni)."
    ),
    RIGOR_RESOLVED: (
        "È possibile valutare che la rigidità cadaverica, al momento dell’ispezione legale, fosse ormai risolta. "
        "Secondo i limiti minimi e massimi segnalati in letteratura scientifica, questo indica che fossero trascorse almeno 24 ore "
        "dal decesso (in genere la rigidità scompare entro 76 ore dal decesso, cioè dopo poco più di 3 giorni)."
    ),
    RIGOR_UNRELIABLE: (
        "La rigidità cadaverica non è stata valutata o i rilievi non sono considerati attendibili "
        "per la stima dell'epoca della morte."
    ),
}


SPECIAL_DESCRIPTION_IT_BY_ID = {
    PARAM_ELECTRICAL_SUPRACILIARY: {
        OPTION_NOT_ASSESSED: None,
        SUPRA_PHASE_I: (
            "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione accennata di una minima "
            "porzione della palpebra superiore (meno di 1/3). Tale reazione di eccitabilità muscolare elettrica residua suggerisce "
            "che il decesso fosse avvenuto tra le 5 e le 22 ore prima della valutazione del dato tanatologico."
        ),
        SUPRA_PHASE_II: (
            "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione dei muscoli di meno di "
            "2/3 della palpebra superiore. Tale reazione di eccitabilità muscolare elettrica residua suggerisce che il decesso "
            "fosse avvenuto tra le 5 e le 16 ore prima della valutazione del dato tanatologico."
        ),
        SUPRA_PHASE_III: (
            "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione dei muscoli "
            "dell’intera palpebra superiore. Tale reazione di eccitabilità muscolare elettrica residua suggerisce che il "
            "decesso fosse avvenuto tra le 3 ore e 30 minuti e le 13 ore prima della valutazione del dato tanatologico."
        ),
        SUPRA_PHASE_IV: (
            "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione generalizzata "
            "dei muscoli orbicolari (superiori e inferiori). Tale reazione di eccitabilità muscolare elettrica residua "
            "suggerisce che il decesso fosse avvenuto tra le 3 e le 8 ore prima della valutazione del dato tanatologico."
        ),
        SUPRA_PHASE_V: (
            "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione generalizzata "
            "dei muscoli della fronte e dell’orbita. Tale reazione di eccitabilità muscolare elettrica residua suggerisce "
            "che il decesso fosse avvenuto tra le 2 e le 7 ore prima della valutazione del dato tanatologico."
        ),
        SUPRA_PHASE_VI: (
            "L’applicazione di uno stimolo elettrico in regione sopraciliare ha prodotto una contrazione "
            "generalizzata dei muscoli della fronte, dell’orbita, della guancia. Tale reazione di eccitabilità "
            "muscolare elettrica residua suggerisce che il decesso fosse avvenuto tra 1 e 6 ore prima della valutazione "
            "del dato tanatologico."
        ),
        OPTION_NO_REACTION: (
            "L’applicazione di uno stimolo elettrico in regione sopraciliare non ha prodotto contrazioni muscolari. Tale risultato "
            "consente soltanto di stimare che, al momento della valutazione del dato tanatologico, fossero trascorse più di 5 ore dal decesso."
        ),
        OPTION_UNRELIABLE: (
            "Non è stato possibile valutare l'eccitabilità muscolare elettrica residua sopraciliare o il suo rilievo "
            "non è da considerarsi attendibile."
        ),
    },
    PARAM_ELECTRICAL_PERIORAL: {
        OPTION_NOT_ASSESSED: None,
        PERIORAL_MARKED: (
            "L’applicazione di uno stimolo elettrico in regione peribuccale ha prodotto una contrazione marcata dei muscoli "
            "peribuccali e dei muscoli facciali. Tale reazione di eccitabilità muscolare elettrica residua suggerisce che il "
            "decesso fosse avvenuto meno di 2 ore e mezzo prima della valutazione del dato tanatologico."
        ),
        PERIORAL_MODERATE: (
            "L’applicazione di uno stimolo elettrico in regione peribuccale ha prodotto una contrazione discreta dei muscoli "
            "peribuccali. Tale reazione di eccitabilità muscolare elettrica residua suggerisce che il decesso fosse avvenuto "
            "tra 1 e 5 ore prima della valutazione del dato tanatologico."
        ),
        PERIORAL_SLIGHT: (
            "L’applicazione di uno stimolo elettrico in regione peribuccale ha prodotto una contrazione solo accennata dei muscoli "
            "peribuccali. Tale reazione di eccitabilità muscolare elettrica residua suggerisce che il decesso fosse avvenuto tra le 2 "
            "e le 6 ore prima della valutazione del dato tanatologico."
        ),
        OPTION_NO_REACTION: (
            "L’applicazione di uno stimolo elettrico in regione peribuccale non ha prodotto contrazioni muscolari. Tale risultato "
            "consente soltanto di stimare che, al momento della valutazione del dato tanatologico, fossero trascorse più di 3 ore dal decesso."
        ),
        OPTION_UNRELIABLE: (
            "Non è stato possibile valutare l'eccitabilità muscolare elettrica residua peribuccale o i rilievi non sono attendibili "
            "per la stima dell'epoca della morte."
        ),
    },
    PARAM_MECHANICAL_MUSCLE: {
        OPTION_NOT_ASSESSED: None,
        MECH_WHOLE_MUSCLE: (
            "L’eccitabilità muscolare meccanica residua, nel momento dell’ispezione legale, era caratterizzata dalla contrazione "
            "reversibile dell’intero muscolo bicipite del braccio, in risposta alla percussione. Tale reazione suggerisce che il decesso "
            "fosse avvenuto meno di 2 ore prima della valutazione del dato tanatologico."
        ),
        MECH_REVERSIBLE_SWELLING: (
            "L’eccitabilità muscolare meccanica residua, nel momento dell’ispezione legale, era caratterizzata dalla formazione "
            "di una tumefazione reversibile del muscolo bicipite del braccio, in risposta alla percussione. Tale reazione suggerisce "
            "che il decesso fosse avvenuto tra le 2 e le 5 ore prima della valutazione del dato tanatologico."
        ),
        MECH_SMALL_PERSISTENT_SWELLING: (
            "L’eccitabilità muscolare meccanica residua, nel momento dell’ispezione legale, era caratterizzata dalla formazione "
            "di una piccola tumefazione persistente del muscolo bicipite del braccio, in risposta alla percussione. Tale reazione "
            "suggerisce che il decesso fosse avvenuto meno di 12 ore prima della valutazione del dato tanatologico."
        ),
        OPTION_NO_REACTION: (
            "L’applicazione di uno stimolo meccanico al muscolo del braccio non ha prodotto contrazioni muscolari evidenti. "
            "Tale risultato consente soltanto di stimare che, al momento della valutazione del dato tanatologico, fossero trascorse "
            "più di 1 ora e 30 minuti dal decesso."
        ),
        OPTION_UNRELIABLE: (
            "Non è stato possibile valutare l'eccitabilità muscolare meccanica o i rilievi non sono attendibili per la stima "
            "dell'epoca della morte."
        ),
    },
    PARAM_CHEMICAL_PUPILLARY: {
        OPTION_NOT_ASSESSED: None,
        OPTION_UNRELIABLE: (
            "L'eccitabilità chimica pupillare non era valutabile o i rilievi non sono considerabili attendibili per la stima dell'epoca della morte."
        ),
        PUPILLARY_POSITIVE: (
            "L’eccitabilità pupillare chimica residua, nel momento dell’ispezione legale, era caratterizzata da una risposta dei muscoli "
            "pupillari dell’occhio (con aumento del diametro della pupilla) all’instillazione intraoculare di atropina. Tale reazione "
            "suggerisce che il decesso fosse avvenuto meno di 30 ore prima delle valutazioni medico legali."
        ),
        PUPILLARY_NEGATIVE: (
            "L’eccitabilità pupillare chimica residua, nel momento dell’ispezione legale, era caratterizzata da una assenza di risposta "
            "dei muscoli pupillari dell’occhio (senza aumento del diametro della pupilla) all'instillazione intraoculare di atropina. "
            "Tale reazione suggerisce che il decesso fosse avvenuto più di 5 ore prima delle valutazioni medico legali."
        ),
    },
}


NOMI_BREVI_LEGACY = {
    "Macchie ipostatiche": "Ipostasi",
    "Rigidità cadaverica": "Rigor",
    "Raffreddamento cadaverico": "Raffreddamento",
    "Eccitabilità elettrica peribuccale": "Ecc. elettrica peribuccale",
    "Eccitabilità elettrica sopraciliare": "Ecc. elettrica sopraciliare",
    "Eccitabilità chimica pupillare": "Ecc. pupillare",
    "Eccitabilità muscolare meccanica": "Ecc. meccanica",
}

SPECIAL_GRAPH_LABEL_IT_BY_ID = {
    param_id: NOMI_BREVI_LEGACY.get(param_label, param_label)
    for param_id, param_label in SPECIAL_PARAM_LABEL_IT.items()
}


TESTI_MACCHIE_LEGACY = {
    LIVOR_LABEL_IT[state_id]: description
    for state_id, description in LIVOR_DESCRIPTION_IT_BY_ID.items()
}

RIGIDITA_DESCRIZIONI_LEGACY = {
    RIGOR_LABEL_IT[state_id]: description
    for state_id, description in RIGOR_DESCRIPTION_IT_BY_ID.items()
}

SPECIAL_DESCRIPTIONS_LEGACY_BY_PARAM_LABEL = {
    SPECIAL_PARAM_LABEL_IT[param_id]: {
        SPECIAL_OPTION_LABEL_IT[param_id][option_id]: description
        for option_id, description in descriptions.items()
        if description is not None
    }
    for param_id, descriptions in SPECIAL_DESCRIPTION_IT_BY_ID.items()
}


def livor_description_it(state_id: str):
    return LIVOR_DESCRIPTION_IT_BY_ID.get(state_id)


def rigor_description_it(state_id: str):
    return RIGOR_DESCRIPTION_IT_BY_ID.get(state_id)


def livor_description_from_legacy_it(legacy_label: str):
    for state_id, label in LIVOR_LABEL_IT.items():
        if label == legacy_label:
            return LIVOR_DESCRIPTION_IT_BY_ID.get(state_id)
    return None


def rigor_description_from_legacy_it(legacy_label: str):
    for state_id, label in RIGOR_LABEL_IT.items():
        if label == legacy_label:
            return RIGOR_DESCRIPTION_IT_BY_ID.get(state_id)
    return None


def special_description_it(param_id: str, option_id: str):
    return SPECIAL_DESCRIPTION_IT_BY_ID[param_id].get(option_id)


def special_graph_label_it(param_id: str):
    return SPECIAL_GRAPH_LABEL_IT_BY_ID[param_id]


def format_hours_minutes(h: int, m: int) -> str:
    """Formattazione italiana legacy di ore e minuti."""
    if h > 0 and m > 0:
        return f"{h} {'ora' if h == 1 else 'ore'} {m} {'minuto' if m == 1 else 'minuti'}"
    if h > 0:
        return f"{h} {'ora' if h == 1 else 'ore'}"
    if m > 0:
        return f"{m} {'minuto' if m == 1 else 'minuti'}"
    return "0 minuti"


def format_hours_range(h1: int, m1: int, h2: int, m2: int) -> str:
    """Formattazione italiana legacy degli intervalli temporali."""
    if h1 > 0 and h2 > 0 and m1 == 0:
        unit2 = "ora" if h2 == 1 else "ore"
        if m2 == 0:
            return f"tra {h1} e {h2} {unit2}"
        unit1 = "ora" if h1 == 1 else "ore"
        return f"tra {h1} {unit1} e {h2} {unit2} {m2} minuti"
    return f"tra {format_hours_minutes(h1, m1)} e {format_hours_minutes(h2, m2)}"


def simple_sentence_no_dt_not_over(duration: str) -> str:
    return (
        "<p><b>EPOCA DEL DECESSO STIMATA</b>: "
        f"<b>non oltre {duration} prima</b> "
        "dei rilievi effettuati nel corso dell’ispezione legale.</p>"
    )


def simple_sentence_no_dt_over(duration: str) -> str:
    return (
        "<p><b>EPOCA DEL DECESSO STIMATA</b>: "
        f"<b>oltre {duration} prima</b> "
        "dei rilievi effettuati nel corso dell’ispezione legale.</p>"
    )


def simple_sentence_no_dt_range(interval: str) -> str:
    return (
        "<p><b>EPOCA DEL DECESSO STIMATA</b>: "
        f"<b>{interval} prima</b> "
        "dei rilievi effettuati nel corso dell’ispezione legale.</p>"
    )


def final_sentence_simple_over(duration: str) -> str:
    return (
        "<p><b>EPOCA DEL DECESSO STIMATA</b>: "
        "La valutazione complessiva dei dati tanatologici, integrando i loro limiti temporali, "
        f"consente di stimare che la morte sia avvenuta all'incirca <b>oltre {duration} prima</b> "
        "dei rilievi effettuati nel corso dell’ispezione legale.</p>"
    )


def final_sentence_simple_not_over(duration: str) -> str:
    return (
        "<p><b>EPOCA DEL DECESSO STIMATA</b>: "
        "La valutazione complessiva dei dati tanatologici, integrando i loro limiti temporali, "
        f"consente di stimare che la morte sia avvenuta all'incirca <b>non oltre {duration} prima</b> "
        "dei rilievi effettuati nel corso dell’ispezione legale.</p>"
    )


def final_sentence_simple_range(interval: str) -> str:
    return (
        "<p><b>EPOCA DEL DECESSO STIMATA</b>: "
        "La valutazione complessiva dei dati tanatologici, integrando i loro limiti temporali, "
        f"consente di stimare che la morte sia avvenuta all'incirca <b>{interval} prima</b> "
        "dei rilievi effettuati nel corso dell’ispezione legale.</p>"
    )


def simple_sentence_dt_not_over(
    duration: str,
    lower_time: str,
    lower_date: str,
    inspection_time: str,
    inspection_date: str,
) -> str:
    if lower_date == inspection_date:
        window = f"tra le ore {lower_time} e le {inspection_time} del {lower_date}"
    else:
        window = f"tra le ore {lower_time} del {lower_date} e le {inspection_time} del {inspection_date}"
    return (
        "<p>EPOCA DEL DECESSO STIMATA: "
        f"non oltre {duration} prima "
        "dei rilievi effettuati nel corso dell’ispezione legale, "
        f"vale a dire all'incirca {window}.</p>"
    )


def simple_sentence_dt_over(duration: str, cutoff_time: str, cutoff_date: str) -> str:
    return (
        "<p><b>EPOCA DEL DECESSO STIMATA</b>: "
        f"<b>oltre {duration} prima</b> "
        "dei rilievi effettuati nel corso dell’ispezione legale, "
        f"vale a dire <b>prima delle ore {cutoff_time} del {cutoff_date}</b>.</p>"
    )


def simple_sentence_dt_range(
    interval: str,
    start_time: str,
    start_date: str,
    end_time: str,
    end_date: str,
    same_date: bool,
) -> str:
    if same_date:
        window = f"tra le ore {start_time} e le ore {end_time} del {start_date}"
    else:
        window = f"tra le ore {start_time} del {start_date} e le ore {end_time} del {end_date}"
    return (
        "<p><b>EPOCA DEL DECESSO STIMATA</b>: "
        f"<b>{interval} prima</b> "
        "dei rilievi effettuati nel corso dell’ispezione legale, "
        f"vale a dire circa <b>{window}</b>.</p>"
    )


def final_sentence_dt_over(duration: str, cutoff_time: str, cutoff_date: str) -> str:
    return (
        "<p>La valutazione complessiva dei dati tanatologici consente di stimare che la morte sia avvenuta all'incirca "
        f"<b>oltre {duration} prima</b> "
        "dei rilievi effettuati nel corso dell’ispezione legale, "
        f"vale a dire <b>prima delle ore {cutoff_time} del {cutoff_date}</b>.</p>"
    )


def final_sentence_dt_not_over(
    duration: str,
    lower_time: str,
    lower_date: str,
    inspection_time: str,
    inspection_date: str,
) -> str:
    return (
        "<p>La valutazione complessiva dei dati tanatologici, integrando i loro limiti temporali minimi e massimi, "
        f"consente di stimare che la morte sia avvenuta all'incirca <b>non oltre {duration} prima</b> "
        "dei rilievi effettuati nel corso dell’ispezione legale, "
        f"vale a dire <b>successivamente alle ore {lower_time} del {lower_date} "
        f"(ma prima delle ore {inspection_time} del {inspection_date})</b>.</p>"
    )


def final_sentence_dt_range(
    interval: str,
    start_time: str,
    start_date: str,
    end_time: str,
    end_date: str,
    same_date: bool,
) -> str:
    if same_date:
        window = f"tra le ore {start_time} e le ore {end_time} del {start_date}"
    else:
        window = f"tra le ore {start_time} del {start_date} e le ore {end_time} del {end_date}"
    return (
        "<p>La valutazione complessiva dei dati tanatologici, integrando i loro limiti temporali minimi e massimi, "
        f"consente di stimare che la morte sia avvenuta all'incirca <b>{interval} prima</b> "
        "dei rilievi effettuati nel corso dell’ispezione legale, "
        f"vale a dire circa <b>{window}</b>.</p>"
    )


def putrefactive_paragraph() -> str:
    return (
        "<ul><li>Per quanto riguarda i processi trasformativi post-mortali (compresi quelli putrefattivi), "
        "la loro insorgenza è influenzata da numerosi fattori, esogeni (ad esempio temperatura ambientale, "
        "esposizione ai fenomeni meteorologici…) ed endogeni (temperatura corporea, infezioni prima del decesso, "
        "presenza di ferite…). Poiché tali processi possono manifestarsi in un intervallo temporale estremamente "
        "variabile, da poche ore a diverse settimane dopo il decesso, la loro valutazione non permette di formulare "
        "ulteriori precisazioni sull’epoca della morte.</li></ul>"
    )


def parameter_summary(labels: list[str]) -> str:
    if len(labels) == 1:
        p = labels[0]
        return f"<p style='color:blue;font-size:small;'>La stima complessiva si basa sul seguente parametro: {p[0].lower() + p[1:]}.</p>"
    join = ', '.join(x[0].lower() + x[1:] for x in labels[:-1])
    join += f" e {labels[-1][0].lower() + labels[-1][1:]}"
    return f"<p style='color:blue;font-size:small;'>La stima complessiva si basa sui seguenti parametri: {join}.</p>"


def potente_paragraph(duration: str, days: str) -> str:
    return (
        "<ul><li>Il metodo proposto da Potente et al., basato sul modello di raffreddamento di Henssge, consente di stimare grossolanamente il tempo minimo post-mortem nei casi in cui i valori ottenuti con l'equazione di Henssge ricadano al di fuori del suo intervallo ottimale di applicazione. "
        f"Applicato al caso specifico, suggerisce che, al momento dell’ispezione legale, fossero trascorse almeno {duration} (≈ {days} giorni) dal decesso.</li></ul>"
    )


def cooling_input_paragraph(
    *,
    inspection_time,
    inspection_date,
    ta_text: str,
    tr_text: str,
    weight_text: str,
    t0_text: str,
    correction_description: str,
) -> str:
    if inspection_time is None or inspection_date is None:
        temperature_title = "Temperature misurate nel corso dell’ispezione legale:"
    else:
        temperature_title = (
            "Temperature misurate nel corso dell’ispezione legale verso le ore "
            f"{inspection_time} del {inspection_date}:"
        )

    return (
        "<ul><li>Per quanto attiene la valutazione del raffreddamento cadaverico, sono stati considerati gli elementi di seguito indicati."
        "<ul>"
        f"<li>{temperature_title}"
        "<ul>"
        f"<li>Temperatura ambientale: {ta_text} °C.</li>"
        f"<li>Temperatura rettale: {tr_text} °C.</li>"
        "</ul>"
        "</li>"
        f"<li>Peso del cadavere misurato: {weight_text} kg.</li>"
        f"<li>Temperatura corporea ipotizzata al momento della morte: {t0_text} °C.</li>"
        f"<li>Fattore di correzione ipotizzato in base alle condizioni ambientali (per quanto noto): {correction_description}.</li>"
        "</ul>"
        "</li></ul>"
    )


__all__ = [
    "LIVOR_DESCRIPTION_IT_BY_ID",
    "RIGOR_DESCRIPTION_IT_BY_ID",
    "SPECIAL_DESCRIPTION_IT_BY_ID",
    "SPECIAL_GRAPH_LABEL_IT_BY_ID",
    "TESTI_MACCHIE_LEGACY",
    "RIGIDITA_DESCRIZIONI_LEGACY",
    "SPECIAL_DESCRIPTIONS_LEGACY_BY_PARAM_LABEL",
    "NOMI_BREVI_LEGACY",
    "livor_description_it",
    "rigor_description_it",
    "livor_description_from_legacy_it",
    "rigor_description_from_legacy_it",
    "special_description_it",
    "special_graph_label_it",
    "format_hours_minutes",
    "format_hours_range",
    "simple_sentence_no_dt_not_over",
    "simple_sentence_no_dt_over",
    "simple_sentence_no_dt_range",
    "final_sentence_simple_over",
    "final_sentence_simple_not_over",
    "final_sentence_simple_range",
    "simple_sentence_dt_not_over",
    "simple_sentence_dt_over",
    "simple_sentence_dt_range",
    "final_sentence_dt_over",
    "final_sentence_dt_not_over",
    "final_sentence_dt_range",
    "putrefactive_paragraph",
    "parameter_summary",
    "potente_paragraph",
    "cooling_input_paragraph",
]
