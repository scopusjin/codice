# -*- coding: utf-8 -*-
# factor_calc.py — Logica per il fattore di correzione e la parentetica.

from dataclasses import dataclass
from typing import Optional, Dict, Any, Literal, Tuple
import numpy as np
import pandas as pd
from decimal import Decimal, ROUND_FLOOR

from app import i18n

def floor_to_step(x: float, step: float = 0.05) -> float:
    """Arrotonda sempre per difetto al multiplo più vicino di step (default 0.05)."""
    d = Decimal(str(x))
    s = Decimal(str(step))
    return float((d / s).to_integral_value(rounding=ROUND_FLOOR) * s)

# --------------------------------
# Datamodel di input/riassunto
# --------------------------------
@dataclass
class DressCounts:
    sottili: int = 0
    spessi: int = 0
    coperte_medie: int = 0
    coperte_pesanti: int = 0

@dataclass
class ComputeResult:
    fattore_base: float
    fattore_finale: float
    riassunto: Dict[str, Any]  # per sessione/parentetica

# --------------------------------
# Superfici (mappa & ordine)
# --------------------------------
SURF_INDIFF = "INDIFFERENTE"
SURF_ISOL   = "ISOLANTE"
SURF_MOLTOI = "MOLTO_ISOLANTE"
SURF_COND   = "CONDUTTIVO"
SURF_MOLTOC = "MOLTO_CONDUTTIVO"
SURF_FOGLIU = "FOGLIE_UMIDE"
SURF_FOGLIS = "FOGLIE_SECCHE"

SURF_DISPLAY_TO_KEY = {
    "Pavimento di casa/piano in legno.": SURF_INDIFF,
    "Asfalto/terreno/prato asciutti": SURF_INDIFF,
    "Materasso/tappeto spesso": SURF_ISOL,
    "Divano/sacco a pelo tecnico/polistirolo": SURF_MOLTOI,
    "Cemento/pietra/PVC": SURF_COND,
    "Pavimento freddo (all’aperto/in cantina)": SURF_COND,
    "Piano metallico (all’interno)": SURF_COND,
    "Piano metallico spesso (all’aperto)": SURF_MOLTOC,
    "Strato di foglie umide (≥2 cm)": SURF_FOGLIU,
    "Strato di foglie secche (≥2 cm)": SURF_FOGLIS,
}

SURF_DISPLAY_ORDER = [
    "Pavimento di casa/piano in legno.",
    "Asfalto/terreno/prato asciutti",
    "Materasso/tappeto spesso",
    "Divano/sacco a pelo tecnico/polistirolo",
    "Cemento/pietra/PVC",
    "Pavimento freddo (all’aperto/in cantina)",
    "Piano metallico (all’interno)",
    "Piano metallico spesso (all’aperto)",
    "Strato di foglie umide (≥2 cm)",
    "Strato di foglie secche (≥2 cm)",
]

def surface_display_to_key(s: Optional[str]) -> Optional[str]:
    if not s or s == "/":
        return None
    return SURF_DISPLAY_TO_KEY.get(s, SURF_INDIFF)

# --------------------------------
# Helpers “motore”
# --------------------------------
def clamp(x: float, lo: float = 0.35, hi: float = 3.0) -> float:
    return max(lo, min(hi, x))

def is_nudo(c: DressCounts) -> bool:
    return (c.sottili == 0 and c.spessi == 0 and c.coperte_medie == 0 and c.coperte_pesanti == 0)

def fattore_vestiti_coperte(c: DressCounts) -> float:
    # base da coperte, poi contributi sottili/spessi
    if c.coperte_pesanti > 0:
        f = 2.0 + max(0, c.coperte_pesanti - 1) * 0.3 + c.coperte_medie * 0.2
    elif c.coperte_medie > 0:
        f = 1.8 + max(0, c.coperte_medie - 1) * 0.2
    else:
        f = 1.0
    f += c.sottili * 0.07 + c.spessi * 0.14
    return float(f)

