# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 17:29:36 2026

@author: rmb80
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Germline Feasibility Dashboard", layout="wide")

st.title("Germline Translational Feasibility Dashboard")
st.caption("Simulated aggregate dataset for educational purposes only.")

# -----------------------
# Synthetic Aggregate Data
# -----------------------

np.random.seed(42)

cancers = ["Breast", "Ovarian", "Prostate", "Colon"]
genes = ["BRCA1", "BRCA2", "TP53", "PALB2", "CHEK2", "ATM"]

project_categories = [
    "None",
    "WGS",
    "WES",
    "SNP",
    "WGS + WES",
    "WGS + SNP",
    "WES + SNP",
    "WGS + WES + SNP"
]

data = []

base_totals = {
    "Breast": 1200,
    "Ovarian": 700,
    "Prostate": 900,
    "Colon": 800
}

pre_cancer_rate = {
    "Breast": 0.35,
    "Ovarian": 0.30,
    "Prostate": 0.25,
    "Colon": 0.20
}

for cancer in cancers:
    total_cases = base_totals[cancer]
    pre_cases = int(total_cases * pre_cancer_rate[cancer])
    post_cases = total_cases - pre_cases

    # Distribute projects only among pre-cancer samples
    project_distribution = {
        "None": 0.40,
        "WGS": 0.15,
        "WES": 0.15,
        "SNP": 0.10,
        "WGS + WES": 0.08,
        "WGS + SNP": 0.05,
        "WES + SNP": 0.04,
        "WGS + WES + SNP": 0.03
    }

    for gene in genes:
        # Random gene distribution
        gene_fraction = np.random.uniform(0.05, 0.20)

        # Pre-cancer rows
        for project, pct in project_distribution.items():
            cases = int(pre_cases * pct * gene_fraction)
            data.append([cancer, "Yes", project, gene, cases])

        # Post-cancer rows (no projects allowed)
        cases = int(post_cases * gene_fraction)
        data.append([cancer, "No", "None", gene, cases])

df = pd.DataFrame(data, columns=["Cancer", "PreCancer", "Project", "Gene", "Cases"])

# -----------------------
# Filters
# -----------------------

col1, col2, col3 = st.columns(3)

with col1:
    selected_cancer = st.selectbox("Cancer Type", cancers)

with col2:
    pre_filter = st.selectbox("Pre-Cancer Blood Sample", ["All", "Yes", "No"])

with col3:
    project_filter = st.multiselect(
        "Project Participation",
        project_categories,
        default=project_categories
    )

filtered_df = df[df["Cancer"] == selected_cancer]

if pre_filter != "All":
    filtered_df = filtered_df[filtered_df["PreCancer"] == pre_filter]

filtered_df = filtered_df[filtered_df["Project"].isin(project_filter)]

# -----------------------
# KPIs
# -----------------------

total_cases = filtered_df["Cases"].sum()

pre_cases = df[
    (df["Cancer"] == selected_cancer) &
    (df["PreCancer"] == "Yes")
]["Cases"].sum()

project_cases = df[
    (df["Cancer"] == selected_cancer) &
    (df["Project"] != "None")
]["Cases"].sum()

k1, k2, k3 = st.columns(3)
k1.metric("Total Cases (Filtered)", total_cases)
k2.metric("% With Pre-Cancer Sample", f"{round(pre_cases / base_totals[selected_cancer] * 100,1)}%")
k3.metric("% Used in ≥1 Project", f"{round(project_cases / base_totals[selected_cancer] * 100,1)}%")

# -----------------------
# Gene Distribution Chart
# -----------------------

gene_summary = filtered_df.groupby("Gene")["Cases"].sum().reset_index()

fig1 = px.bar(
    gene_summary,
    x="Gene",
    y="Cases",
    title="Germline Gene Distribution",
)

st.plotly_chart(fig1, use_container_width=True)

# -----------------------
# Project Utilization Chart
# -----------------------

project_summary = filtered_df.groupby("Project")["Cases"].sum().reset_index()

fig2 = px.bar(
    project_summary,
    x="Project",
    y="Cases",
    title="Project Utilization Distribution"
)

st.plotly_chart(fig2, use_container_width=True)