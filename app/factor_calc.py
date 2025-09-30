# -*- coding: utf-8 -*-
# factor_calc.py — Logica per il fattore di correzione e la parentetica.

from dataclasses import dataclass
from typing import Optional, Dict, Any, Literal, Tuple
import numpy as np
import pandas as pd
from decimal import Decimal, ROUND_FLOOR, InvalidOperation

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

@dataclass
class FCContext:
    stato: Literal["Asciutto", "Bagnato", "Immerso"]
    acqua: Optional[Literal["stagnante", "corrente"]] = None
    counts: Optional[Dict[str, int]] = None  # {"sottili":..,"spessi":..,"coperte_medie":..,"coperte_pesanti":..}
    superficie_display: Optional[str] = None
    correnti_aria: bool = False

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
    "Pavimento di casa, piano in legno.": SURF_INDIFF,
    "Asfalto, terreno o prato asciutti": SURF_INDIFF,
    "Materasso o tappeto spesso": SURF_ISOL,
    "Divano imbottito, sacco a pelo tecnico, polistirolo": SURF_MOLTOI,
    "Cemento, pietra, PVC": SURF_COND,
    "Pavimento freddo (all'aperto, in cantina…)": SURF_COND,
    "Piano metallico (in ambiente interno)": SURF_COND,
    "Superficie metallica spessa (all’aperto)": SURF_MOLTOC,
    "Strato di foglie umide (≥2 cm)": SURF_FOGLIU,
    "Strato di foglie secche (≥2 cm)": SURF_FOGLIS,
}

