import sys
import json
import logging
from pprint import pprint
import traceback
import numpy as np
import pandas as pd

sys.path.append('./')
from utils.config import Config
from utils.errors import Errors


logging.basicConfig(level=logging.DEBUG,
                          format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


class ToyFunnel():
    """
    Simulate data of customers traveling through the funnel. 
    Generate some simple statistics.
    """

    def __init__(self):
        """
        Initialize class
        """

        # Initialize some stuff
        self._config = Config()
        self._error_generator = Errors()
        self._errors = []
        self._funnel_stages = None
        self._data = pd.DataFrame(columns=['customer_id', 'group', 'funnel_stages'])


        # Load customer data and analyze funnel
        try:
            self._load_customer_data()

            try:
                self._analyze_funnel_data()
            except:
                self._handle_exception(3000)

        except:
            self._handle_exception(2000)


        # Add any errors to the output file
        if len(self._errors) > 0:
            with open(self._config.file_results, 'a') as f:
                f.write('\n\nERRORS:\n')
                for err in self._errors:
                    f.write('{0}: {1}\n'.format(err['code'], err['text']))
                    if 'details' in err:
                        f.write(json.dumps(err['details']) + '\n')
                    if 'traceback' in err:
                        f.write(err['traceback'])
                    f.write('\n')


    def _handle_exception(self, code):
        """
        Handle exception nicely
        """

        logging.info('Terminating due to error')
        tb = traceback.format_exc()
        self._errors.append(self._error_generator.get_error(code, traceback=tb))


        return


    def _load_customer_data(self):
        """
        Load data about customer movement through the funnel
            *** Right now this data is being simulated, but this could be replaced by a
                function that loads in real customer data from a SQL database, for example ***
        """

        logging.info('Loading customer data')

        logging.info('   Simulating data (later could make this load real customer data)')

        self._funnel_stages = self._config.funnel_stages.copy()

        # Get a bunch of random numbers that you can use to determine movement through the funnel
        # Set the seed to get reproducible results
        logging.info('    Generating random numbers')
        np.random.seed(17)
        num_customers_total = sum(self._config.num_customers.values())
        num_stages = self._funnel_stages.shape[0]
        states = np.random.uniform(0, 1, (num_customers_total, num_stages))

        # Generate individual customer values
        logging.info('    Generating individual customer data')
        self._data['customer_id'] = range(num_customers_total)
        bins = [0] + list(np.cumsum(self._config.num_customers.values()))
        func = lambda x: self._config.funnel_params.loc[np.digitize(x, bins) - 1]['group']
        self._data['group'] = self._data['customer_id'].apply(func)
        func = lambda x: self._get_individual_funnel_status(x, states[x['customer_id'], :])
        self._data['funnel_stages'] = self._data.apply(func, axis=1)


        return


    def _get_individual_funnel_status(self, customer, states):
        """
        Get the state in the funnel for an individual customer
        *** Hmmm, there's probably a faster day to do this, think a little
            more carefully about how you're doing things here if speed
            becomes an issue ***

        customer = dataframe row for that customer
        states = state info for all groups for that customer
        """

        funnel_status = dict.fromkeys(self._funnel_stages, False)

        previous_status = True
        for istage, stage in enumerate(self._funnel_stages):
            if previous_status:
                ind = self._config.funnel_params['group'] == customer['group']
                rates = self._config.funnel_params[ind]['funnel_rates'].values
                if len(rates) != 1:
                    self._errors.append(self._error_generator.get_error(2010,
                        details={'num_matches': len(rates)}))
                    raise Exception('Forcing early termination because of error')
                else:
                    rate = rates[0][stage]
                current_status = states[istage] < rate
                funnel_status[stage] = current_status
                previous_status = current_status
            else:
                funnel_status[stage] = False


        return funnel_status


    def _analyze_funnel_data(self):
        """
        Analyze funnel data
        """

        logging.info('Analyzing funnel data')

        f = open(self._config.file_results, 'w')

        # Analyze each group
        for igroup, group in enumerate(self._config.funnel_params['group'].values):

            logging.info('    Processing group ({0}/{1}): {2}'.format(igroup + 1, \
                len(self._config.funnel_params['group'].values), group))
            f.write('-' * 80 + '\n')
            f.write('Group: {0}  (# Customers = {1})\n'.format(group,
                self._config.num_customers[group]))

            results = pd.DataFrame(columns=['# Total Customers Left',
                                            '% Total Customers Left',
                                            '% From Last Stage'])

            # Calculate metrics for each stage
            previous_number = self._config.num_customers[group]
            for istage, stage in enumerate(self._funnel_stages):
                func = lambda x: x['funnel_stages'][stage]
                values = self._data[self._data['group'] == group].apply(func, axis=1)
                num_total_customers_left = sum(values)

                if previous_number <= 0:
                    self._errors.append(self._error_generator.get_error(3010,
                        details={'group': group, 'stage': stage}))
                    perc_passed = None
                else:
                    perc_passed = (sum(values) / float(previous_number)) * 100

                perc_total_customers_left = \
                    (num_total_customers_left / float(self._config.num_customers[group])) * 100
                results.loc[stage] = [num_total_customers_left,
                                      perc_total_customers_left,
                                      perc_passed]
                previous_number = num_total_customers_left


            formatter = lambda x: ['{0:d}'.format(int(x['# Total Customers Left'])),
                                   '{0:.2f}'.format(x['% Total Customers Left']),
                                   '{0:.2f}'.format(x['% From Last Stage'])]
            pprint(results.apply(formatter, axis=1), stream=f)
            f.write('\n')


        f.close()


        return



if __name__ == '__main__':

    toy_funnel = ToyFunnel()




