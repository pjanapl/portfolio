import pickle

files = [
    "../data/products_data_0_1000.pickle",
    "../data/products_data_1001_2000.pickle",
    "../data/products_data_2001_3000.pickle",
    "../data/products_data_3001_3600.pickle",
]

output_file = '../data/products_data.pickle'

data = []

for file in files:
    with open(file, "rb") as f:
        data = data + pickle.load(f)

# Repair data
# Muszę się pozbyć tych zakresów:
# print(data[:17])
# print(data[1018:1035])
# print(data[2035:2052])
# print(data[3052:3069])
col_names = data[:17]
rest = data[17:1018] + data[1035:2035] + data[2052:3052] + data[3069:]
new = [col_names] + rest

with open(output_file, "wb") as f:
    pickle.dump(new, f)
