# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 17:29:36 2026

@author: rmb80
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Synthetic Germline Dashboard")

st.title("Synthetic Germline Cancer Dashboard")
st.caption("⚠️ All data is simulated for demonstration purposes")

# -----------------------
# Synthetic Data
# -----------------------

np.random.seed(42)

cancers = ["Breast", "Ovarian", "Prostate", "Colon"]
genes = ["BRCA1", "BRCA2", "TP53", "PALB2", "CHEK2", "ATM"]

cohort_sizes = {
    "Breast": 1000,
    "Ovarian": 600,
    "Prostate": 800,
    "Colon": 750
}

prevalence = {
    "Breast": {"BRCA1": 0.08, "BRCA2": 0.07, "TP53": 0.02, "PALB2": 0.03, "CHEK2": 0.04, "ATM": 0.05},
    "Ovarian": {"BRCA1": 0.15, "BRCA2": 0.10, "TP53": 0.01, "PALB2": 0.02, "CHEK2": 0.01, "ATM": 0.02},
    "Prostate": {"BRCA1": 0.02, "BRCA2": 0.06, "TP53": 0.01, "PALB2": 0.02, "CHEK2": 0.03, "ATM": 0.04},
    "Colon": {"BRCA1": 0.01, "BRCA2": 0.01, "TP53": 0.05, "PALB2": 0.01, "CHEK2": 0.02, "ATM": 0.03}
}

data = []

for cancer in cancers:
    for gene in genes:
        cases = int(cohort_sizes[cancer] * prevalence[cancer][gene])
        data.append({
            "Cancer": cancer,
            "Gene": gene,
            "Cases": cases,
            "Frequency (%)": prevalence[cancer][gene] * 100
        })

df = pd.DataFrame(data)

# -----------------------
# UI
# -----------------------

selected_cancer = st.selectbox("Select Cancer Type", cancers)

filtered_df = df[df["Cancer"] == selected_cancer]

fig = px.bar(
    filtered_df,
    x="Gene",
    y="Cases",
    text="Frequency (%)",
    title=f"Germline Findings in {selected_cancer}"
)

st.plotly_chart(fig, use_container_width=True)