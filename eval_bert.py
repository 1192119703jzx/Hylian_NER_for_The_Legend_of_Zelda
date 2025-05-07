import json
from mention import Mention, decode_bio
from score import ScoringCounts, score_mentions

def calculation_matrix(reference_labels, predict_labels):
    reference = decode_bio(reference_labels)
    predict = decode_bio(predict_labels)
    matrix = score_mentions(reference, predict)
    return matrix, reference, predict

DATA_PATH = 'test_with_preds.jsonl'
instances = list(map(json.loads, open(DATA_PATH)))

TP = FP = FN = 0
output_list = []
for instance in instances:
    ref = instance['gold']
    pred = instance['pred']
    pred = pred[1:len(ref)]

    matrix, reference, predict = calculation_matrix(ref, pred)
    TP += matrix[0]
    FP += matrix[1]
    FN += matrix[2]
    output_list.append({
        'reference': reference,
        'predict': predict,
        'TP': matrix[0],
        'FP': matrix[1],
        'FN': matrix[2]
    })

print(f'TP: {TP}, FP: {FP}, FN: {FN}')
precision = TP / (TP + FP) if (TP + FP) > 0 else 0
recall = TP / (TP + FN) if (TP + FN) > 0 else 0
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

print(f'Precision: {precision}, Recall: {recall}, F1: {f1}')

with open('test_out.jsonl', 'w') as f:
    for output in output_list:
        f.write(json.dumps(output, indent=4) + '\n')