import pandas as pd



                },
    assert filtered_csv[0].path.exists()
    df = pd.read_csv(filtered_csv[0].path)


    assert filtered_csv[0].path.exists()
    assert filtered_csv[0].uftype == ".any.csv"
    df = pd.read_csv(filtered_csv[0].path)
    assert df.shape[0] == 2


    assert filtered_csv[0].path.exists()
    assert filtered_csv[0].uftype == ".any.csv"
    df = pd.read_csv(filtered_csv[0].path)