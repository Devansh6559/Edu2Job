import pickle

with open("label_encoder.pkl", "rb") as f:
    obj = pickle.load(f)

print(type(obj))
