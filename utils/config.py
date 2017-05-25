import numpy as np
import pandas as pd

class Config():
    """
    Set some configuration parameters for toy funnel
    """

    def __init__(self):
        """
        Initialize class
        """

        # File to save results
        self.file_results = './results.txt'

        # Specifications for how to generate simulated customer data
        # *** For real data, this section could be removed and replaced with (non-sensitive)
        #     information about how to grab the data.  Sensitive information would be loaded
        #     here from an env-file not commited to the git repo, for example ***
        self.funnel_stages = pd.Categorical(['Open',
                                             'Click',
                                             'AddToCart',
                                             'EnterPayment',
                                             'Purchase'], ordered=True)
        self.funnel_params = pd.DataFrame(columns=['group', 'funnel_rates'])
        fstages = {
            'Open': 0.25,
            'Click': 0.18,
            'AddToCart': 0.10,
            'EnterPayment': 0.2,
            'Purchase': 0.5
        }
        self.funnel_params.loc[0] = ['Mobile', fstages]
        fstages = {
            'Open': 0.30,
            'Click': 0.35,
            'AddToCart': 0.05,
            'EnterPayment': 0.4,
            'Purchase': 0.45
        }
        self.funnel_params.loc[1] = ['Tablet', fstages]
        fstages = {
            'Open': 0.15,
            'Click': 0.40,
            'AddToCart': 0.05,
            'EnterPayment': 0.5,
            'Purchase': 0.6
        }
        self.funnel_params.loc[2] = ['Desktop', fstages]

        # Number of customers to simulate for each group
        self.num_customers = {
            'Mobile': 10000,
            'Tablet': 5000,
            'Desktop': 7000
        }


