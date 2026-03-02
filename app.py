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
st.caption("Simulated aggregate dataset for feasibility exploration only.")

np.random.seed(42)

# -----------------------
# Core Definitions
# -----------------------

cancers = ["Breast", "Ovarian", "Prostate", "Colon"]
genes = ["BRCA1", "BRCA2", "TP53", "PALB2", "CHEK2", "ATM"]

project_categories = [
    "None",
    "WGS Project A (contact info)",
    "WES Project B (contact info)",
    "SNP Project C (contact info)",
    "WGS Project A (contact info) + WES Project B (contact info)",
    "WGS Project A (contact info) + SNP Project C (contact info)",
    "WES Project B (contact info) + SNP Project C (contact info)",
    "WGS Project A (contact info) + WES Project B (contact info) + SNP Project C (contact info)"
]

years = list(range(2010, 2026))

# -----------------------
# Base Totals
# -----------------------

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

# -----------------------
# Generate Sample Inventory (Aggregate)
# -----------------------

inventory_rows = []

for cancer in cancers:
    total_cases = base_totals[cancer]

    for year in years:

        # 20% pre-2015 are inaccessible
        if year < 2015:
            year_weight = 0.04  # spread across 5 years
            accessible = "No"
        else:
            year_weight = 0.08  # spread across 11 years
            accessible = "Yes"

        yearly_cases = int(total_cases * year_weight)

        pre_cases = int(yearly_cases * pre_cancer_rate[cancer])
        post_cases = yearly_cases - pre_cases

        for gene in genes:
            gene_fraction = np.random.uniform(0.05, 0.20)

            # Pre-cancer samples
            inventory_rows.append([
                cancer,
                year,
                accessible,
                "Yes",
                gene,
                int(pre_cases * gene_fraction)
            ])

            # Post-cancer samples
            inventory_rows.append([
                cancer,
                year,
                accessible,
                "No",
                gene,
                int(post_cases * gene_fraction)
            ])

inventory_df = pd.DataFrame(inventory_rows, columns=[
    "Cancer",
    "Year",
    "Accessible",
    "PreCancer",
    "Gene",
    "Cases"
])

# -----------------------
# Generate Project Mapping Table
# -----------------------

project_rows = []

for _, row in inventory_df.iterrows():

    # Only eligible samples
    if row["PreCancer"] == "Yes" and row["Accessible"] == "Yes":

        # Randomly decide if used in project (~60% used in at least one)
        if np.random.rand() < 0.6:

            selected_projects = np.random.choice(
                project_categories[1:],  # exclude "None"
                size=np.random.randint(1, 4),
                replace=False
            )

            for proj in selected_projects:
                project_rows.append([
                    row["Cancer"],
                    row["Year"],
                    row["Gene"],
                    proj,
                    int(row["Cases"] * np.random.uniform(0.3, 0.8))
                ])

project_df = pd.DataFrame(project_rows, columns=[
    "Cancer",
    "Year",
    "Gene",
    "Project",
    "Cases"
])

# -----------------------
# Dashboard Filters
# -----------------------

col1, col2, col3, col4 = st.columns(4)

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

with col4:
    year_range = st.slider(
        "Year Range",
        min(years),
        max(years),
        (2015, 2025)
    )

# -----------------------
# Apply Filters to Inventory
# -----------------------

filtered_inventory = inventory_df[
    (inventory_df["Cancer"] == selected_cancer) &
    (inventory_df["Year"] >= year_range[0]) &
    (inventory_df["Year"] <= year_range[1])
]

if pre_filter != "All":
    filtered_inventory = filtered_inventory[
        filtered_inventory["PreCancer"] == pre_filter
    ]

# -----------------------
# Apply Filters to Project Mapping
# -----------------------

filtered_projects = project_df[
    (project_df["Cancer"] == selected_cancer) &
    (project_df["Year"] >= year_range[0]) &
    (project_df["Year"] <= year_range[1])
]

if project_filter:
    filtered_projects = filtered_projects[
        filtered_projects["Project"].isin(project_filter)
    ]
else:
    filtered_projects = pd.DataFrame(columns=project_df.columns)

# -----------------------
# KPIs
# -----------------------

total_cases = filtered_inventory["Cases"].sum()
accessible_cases = filtered_inventory[filtered_inventory["Accessible"] == "Yes"]["Cases"].sum()

k1, k2, k3 = st.columns(3)
k1.metric("Total Cases (Filtered)", total_cases)
k2.metric("Accessible Cases", accessible_cases)
k3.metric("% Accessible", f"{round((accessible_cases / total_cases * 100),1) if total_cases > 0 else 0}%")

# -----------------------
# Gene Distribution Chart
# -----------------------

gene_summary = filtered_inventory.groupby("Gene")["Cases"].sum().reset_index()

fig1 = px.bar(
    gene_summary,
    x="Gene",
    y="Cases",
    title="Germline Gene Distribution"
)

st.plotly_chart(fig1, use_container_width=True)

# -----------------------
# Project Utilization Chart
# -----------------------

project_summary = filtered_projects.groupby("Project")["Cases"].sum().reset_index()

fig2 = px.bar(
    project_summary,
    x="Project",
    y="Cases",
    title="Project Utilization Distribution"
)

st.plotly_chart(fig2, use_container_width=True)

# -----------------------
# CSV Download
# -----------------------

st.download_button(
    label="Download Filtered Dataset (CSV)",
    data=filtered_inventory.to_csv(index=False),
    file_name="filtered_germline_feasibility_data.csv",
    mime="text/csv"
)