SURF_DISPLAY_ORDER = [
    "Pavimento di casa, piano in legno.",
    "Asfalto, terreno o prato asciutti",
    "Materasso o tappeto spesso",
    "Divano imbottito, sacco a pelo tecnico, polistirolo",
    "Cemento, pietra, PVC",
    "Pavimento freddo (all'aperto, in cantina…)",
    "Piano metallico (in ambiente interno)",
    "Superficie metallica spessa (all’aperto)",
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
    return 0.90

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
    # helper locale per il floor a step 0,05
    from decimal import Decimal, ROUND_FLOOR
    def _floor_to_step(x: float, step: float = 0.05) -> float:
        d = Decimal(str(x)); s = Decimal(str(step))
        return float((d / s).to_integral_value(rounding=ROUND_FLOOR) * s)

    # Caso IMMERSO
    if stato == "Immerso":
        base = 0.50 if (acqua == "stagnante") else 0.35
        fatt_base = clamp(base)
        # adatta_per_peso mantiene il suo round(..., 2)
        fatt_finale_raw = adatta_per_peso(fatt_base, peso, tabella2_df)
        # floor finale a 0,05 (unico arrotondamento aggiuntivo)
        fatt_finale = _floor_to_step(fatt_finale_raw)
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
    superf_key = surface_display_to_key(superficie_display) if stato == "Asciutto" else None

    f_tmp = float(f_vest)
    if stato == "Asciutto" and superf_key is not None:
        f_tmp = applica_regole_superficie(f_tmp, superf_key, stato, counts)

    f_corr, _ = applica_correnti(clamp(f_tmp), stato, superf_key, correnti_aria, counts, f_vest)
    if np.isnan(f_corr):
        f_corr = 1.0
    f_corr = clamp(float(f_corr))

    # adatta_per_peso mantiene il suo round(..., 2)
    fatt_finale_raw = adatta_per_peso(f_corr, peso, tabella2_df)
    # floor finale a 0,05 (unico arrotondamento aggiuntivo)
    fatt_finale = _floor_to_step(fatt_finale_raw)
    peso_adattato = (abs(fatt_finale_raw - f_corr) > 1e-12)

    riass = {
        "stato": stato,
        "sottili": int(counts.sottili),
        "spessi": int(counts.spessi),
        "cop_medie": int(counts.coperte_medie),
        "cop_pesanti": int(counts.coperte_pesanti),
        "superficie": superficie_display if stato == "Asciutto" else "/",
        "superficie_key": superf_key,
        "correnti": ("Correnti d'aria presenti" if correnti_aria else None),
        "peso_adattato": bool(peso_adattato),
    }
    return ComputeResult(fattore_base=f_corr, fattore_finale=fatt_finale, riassunto=riass)

# --------------------------------
# Ricalcolo/Autosync FC su cambio peso (riuso compute_factor)
# --------------------------------
def _counts_from_ctx(counts_like: Optional[Dict[str, Any]]) -> DressCounts:
    d = counts_like or {}
    return DressCounts(
        sottili=int(d.get("sottili", 0) or 0),
        spessi=int(d.get("spessi", 0) or 0),
        coperte_medie=int(d.get("coperte_medie", 0) or 0),
        coperte_pesanti=int(d.get("coperte_pesanti", 0) or 0),
    )

def recompute_fc_for_weight(ctx: FCContext, peso: float, tabella2_df: Optional[pd.DataFrame]) -> ComputeResult:
    counts = _counts_from_ctx(ctx.counts)
    return compute_factor(
        stato=ctx.stato,
        acqua=ctx.acqua,
        counts=counts,
        superficie_display=ctx.superficie_display if ctx.stato == "Asciutto" else None,
        correnti_aria=bool(ctx.correnti_aria),
        peso=float(peso),
        tabella2_df=tabella2_df,
    )

def autosync_fc_if_needed(
    fc_corrente: float,
    peso_precedente: Optional[float],
    peso_nuovo: float,
    ctx: Optional[Dict[str, Any] | FCContext],
    tabella2_df: Optional[pd.DataFrame],
    *,
    soglia_fc: float = 1.40
) -> Tuple[float, bool]:
    """
    Se FC > soglia e il peso cambia, ricalcola FC con Tabella 2 usando il contesto.
    Ritorna (fc_aggiornato, changed_bool).
    """
    try:
        fc_val = float(fc_corrente)
    except Exception:
        return fc_corrente, False

    if ctx is None or fc_val <= soglia_fc:
        return fc_corrente, False

    try:
        p_new = float(peso_nuovo)
        p_prev = None if (peso_precedente is None) else float(peso_precedente)
    except Exception:
        return fc_corrente, False

    if p_prev is not None and abs(p_new - p_prev) < 1e-9:
        return fc_corrente, False

    # normalizza ctx
    if isinstance(ctx, FCContext):
        ctx_obj = ctx
    else:
        ctx_obj = FCContext(
            stato=ctx.get("stato"),
            acqua=ctx.get("acqua"),
            counts=ctx.get("counts") or {
                "sottili": ctx.get("sottili", 0),
                "spessi": ctx.get("spessi", 0),
                "coperte_medie": ctx.get("cop_medie", 0),
                "coperte_pesanti": ctx.get("cop_pesanti", 0),
            },
            superficie_display=ctx.get("superficie") if ctx.get("stato") == "Asciutto" else None,
            correnti_aria=bool(ctx.get("correnti") not in (None, "/", "")),
        )

    res = recompute_fc_for_weight(ctx_obj, p_new, tabella2_df)
    fc_new = round(float(res.fattore_finale), 2)
    if abs(fc_new - fc_val) > 1e-12:
        return fc_new, True
    return fc_corrente, False

# --------------------------------
# Parentetica (descrizione FC)
# --------------------------------
def _classifica_superficie(s: Optional[str]) -> Optional[str]:
    """Riduce il testo della superficie a: 'conduttiva' | 'isolante' | 'indifferente'."""
    if not s or s == "/":
        return None
    s_low = s.lower()
    if ("metall" in s_low) or ("cemento" in s_low) or ("pietra" in s_low) or ("pvc" in s_low) or ("pavimentazione fredda" in s_low) or ("pavimentazione esterna" in s_low):
        return "conduttiva"
    if ("materasso" in s_low) or ("tappeto" in s_low) or ("imbottito" in s_low) or ("imbottitura" in s_low) or ("foglie" in s_low) or ("polistirolo" in s_low):
        return "isolante"
    return "indifferente"

def _classifica_superficie_from_key(k: Optional[str]) -> Optional[str]:
    if not k or k == SURF_INDIFF:
        return None
    if k in {SURF_ISOL, SURF_FOGLIU, SURF_FOGLIS}:
        return "isolante"
    if k == SURF_MOLTOI:
        return "molto isolante"
    if k == SURF_COND:
        return "conduttiva"
    if k == SURF_MOLTOC:
        return "molto conduttiva"
    return None

def _format_stato(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    if s == "Immerso":
        return "corpo immerso"
    if s == "Bagnato":
        return "corpo bagnato"
    # Asciutto non va indicato
    return None

def _format_corrente(c: Optional[str]) -> Optional[str]:
    if not c or c == "/":
        return None
    c_low = c.lower()
    if "acqua corrente" in c_low:
        return "in acqua corrente"
    if "acqua stagnante" in c_low:
        return "in acqua stagnante"
    if "correnti d'aria" in c_low or "con correnti" in c_low or "esposto a corrente" in c_low:
        return "con correnti d'aria"
    return None  # non scrivere se assenti

def _format_indumenti(sottili: int, spessi: int, stato: Optional[str]) -> Optional[str]:
    if sottili == 0 and spessi == 0:
        if stato in ("Bagnato", "Immerso"):
            return "nudo"
        else:
            return "corpo nudo"
    if spessi == 0:
        if 1 <= sottili <= 2: return "con indosso pochi strati leggeri"
        if 3 <= sottili <= 4: return "con indosso alcuni strati leggeri"
        if sottili >= 5:      return "con indosso molti strati leggeri"
    if sottili == 0:
        if 1 <= spessi <= 2: return "con indosso pochi strati pesanti"
        if 3 <= spessi <= 4: return "con indosso vari strati pesanti"
        if spessi >= 5:      return "con indosso molti strati pesanti"
    tot = sottili + spessi
    if 1 <= tot <= 2: return "con indosso pochi strati di vario spessore"
    if 3 <= tot <= 4: return "con indosso alcuni strati di vario spessore"
    if tot >= 5:      return "con indosso molti strati di vario spessore"
    return None

def _format_coperte(cop_med: int, cop_pes: int, is_nudo: bool) -> Optional[str]:
    if cop_med == 0 and cop_pes == 0:
        return None
    if cop_med > 0 and cop_pes == 0:
        if cop_med == 1:  base = "sotto una coperta di medio spessore"
        elif cop_med == 2: base = "sotto due coperte di medio spessore"
        else:              base = "sotto varie coperte di medio spessore"
        return ("corpo nudo " + base) if is_nudo else base
    if cop_pes > 0 and cop_med == 0:
        if cop_pes == 1:  base = "sotto una coperta pesante"
        elif cop_pes == 2: base = "sotto due coperte pesanti"
        else:              base = "sotto varie coperte pesanti"
        return ("corpo nudo " + base) if is_nudo else base
    tot = cop_med + cop_pes
    if 1 <= tot <= 2: base = "sotto poche coperte di diverso spessore"
    elif 3 <= tot <= 4: base = "sotto alcune coperte di diverso spessore"
    else: base = "sotto molte coperte di diverso spessore"
    return ("corpo nudo " + base) if is_nudo else base

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
    cf_txt = f"{float(cf_value):.2f}"

    if manual_override:
        return cf_txt

    if not riassunto:
        return f"{cf_txt} (in base ai fattori scelti: {fallback_text})." if fallback_text else f"{cf_txt} (da adattare sulla base dei fattori scelti)."

    stato_txt = _format_stato(riassunto.get("stato"))

    sottili = int(riassunto.get("sottili", 0))
    spessi  = int(riassunto.get("spessi", 0))
    indumenti_txt = _format_indumenti(sottili, spessi, riassunto.get("stato"))

    cop_med = int(riassunto.get("cop_medie", 0))
    cop_pes = int(riassunto.get("cop_pesanti", 0))
    is_nudo = (sottili == 0 and spessi == 0)
    coperte_txt = _format_coperte(cop_med, cop_pes, is_nudo)

    superf_cat = _classifica_superficie_from_key(riassunto.get("superficie_key"))
    superf_txt = f"adagiato su superficie termicamente {superf_cat}" if superf_cat else None

    corr_val = riassunto.get("correnti")
    corr_txt = None
    if isinstance(corr_val, str):
        corr_txt = _format_corrente(corr_val)

    parts = [p for p in (stato_txt, indumenti_txt, coperte_txt, superf_txt, corr_txt) if p]

    nota_peso = "Il fattore di correzione è stato adattato per il peso corporeo." if riassunto.get("peso_adattato") else None

    if parts or nota_peso:
        inner = ", ".join(parts)
        if nota_peso:
            inner = (inner + ". " + nota_peso) if inner else nota_peso
        return f"{cf_txt} ({inner})"

    return f"{cf_txt} (in base ai fattori scelti: {fallback_text})." if fallback_text else f"{cf_txt} (da adattare sulla base dei fattori scelti)."
    
