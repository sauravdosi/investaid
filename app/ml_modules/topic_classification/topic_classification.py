from transformers import pipeline

classifier = pipeline("zero-shot-classification")
sequence = "Bring back the old model, the new model sucks"
candidate_labels = ["company growth", "user feedback", "sale", "market position", "business expanse", "other"]

print(classifier(sequence, candidate_labels, multi_class=True))

sequence = "The company's new product feels okay. Not good, not bad."
candidate_labels = ["positive", "neutral", "negative"]

print(classifier(sequence, candidate_labels, multi_class=False))