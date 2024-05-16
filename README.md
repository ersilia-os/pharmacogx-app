# Browse AI-Based Pharmacogenomics Predictions Relevant to African Populations
This application provides a user-friendly interface to explore pharmacogenomics predictions, with a particular focus on data relevant to Africa.

## Project Overview
This project is a collaboration between the [Ersilia Open Source Initiative](https://ersilia.io) and the [H3D Center](https://h3d.uct.ac.za/). The primary objective is to identify genes that could potentially influence drug responses. We wrote about this in a comment in Nature: [Turon et al, 2024](https://www.nature.com/articles/d41586-024-01001-y).

For a more comprehensive understanding of the project, please visit [pharmacogx-embeddings](https://github.com/ersilia-os/pharmacogx-embeddings), the central GitHub repository of the project.

This application provides a straightforward way to explore predictions derived from a combination of embedding-based drug-gene ranking and GPT-4 assisted re-ranking. For each drug, we offer 10 high-quality prioritized genes and 40 additional predictions of lower confidence.

## How to Use
To use this application, you first need to install the necessary dependencies. You can do this by running the following command in your terminal:
```bash
pip install -r requirements.txt
```
Once the dependencies are installed, you can start the application using Streamlit with the following command:

```bash
streamlit run app/app.py
```
## Online Demo
For those who prefer not to install the application locally, we provide an online demo that you can access here: https://example.com

## Disclaimer
Please be aware that the data presented in this application is the result of extensive use of machine learning and AI models. While we strive for accuracy, the results are intended for research purposes only. They should not be used to inform clinical decision-making without further validation.

## About
Learn more about the [Ersilia Open Source Initiative](https://ersilia.io) in the [Ersilia GitHub profile](https://github.com/ersilia). Ersilia is a non-profit organization aimed at supporting infectious disease research in the Global South.
