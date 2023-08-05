import pandas as pd

def multiindex_col_ix(df, col):
    """Get the index into df.index.levels[] corresponding to a given "column
    name" in a multiindex."""
    return df.index.names.index(col)

def unique_vals_multiindex(df, col):
    """Get the "unique column values" in a multiindex "column"."""
    return df.index.levels[multiindex_col_ix(df, col)]

def df_update_using_cols_like_keys(df1, df2, cols, ignore_index=True):
    """Add the rows in df1 whose values in cols do not appear in df2 to df2.

    Loosely, update df1 with the values of df2 as if cols were the index,
    but treating each block of values in cols as a whole.

    WARNING: only works if df1/df2 have "no" index for now, i.e. ignore_index
    (as in original index) must be True.

    Performed by taking the multiindex dfN.set_index(cols), taking the set
    difference, then appending to a copy of df2 by indexing back into df1 with
    the result."""
    df_diff = df_dict_diff_cols_like_keys(df1, df2, cols, ignore_index)
    return df_diff.append(df2)

def df_dict_diff_cols_like_keys(df1, df2, cols, ignore_index=True):
    """Return 'dict' difference df1 \ df2 using values in cols as the 'keys',
    but treat the non-unique keys as a single unit each."""
    if not ignore_index:
        raise NotImplementedError('only ignore_index=True is allowed.')
    df1_indexed = df1.set_index(cols)
    df2_indexed = df2.set_index(cols)
    diff_index = df1_indexed.index.difference(df2_indexed.index)

    new_df = [df1_indexed.loc[[idx]].reset_index() for idx in diff_index]
    # explicitly include initial object of append in case new_df ends up empty
    new_df.append(pd.DataFrame(index=[], columns=df2.columns))
    return pd.concat(new_df, ignore_index=True)



