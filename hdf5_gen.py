import pandas as pd
import numpy as np

if __name__ == "__main__":
    hdf = pd.HDFStore("test2.h5")
    data = {"x": [], "y": [], "k": []}
    for k in range(5, 10):
        for i in range(10000):
            data["x"].append(i)
            data["k"].append(k)
            data["y"].append(i**(1/k))
    df = pd.DataFrame(data)
    hdf.put("groupby", df)