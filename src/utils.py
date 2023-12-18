'''

    utils.py

    Some standard util functions

'''

import pandas as pd

def strip_xx_from_node(
        nodes : pd.Series,
) -> pd.Series:
    return nodes.str.replace('-XX','')