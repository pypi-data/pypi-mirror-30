# coding=utf-8
""""
    Most Popular Collaborative Filtering Recommender
    [Item Recommendation (Ranking)]

    Most Popular predicts a user’s ranking based on popularity of user and items.

"""

# © 2018. Case Recommender (MIT License)

from caserec.recommenders.item_recommendation.base_item_recommendation import BaseItemRecommendation
from caserec.utils.extra_functions import timed

__author__ = 'Arthur Fortes <fortes.arthur@gmail.com>'


class MostPopular(BaseItemRecommendation):
    def __init__(self, train_file=None, test_file=None, output_file=None, as_binary=False, rank_length=10, sep='\t',
                 output_sep='\t'):
        """
        Most Popular for Item Recommendation

        This algorithm predicts a rank for each user using the count of number of feedback of users and items

        Usage::

            >> MostPopular(train, test).compute()
            >> MostPopular(train, test, as_binary=True).compute()

        :param train_file: File which contains the train set. This file needs to have at least 3 columns
        (user item feedback_value).
        :type train_file: str

        :param test_file: File which contains the test set. This file needs to have at least 3 columns
        (user item feedback_value).
        :type test_file: str, default None

        :param output_file: File with dir to write the final predictions
        :type output_file: str, default None

        :param rank_length: Size of the rank that must be generated by the predictions of the recommender algorithm
        :type rank_length: int, default 10

        :param as_binary: If True, the explicit feedback will be transform to binary
        :type as_binary: bool, default False

        :param sep: Delimiter for input files
        :type sep: str, default '\t'

        :param output_sep: Delimiter for output file
        :type output_sep: str, default '\t'

        """

        super(MostPopular, self).__init__(train_file=train_file, test_file=test_file, output_file=output_file,
                                          as_binary=as_binary, rank_length=rank_length, sep=sep, output_sep=output_sep)

        self.recommender_name = 'Most Popular'

    def predict(self):
        """
            This method predict final result, building an rank of each user of the train set.

        """

        for user in set(self.users):
            predictions = list()

            for item in self.train_set['items_unobserved'].get(user, []):

                if self.as_binary:
                    predictions.append((user, item, len(self.train_set['users_viewed_item'][item])))
                else:
                    count_value = 0
                    for user_v in self.train_set['users_viewed_item'][item]:
                        count_value += self.train_set['feedback'][user_v][item]
                    predictions.append((user, item, count_value))

            predictions = sorted(predictions, key=lambda x: -x[2])
            self.ranking += predictions[:self.rank_length]

    def compute(self, verbose=True, metrics=None, verbose_evaluation=True, as_table=False, table_sep='\t'):
        """
        Extends compute method from BaseItemRecommendation. Method to run recommender algorithm

        :param verbose: Print recommender and database information
        :type verbose: bool, default True

        :param metrics: List of evaluation measures
        :type metrics: list, default None

        :param verbose_evaluation: Print the evaluation results
        :type verbose_evaluation: bool, default True

        :param as_table: Print the evaluation results as table
        :type as_table: bool, default False

        :param table_sep: Delimiter for print results (only work with verbose=True and as_table=True)
        :type table_sep: str, default '\t'

        """

        super(MostPopular, self).compute(verbose=verbose)

        if verbose:
            print("prediction_time:: %4f sec" % timed(self.predict))
            print('\n')

        else:
            self.predict()

        self.write_ranking()

        if self.test_file is not None:
            self.evaluate(metrics, verbose_evaluation, as_table=as_table, table_sep=table_sep)