def applica_regole_superficie(fatt: float, superficie_key: Optional[str], stato: str, c: DressCounts) -> float:
    if superficie_key is None or superficie_key == SURF_INDIFF:
        return fatt

    tot_items = c.sottili + c.spessi + c.coperte_medie + c.coperte_pesanti
    only_thin_1   = (c.sottili == 1 and c.spessi == 0 and c.coperte_medie == 0 and c.coperte_pesanti == 0)
    only_thin_1_2 = (c.sottili in (1, 2) and c.spessi == 0 and c.coperte_medie == 0 and c.coperte_pesanti == 0)

    if superficie_key == SURF_ISOL:
        if tot_items == 0:      return 1.10
        elif only_thin_1:       return 1.20
        else:                   return fatt + 0.10

    if superficie_key == SURF_MOLTOI:
        if tot_items == 0:      return 1.30
        elif only_thin_1_2:     return fatt + 0.30
        else:                   return fatt + 0.10

    if superficie_key == SURF_COND:
        if tot_items == 0:      return 0.75
        elif only_thin_1:       return fatt - 0.20
        else:                   return fatt - 0.10

    if superficie_key == SURF_MOLTOC:
        if (stato == "Asciutto") and is_nudo(c):
            return 0.55
        return fatt

    if superficie_key == SURF_FOGLIU:
        if tot_items == 0:      return 1.20
        elif only_thin_1_2:     return fatt + 0.20
        else:                   return fatt + 0.10

    if superficie_key == SURF_FOGLIS:
        if tot_items == 0:      return 1.50
        elif only_thin_1_2:     return fatt + 0.30
        else:                   return fatt + 0.20

    return fatt

def bagnato_base_senza_correnti(sottili: int, spessi: int) -> float:
    if spessi > 2 or sottili > 4:
        return 1.20
    if spessi == 2 or (3 <= sottili <= 4):
        return 1.15
    if spessi == 1 or sottili == 2:
        return 1.10
    if sottili == 1:
        return 1.00
    return 0.75

def bagnato_con_correnti(sottili: int, spessi: int) -> float:
    if spessi >= 2 or sottili >= 4:
        return 0.90
    if (spessi == 1 and sottili == 1) or (sottili == 3 and spessi == 0):
        return 0.80
    if (spessi == 1 and sottili == 0) or (sottili == 2 and spessi == 0):
        return 0.75
    if (sottili == 1 and spessi == 0):
        return 0.70
    return 0.70

def bagnato_nudo_range_superficie(superficie_key: Optional[str]) -> Optional[Tuple[float, float]]:
    """Range orientativo per nudo+bagnato+aria ferma su superfici non neutre concordate."""
    if superficie_key == SURF_ISOL:
        return (0.85, 0.95)
    if superficie_key == SURF_MOLTOI:
        return (0.95, 1.10)
    if superficie_key == SURF_COND:
        return (0.60, 0.75)
    if superficie_key == SURF_MOLTOC:
        return (0.55, 0.75)
    return None

def applica_correnti(fatt: float,
                     stato: str,
                     superficie_key: Optional[str],
                     correnti_presenti: bool,
                     c: DressCounts,
                     f_vest_cop: float) -> Tuple[float, bool]:
    """Restituisce (fattore, applicate_correnti_bool)."""
    def is_poco_vestito(fvc: float) -> bool:
        return (1.0 < fvc < 1.2)

    if stato == "Bagnato":
        sottili_eff = c.sottili
        spessi_eff  = c.spessi
        if (c.coperte_medie > 0 or c.coperte_pesanti > 0):
            sottili_eff = max(sottili_eff, 5)
            spessi_eff  = max(spessi_eff, 3)
        if correnti_presenti:
            return bagnato_con_correnti(sottili_eff, spessi_eff), True
        else:
            return bagnato_base_senza_correnti(sottili_eff, spessi_eff), True

    if not correnti_presenti:
        return fatt, False

    nudo_asciutto = (stato == "Asciutto" and is_nudo(c))
    poco_vest     = (stato == "Asciutto" and is_poco_vestito(f_vest_cop))

    if superficie_key == SURF_INDIFF:
        if nudo_asciutto: return fatt * 0.75, True
        if poco_vest:     return fatt * 0.80, True
    elif superficie_key == SURF_ISOL:
        if nudo_asciutto: return fatt * 0.80, True
        if poco_vest:     return fatt * 0.85, True
    elif superficie_key == SURF_MOLTOI:
        if nudo_asciutto or poco_vest: return fatt * 0.90, True
    elif superficie_key == SURF_COND:
        if nudo_asciutto or poco_vest: return fatt * 0.75, True
    elif superficie_key == SURF_MOLTOC:
        return fatt * 0.75, True

    return fatt, False

