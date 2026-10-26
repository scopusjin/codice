"""English labels for the field interface; existing state IDs are unchanged."""

from app import tanatology_states as ts


MSIL_LIVOR_LABEL_BY_ID = {
    ts.LIVOR_NOT_ASSESSED: "🩸 POSTMORTEM LIVIDITY?",
    ts.LIVOR_ABSENT: "Lividity absent",
    ts.LIVOR_CONFLUING: "Lividity present, not yet confluent",
    ts.LIVOR_CONFLUENT: "Confluent lividity",
    ts.LIVOR_FULLY_MIGRATABLE: "Complete shifting of livores (confluence unspecified)",
    ts.LIVOR_CONFLUENT_FULLY_MIGRATABLE: "Confluent lividity, with complete shifting",
    ts.LIVOR_PARTIALLY_MIGRATABLE: "Incomplete shifting of livores",
    ts.LIVOR_AT_LEAST_PARTIALLY_MIGRATABLE: "Shifting of livores (extent unspecified)",
    ts.LIVOR_FIXED: "Fixed lividity",
}

MSIL_RIGOR_LABEL_BY_ID = {
    ts.RIGOR_NOT_ASSESSED: "💪🏻 RIGOR MORTIS?",
    ts.RIGOR_ABSENT: "Rigor mortis absent",
    ts.RIGOR_DEVELOPING: "Rigor mortis present and increasing",
    ts.RIGOR_FULL: "Fully developed and generalised rigor mortis",
    ts.RIGOR_RESOLVING: "Rigor mortis resolving",
    ts.RIGOR_RESOLVED: "Rigor mortis resolved",
}
