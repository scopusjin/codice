from app.plotting import compute_plot_data, render_ranges_plot

# --- Sezione dedicata alla generazione del grafico (spacchettata) ---
num_params_grafico = 0
if macchie_range_valido: num_params_grafico += 1
if rigidita_range_valido: num_params_grafico += 1
if raffreddamento_calcolabile: num_params_grafico += 1
num_params_grafico += len([
    p for p in parametri_aggiuntivi_da_considerare
    if not np.isnan(p["range_traslato"][0]) and not np.isnan(p["range_traslato"][1])
])

if num_params_grafico > 0:
    plot_data = compute_plot_data(
        macchie_range=macchie_range if macchie_range_valido else (np.nan, np.nan),
        macchie_medi_range=macchie_medi_range if macchie_range_valido else None,
        rigidita_range=rigidita_range if rigidita_range_valido else (np.nan, np.nan),
        rigidita_medi_range=rigidita_medi_range if rigidita_range_valido else None,
        raffreddamento_calcolabile=raffreddamento_calcolabile,
        t_min_raff_hensge=t_min_raff_hensge if raffreddamento_calcolabile else np.nan,
        t_max_raff_hensge=t_max_raff_hensge if raffreddamento_calcolabile else np.nan,
        t_med_raff_hensge_rounded_raw=t_med_raff_hensge_rounded_raw if raffreddamento_calcolabile else np.nan,
        Qd_val_check=Qd_val_check if raffreddamento_calcolabile else np.nan,
        mt_ore=mt_ore if ('mt_ore' in locals()) else None,
        INF_HOURS=INF_HOURS,
    )

    fig = render_ranges_plot(plot_data)

    # Linee rosse dell’intersezione: restano qui (identiche)
    if overlap and (np.isnan(comune_fine) or comune_fine > 0):
        ax = fig.axes[0]
        if comune_inizio < plot_data["tail_end"]:
            ax.axvline(max(0, comune_inizio), color='red', linestyle='--')
        if not np.isnan(comune_fine) and comune_fine > 0:
            ax.axvline(min(plot_data["tail_end"], comune_fine), color='red', linestyle='--')

    st.pyplot(fig)

