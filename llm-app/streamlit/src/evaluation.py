import pandas as pd

def hit_rate(relevance_total):

    cnt = 0
    for line in relevance_total:
        if True in line:
            cnt = cnt + 1

    return cnt/len(relevance_total)

def mrr(relevance_total):
    
    score=0
    for line in relevance_total:
        for rank in range(len(line)):
            if line[rank] == True:
                score = score + 1/(rank +1)

    return score/len(relevance_total)

def evaluate(search_function):
    
    ground_truth = pd.read_csv("streamlit/src/ground_truth/ground-truth-data.csv")
    ground_truth = ground_truth.to_dict(orient = "records")
    relevance_total = []

    for q in (ground_truth):
        doc_id = q['document']
        results = search_function(q)
        relevance = [d['doc_id'] == doc_id for d in results]
        relevance_total.append(relevance)
    
    return {
        "hit_rate":hit_rate(relevance_total),
        "mrr": mrr(relevance_total)
    }