# --------------------------------
# Adattamento per il peso (Tabella 2)
# --------------------------------
def _parse_peso_header(col: str) -> Optional[float]:
    s = str(col).strip().lower().replace('kg', '').replace('w', '')
    num = ''.join(ch for ch in s if (ch.isdigit() or ch in '.,'))
    num = num.replace(',', '.')
    try:
        return float(num) if num not in ("", ".", ",") else None
    except ValueError:
        return None

def adatta_per_peso(fattore_base: float, peso: float, tabella2: Optional[pd.DataFrame]) -> float:
    """
    Doppia interpolazione (righe e pesi).
    Restituisce valore clampato [0.35, 3.0] e arrotondato a 2 decimali.
    Early-exit se fc_base < 1.4 (fuori tabella) o peso≈70.
    """
    # --- guardie veloci ---
    try:
        fb = float(fattore_base)
        if tabella2 is None or np.isnan(fb) or peso is None:
            return round(clamp(fb), 2)
        pw = float(peso)
    except Exception:
        return round(clamp(float(fattore_base)), 2)

    # fuori campo tabella: NON adattare
    if fb < 1.4:
        return round(clamp(fb), 2)

    # nessun adattamento se peso ~ 70 kg
    if abs(pw - 70.0) < 1e-9:
        return round(clamp(fb), 2)

    # --- parse colonne peso ---
    pesi_col = {col: _parse_peso_header(col) for col in tabella2.columns}
    pesi_col = {col: w for col, w in pesi_col.items() if w is not None}
    if len(pesi_col) < 2:
        return round(clamp(fb), 2)

    # ordina per peso crescente
    cols_sorted = sorted(pesi_col.items(), key=lambda x: x[1])
    col_names = [c for c, _ in cols_sorted]
    col_weights = np.array([w for _, w in cols_sorted], dtype=float)

    # colonna ~70 kg
    ref_idx = int(np.argmin(np.abs(col_weights - 70.0)))
    col70 = col_names[ref_idx]

    # serie 70 kg numerica
    v70 = pd.to_numeric(tabella2[col70], errors="coerce")
    valid_idx = v70.dropna().index
    if len(valid_idx) == 0:
        return round(clamp(fb), 2)

    # ordina righe per valore a 70 kg
    v70_valid = v70.loc[valid_idx]
    order = np.argsort(v70_valid.values)
    v_sorted = v70_valid.values[order]
    idx_sorted = v70_valid.index.values[order]

    # trova r_low, r_high, t
    if fb <= v_sorted[0]:
        r_low = r_high = idx_sorted[0]; t = 0.0
    elif fb >= v_sorted[-1]:
        r_low = r_high = idx_sorted[-1]; t = 0.0
    else:
        pos = int(np.searchsorted(v_sorted, fb, side="left"))
        r_low, r_high = idx_sorted[pos-1], idx_sorted[pos]
        denom = (v_sorted[pos] - v_sorted[pos-1])
        t = 0.0 if denom == 0 else float((fb - v_sorted[pos-1]) / denom)

    # valore alla riga r e al peso 'pw' con interp tra colonne adiacenti
    def _val_row_at_weight(row_idx) -> Optional[float]:
        row_vals = pd.to_numeric(tabella2.loc[row_idx, col_names], errors="coerce").values.astype(float)
        if pw <= col_weights[0]:
            return row_vals[0] if np.isfinite(row_vals[0]) else None
        if pw >= col_weights[-1]:
            return row_vals[-1] if np.isfinite(row_vals[-1]) else None
        hi = int(np.searchsorted(col_weights, pw, side="right"))
        lo = hi - 1
        w_lo, w_hi = col_weights[lo], col_weights[hi]
        v_lo, v_hi = row_vals[lo], row_vals[hi]
        if not np.isfinite(v_lo) and np.isfinite(v_hi): return float(v_hi)
        if not np.isfinite(v_hi) and np.isfinite(v_lo): return float(v_lo)
        if not (np.isfinite(v_lo) and np.isfinite(v_hi)): return None
        alpha = (pw - w_lo) / (w_hi - w_lo)
        return float(v_lo + alpha * (v_hi - v_lo))

    val_low  = _val_row_at_weight(r_low)
    val_high = _val_row_at_weight(r_high)

    if val_low is None and val_high is None:
        return round(clamp(fb), 2)
    if r_low == r_high or val_high is None:
        return round(clamp(float(val_low)), 2)
    if val_low is None:
        return round(clamp(float(val_high)), 2)

    fc_user = float(val_low + t * (val_high - val_low))
    return round(clamp(fc_user), 2)


