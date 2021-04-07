from tqdm import tqdm  # type: ignore


def compare_dicts(dict_1, dict_2):
    assert type(dict_1) == type(dict_2), f"different types: {dict_1}, {dict_2}"

    if isinstance(dict_1, dict):
        assert set(dict_1.keys()) == set(
            dict_2.keys()
        ), f"{set(dict_1.keys()).symmetric_difference(set(dict_2.keys()))}"
        for k in dict_1.keys():
            try:
                compare_dicts(dict_2[k], dict_1[k])
            except Exception as e:
                print(e)
                raise KeyError(f"mismatch on key {k}")
    elif isinstance(dict_1, list):
        assert len(dict_1) == len(
            dict_2
        ), f"different lengths of lists, {len(dict_1)} {len(dict_2)}"
        for entry_1, entry_2 in zip(dict_1, dict_2):
            compare_dicts(entry_1, entry_2)
    else:
        assert dict_1 == dict_2, f"objects dont match {dict_1} {dict_2}"


def sort_prices(df):
    """
    sorts prices in price_i columns
    """
    sorted_price_columns = sorted(
        [c for c in df.columns if c.startswith("price_")], key=lambda x: int(x[6:])
    )
    other_columns = [c for c in df.columns if c not in sorted_price_columns]
    df = df[other_columns + sorted_price_columns]

    for idx in tqdm(range(len(df))):
        df.loc[idx, sorted_price_columns] = (
            df.loc[idx, sorted_price_columns].sort_values().values
        )

    return df
