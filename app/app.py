import streamlit as st
import pandas as pd
import requests
import os

st.set_page_config(layout="wide", page_title='AI pharmacogenetics', page_icon=':pill:', initial_sidebar_state='expanded')

root = "https://raw.githubusercontent.com/ersilia-os/pharmacogx-embeddings/main"
data_dir = root + "/data"
results_dir = root + "/results"

all_results_file = results_dir + "/results_pairs/chemical_gene_pairs_prediction_output_focus_with_variant_aggregates.csv"
z95_results_file = results_dir + "/results_pairs/chemical_gene_pairs_prediction_output_focus_with_variant_aggregates_zscore95_filter.csv"
t50_results_file = results_dir + "/results_pairs/chemical_gene_pairs_prediction_output_focus_with_variant_aggregates_top50_filter.csv"

st.sidebar.title(':robot_face: Predicted PGx drug-gene interactions :pill:')
st.sidebar.write('This web application is a demonstration of the AI-based prediction of pharmacogenetic drug-gene interactions.')

st.sidebar.warning("This is a demo application used for research purposes only. The predictions are based on extensive use of machine learning and AI models, including large-language models. The predictions are not validated and should not be used for clinical decision-making.")

@st.cache_data
def load_chemical_cid_name_mapping():
    df = pd.read_csv(all_results_file)
    drugs = []
    for r in df[["cid", "chemical"]].values:
        drugs += [(r[0], r[1].capitalize())]
    cid2name = dict((r[0], r[1]) for r in drugs)
    return cid2name

@st.cache_data
def load_gene_gid_name_mapping():
    df = pd.read_csv(all_results_file)
    genes = []
    for r in df[["gid", "gene"]].values:
        genes += [(r[0], r[1])]
    gid2name = dict((r[0], r[1]) for r in genes)
    return gid2name

@st.cache_data
def load_results_data():
    df = pd.read_csv(t50_results_file)
    return df

def read_file_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None

def read_drug_tldr(cid):
    tldr_file = data_dir + "/tldr/drugs/{0}.md".format(cid)
    text = read_file_from_url(tldr_file)
    if text is None:
        return "No TLDR drug information available"
    else:
        return text.replace("\n\n", "\n").replace("## ", "### ")

def read_gene_tldr(gid):
    tldr_file = data_dir + "/tldr/gene/{0}.md".format(gid)
    text = read_file_from_url(tldr_file)
    if text is None:
        return "No TLDR gene information available"
    else:
        return text.replace("\n\n", "\n").replace("## ", "### ")
    
def read_top10_llm_genes(cid):
    chemical_name = cid2name[cid]
    results_file = results_dir + "/results_pairs/reranking/responses/{0}.md".format(chemical_name)
    print(results_file)
    text = read_file_from_url(results_file)
    if text is None:
        return "No LLM gene information available"
    else:
        return text.replace("\n\n", "\n").replace("## ", "### ")

df = load_results_data()

cid2name = load_chemical_cid_name_mapping()
name2cid = dict((v, k) for k, v in cid2name.items())
gid2name = load_gene_gid_name_mapping()
name2gid = dict((v, k) for k, v in gid2name.items())

sel_chemical = st.sidebar.selectbox('Select a chemical', sorted(cid2name.values()))
sel_cid = name2cid[sel_chemical]

ds = df[df["cid"] == sel_cid]

view = st.sidebar.radio('View predicted pharmacogenes', ['Top 10 genes according to LLMs', 'Top 50 according to embedding-based search', 'Results table'])

if view == "Top 10 genes according to LLMs":
    st.markdown(read_top10_llm_genes(sel_cid))

elif view == "Top 50 according to embedding-based search":
    pass

else:
    st.title("{0}".format(sel_chemical))
    st.write("Predicted pharmacogenes, tabular view")
    st.dataframe(ds, height=1000)


drug_tldr = read_drug_tldr(sel_cid)

st.sidebar.header("Prior TLDR drug information")
st.sidebar.markdown(drug_tldr)

st.sidebar.title(":information_desk_person: About")
st.sidebar.write("This web application has been developed by the [Ersilia Open Source Initiative](https://ersilia.io) in collaboration with the [H3D Center](https://h3d.uct.ac.za/).")
st.sidebar.write("For more information, please visit our [GitHub repository](https://github.com/pharmacogx-embeddings)")