# --------------------------------
# API principale di calcolo
# --------------------------------
def compute_factor(
    stato: Literal["Asciutto", "Bagnato", "Immerso"],
    acqua: Optional[Literal["stagnante", "corrente"]],
    counts: DressCounts,
    superficie_display: Optional[str],
    correnti_aria: bool,
    peso: float,
    tabella2_df: Optional[pd.DataFrame] = None
) -> ComputeResult:
    # Caso IMMERSO
    if stato == "Immerso":
        base = 0.50 if (acqua == "stagnante") else 0.35
        fatt_base = clamp(base)
        # adatta_per_peso mantiene il suo round(..., 2)
        fatt_finale_raw = adatta_per_peso(fatt_base, peso, tabella2_df)
        # floor finale a 0,05 (unico arrotondamento aggiuntivo)
        fatt_finale = floor_to_step(fatt_finale_raw)
        peso_adattato = (abs(fatt_finale_raw - fatt_base) > 1e-12)
        return ComputeResult(
            fattore_base=fatt_base,
            fattore_finale=fatt_finale,
            riassunto={
                "stato": "Immerso",
                "sottili": 0, "spessi": 0, "cop_medie": 0, "cop_pesanti": 0,
                "superficie": "/",
                "superficie_key": None,
                "correnti": "in acqua stagnante" if acqua == "stagnante" else "in acqua corrente",
                "peso_adattato": bool(peso_adattato),
            }
        )

    # Asciutto / Bagnato
    f_vest = fattore_vestiti_coperte(counts)
    superf_key = surface_display_to_key(superficie_display) if stato in ("Asciutto", "Bagnato") else None

    f_tmp = float(f_vest)
    if stato == "Asciutto" and superf_key is not None:
        f_tmp = applica_regole_superficie(f_tmp, superf_key, stato, counts)

    f_corr, _ = applica_correnti(clamp(f_tmp), stato, superf_key, correnti_aria, counts, f_vest)
    if np.isnan(f_corr):
        f_corr = 1.0
    f_corr = clamp(float(f_corr))

    fc_range_suggerito = None
    if stato == "Bagnato" and is_nudo(counts) and not correnti_aria:
        fc_range_suggerito = bagnato_nudo_range_superficie(superf_key)

    # adatta_per_peso mantiene il suo round(..., 2)
    fatt_finale_raw = adatta_per_peso(f_corr, peso, tabella2_df)
    # floor finale a 0,05 (unico arrotondamento aggiuntivo)
    fatt_finale = floor_to_step(fatt_finale_raw)
    peso_adattato = (abs(fatt_finale_raw - f_corr) > 1e-12)

    riass = {
        "stato": stato,
        "sottili": int(counts.sottili),
        "spessi": int(counts.spessi),
        "cop_medie": int(counts.coperte_medie),
        "cop_pesanti": int(counts.coperte_pesanti),
        "superficie": superficie_display if stato in ("Asciutto", "Bagnato") else "/",
        "superficie_key": superf_key,
        "correnti": ("Correnti d'aria presenti" if correnti_aria else None),
        "peso_adattato": bool(peso_adattato),
        "fc_range_suggerito": fc_range_suggerito,
    }
    return ComputeResult(fattore_base=f_corr, fattore_finale=fatt_finale, riassunto=riass)

# --------------------------------
# Parentetica (descrizione FC)
# --------------------------------
def build_cf_description(
    cf_value: float,
    riassunto: Optional[Dict[str, Any]],
    fallback_text: Optional[str] = None,
    manual_override: bool = False  # True se FC inserito/modificato manualmente
) -> str:
    """
    Rende una stringa tipo:
    "1.40 (corpo nudo sotto una coperta pesante, adagiato su superficie termicamente conduttiva, con correnti d'aria. Il fattore di correzione è stato adattato per il peso corporeo.)"
    Regole:
      - Nessuna parentesi se manual_override=True.
      - Non menzionare 'asciutto'; 'bagnato' non usato; 'Immerso' → 'corpo immerso' + stato acqua.
      - Superficie solo se ≠ indifferente.
      - Correnti d'aria solo se presenti.
      - Aggiungi frase peso se riassunto['peso_adattato'] è True.
    """
    return i18n.factor_correction_description(
        cf_value=cf_value,
        summary=riassunto,
        fallback_text=fallback_text,
        manual_override=manual_override,
    )
