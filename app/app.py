import streamlit as st
import pandas as pd
import requests

st.set_page_config(layout="wide", page_title='AI pharmacogenetics', page_icon=':pill:', initial_sidebar_state='expanded')

st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"]{
        min-width: 500px;
        max-width: 1000px;
    }
    """,
    unsafe_allow_html=True,
)   


root = "https://raw.githubusercontent.com/ersilia-os/pharmacogx-embeddings/main"
data_dir = root + "/data"
results_dir = root + "/results"

all_results_file = results_dir + "/results_pairs/chemical_gene_pairs_prediction_output_focus_with_variant_aggregates.csv"
z95_results_file = results_dir + "/results_pairs/chemical_gene_pairs_prediction_output_focus_with_variant_aggregates_zscore95_filter.csv"
t50_results_file = results_dir + "/results_pairs/chemical_gene_pairs_prediction_output_focus_with_variant_aggregates_top50_filter.csv"
t10_results_file = results_dir + "/results_pairs/chemical_gene_pairs_prediction_output_focus_with_variant_aggregates_top50_filter_llm_top10.csv"

drug_tldrs_file = results_dir + "/results_pairs/cid_tldrs.csv"
gene_tldrs_file = results_dir + "/results_pairs/gid_tldrs.csv"

st.sidebar.title(':robot_face: Predicted PGx drug-gene interactions :pill:')
st.sidebar.write('This web application is a demonstration of the AI-based prediction of pharmacogenetic drug-gene interactions.')

st.sidebar.warning("This is a demo application used for research purposes only. The predictions are based on extensive use of machine learning and AI models, including large-language models. The predictions are not validated and should not be used for clinical decision-making.")

@st.cache_data
def load_chemical_cid_name_mapping():
    df = pd.read_csv(all_results_file)
    drugs = []
    for r in df[["cid", "chemical"]].values:
        drugs += [(r[0], r[1])]
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
    df = pd.read_csv(t10_results_file)
    return df

def read_file_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None
    
@st.cache_data
def load_drug_tldrs():
    df = pd.read_csv(drug_tldrs_file)
    cid2tldr = {}
    for r in df.values:
        cid2tldr[r[0]] = r[1]
    return cid2tldr

@st.cache_data
def load_gene_tldrs():
    df = pd.read_csv(gene_tldrs_file)
    gid2tldr = {}
    for r in df.values:
        gid2tldr[r[0]] = r[1]
    return gid2tldr

def get_top10_genes(df, cid):
    df_ = df[df["cid"] == cid]
    df_ = df_[df_["llm_rank"].notnull()]
    df_ = df_.sort_values(by="llm_rank")
    return df_.reset_index(drop=True)

def get_top50_genes(df, cid):
    df_ = df[df["cid"] == cid]
    df_ = df_.sort_values(by="consensus_zscore", ascending=False)
    return df_.reset_index(drop=True)

df = load_results_data()

cid2name = load_chemical_cid_name_mapping()
name2cid = dict((v, k) for k, v in cid2name.items())
gid2name = load_gene_gid_name_mapping()
name2gid = dict((v, k) for k, v in gid2name.items())
cid2tldr = load_drug_tldrs()
gid2tldr = load_gene_tldrs()

cap2name = {}
for n in cid2name.values():
    cap2name[n.capitalize()] = n

sel_chemical = st.sidebar.selectbox('Select a chemical', sorted(cap2name.keys()))
sel_cid = name2cid[cap2name[sel_chemical]]


def genes_layout(chemical, ds, has_explanation):
    cid = name2cid[cap2name[sel_chemical]]
    if cid[0] == cid[0].upper():
        st.title("[{0}](https://www.pharmgkb.org/chemical/{1})".format(chemical, cid))
    else:
        st.title(chemical)
    for d in ds.iterrows():
        rank = d[0] + 1
        r = d[1]
        
        if int(r["train_set"]) == 1:
            in_pgkb_str = ":blue[Yes]"
        else:
            in_pgkb_str = ":red[No]"

        st.header("`{0}` [{1}](https://www.pharmgkb.org/gene/{2})".format(str(rank).zfill(2), r["gene"], r["gid"]))
        cols = st.columns([1, 2, 2, 2])
        cols[0].markdown("- Consensus Z-score: `{0:.2f}`\n- In PharmGKB: {1}".format(r["consensus_zscore"], in_pgkb_str))
        
        # Variants
        col = cols[1]
        col.markdown("**Observed gene variants**")
        col_names = ["Total", "Intron", "Missense"]
        row_names = ["Worldwide", "Africa abundant", "Africa specific"]
        R = [
            [r["total_variants"], r["intron_variants"], r["missense_variants"]],
            [r["afr_abundant_variants"], r["afr_abundant_intron_variants"], r["afr_abundant_missense_variants"]],
            [r["afr_specific_variants"], r["afr_specific_intron_variants"], r["afr_specific_missense_variants"]]
        ]
        dv = pd.DataFrame(R, columns=col_names, index=row_names)
        col.dataframe(dv)

        # Explanation
        col = cols[-2]
        if has_explanation:
            if r["llm_expl"] is not None:
                col.markdown("**Explanation**: "+r["llm_expl"])
        else:
            col.markdown("**Scores per training set**")
            row_names = ["All genes & all outcomes", "All genes & PK outcomes", "ADME genes & PK outcomes"]
            col_names = ["Z-score", "Support"]
            R = [
                [r["y_hat_all_outcomes_all_genes_zscore"], r["support_all_outcomes_all_genes"]],
                [r["y_hat_only_pk_all_genes_zscore"], r["support_only_pk_all_genes"]],
                [r["y_hat_only_pk_only_adme_genes_zscore"], r["support_only_pk_only_adme_genes"]]
            ]
            dv = pd.DataFrame(R, columns=col_names, index=row_names)
            col.dataframe(dv)
        
        # Gene TLDR
        cols[-1].markdown("**Prior Gene TLDR**: "+gid2tldr[r["gid"]])

view = st.sidebar.radio('View predicted pharmacogenes', ['Top 10 genes according to LLMs', 'Top 50 according to embedding-based search', 'Results table'])

if view == "Top 10 genes according to LLMs":
    ds = get_top10_genes(df, sel_cid)
    genes_layout(sel_chemical, ds, has_explanation=True)

elif view == "Top 50 according to embedding-based search":
    ds = get_top50_genes(df, sel_cid)
    genes_layout(sel_chemical, ds, has_explanation=False)

else:
    st.title("{0}".format(sel_chemical))
    st.write("Predicted pharmacogenes, tabular view")
    ds = df[df["cid"] == sel_cid]
    st.dataframe(ds, height=1000)

st.sidebar.header("Prior TLDR drug information")
st.sidebar.markdown(cid2tldr[sel_cid])

@st.cache_data
def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

csv = convert_df(df)

st.sidebar.title(":arrow_down_small: Get the data")
st.sidebar.write("You can download the main predictions data used in this application in CSV format")
st.sidebar.download_button(
   "Download PGx predictions",
   csv,
   "pharmacogx_predictions.csv",
   "text/csv",
   key='download-csv'
)

st.sidebar.title(":information_desk_person: About")
st.sidebar.write("This web application has been developed by the [Ersilia Open Source Initiative](https://ersilia.io) in collaboration with the [H3D Center](https://h3d.uct.ac.za/).")
st.sidebar.write("For more information, please visit our [GitHub repository](https://github.com/pharmacogx-embeddings)")