import os, pickle

with open(os.getcwd() + '\\database\\dataset_faces.dat', 'rb') as f:
    A = pickle.load(f)

print(A)