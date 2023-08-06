#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import warnings

from sklearn.utils.validation import check_consistent_length

from mdesc.utils import utils as wb_utils


class CheckInputs(object):
    @staticmethod
    def is_regression(modelobj):
        """
        determined whether users modelobj is regression or classification based on
        presence of predict_proba

        :param modelobj: sklearn model object
        :return: sklearn predict method, str classification type
        :rtype: sklearn predict, str
        """
        # determine if in classification problem or regression problem
        if hasattr(modelobj, 'predict_proba'):
            # if classification setting, secure the predicted class probabilities
            predict_engine = getattr(modelobj, 'predict_proba')
            model_type = 'classification'
        else:
            # use the regular predict function
            predict_engine = getattr(modelobj, 'predict')
            model_type = 'regression'
        return predict_engine, model_type

    @staticmethod
    def check_keepfeaturelist(keepfeaturelist,
                              cat_df):
        """
        check user defined featuredict - if blank assign all dataframe columns

        :param keepfeaturelist: user defined featurelist
        :param cat_df: dataframe
        :return: validated keepfeaturelist
        :rtype: list
        """
        # keepfeaturelist blank
        if not keepfeaturelist:
            keepfeaturelist = cat_df.columns.values.tolist()
        else:
            if not all([feature in cat_df.columns for feature in keepfeaturelist]):
                # identify missing keys
                missing = list(set(keepfeaturelist).difference(set(cat_df.columns)))
                raise ValueError(wb_utils.ErrorWarningMsgs.error_msgs['keepfeaturelist'].format(missing))
        return keepfeaturelist

    @staticmethod
    def check_agg_func(aggregate_func):
        """
        check user defined aggregate function returns scalar when
        passed a list

        :param aggregate_func: user defined aggregate function
        :return: validated aggregate_func
        :rtype: func
        """

        try:
            agg_results = aggregate_func(list(range(100)))
            if hasattr(agg_results, '__len__'):
                raise ValueError("""aggregate_func must return scalar""")
        except Exception as e:
            raise TypeError(wb_utils.ErrorWarningMsgs.error_msgs['agg_func'].format(e))

    @staticmethod
    def check_cat_df(cat_df, model_df):
        """
        ensure validity of assigned cat_df - must have same length and
         index of model_df. If cat_df None, replaced by model_df

        :param cat_df: user defined cat_df
        :param model_df: user defined dataframe used to build model
        :return: validated cat_df
        :rtype: pd.DataFrame
        """
        # if cat_df not assigned, use model_df
        if cat_df is None:
            warnings.warn(wb_utils.ErrorWarningMsgs.warning_msgs['cat_df'])
            cat_df = model_df.copy(deep=True)
        else:
            cat_df = cat_df.copy(deep=True).reset_index(drop=True)
            # check both model_df and cat_df have the same length
            check_consistent_length(cat_df, model_df)
            # check index's are equal
            if not all(cat_df.index == model_df.index):
                raise ValueError("""Indices of cat_df and model_df are not aligned. Ensure Index's are 
                                            \nexactly the same before WhiteBox use.""")
            # reset users index in case of multi index or otherwise

        # finally check is any missing values exist and are untreated
        missing = cat_df.isnull().sum()
        # pull col names and count of missing values for columns that have missing
        missing = missing[missing > 0].to_dict()
        if len(missing) > 0:
            raise ValueError("""cat_df has missing values - resolve missing values for columns: {}""".format(missing))

        return cat_df

    @staticmethod
    def check_modelobj(modelobject):
        """
        check user defined model object has been fit before use

        :param modelobject: user defined model object
        :return: validated modelobj
        :rtype: sklearn model
        """
        # basic parameter checks
        if not hasattr(modelobject, 'predict'):
            raise ValueError(wb_utils.ErrorWarningMsgs.error_msgs['modelobj'])
