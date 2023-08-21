import pandas as pd
from rouge_score import rouge_scorer

"""
rougebench.py
used after loader.py and examine.py, pass through each row for rouge score and saved in {dataset name}result.xlsx
"""


def write_result(path, ref_col_name):
    # default to include for rouge metrics, delete relevant lines if unnecessary
    data = pd.read_excel(path, engine='openpyxl')
    data['Rouge1score'] = ""
    data['Rouge2score'] = ""
    data['RougeLscore'] = ""
    data['RougeLsumscore'] = ""
    for index in range(len(data)):
        reference = data.loc[index, ref_col_name]
        summary = data.loc[index, 'Summary']
        # summary of cnn stories may result in sensitive content, ignoring Nan rows
        if not pd.isna(summary):
            scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL', 'rougeLsum'], use_stemmer=True)
            scores = scorer.score(reference, summary)
            data.loc[index, 'Rouge1score'] = scores['rouge1'].precision
            data.loc[index, 'Rouge2score'] = scores['rouge2'].precision
            data.loc[index, 'RougeLscore'] = scores['rougeL'].precision
            data.loc[index, 'RougeLsumscore'] = scores['rougeLsum'].precision
    data.to_excel(path, index=False, engine='openpyxl')


# write rouge result to examined result file, specify generated column
# reference column of different dataset specified, pubmed as Abstract; cnnstories as Highlight
write_result("data/pubmedresult.xlsx", "Abstract")
# write_result("data/cnnresult.xlsx", "Highlight")
