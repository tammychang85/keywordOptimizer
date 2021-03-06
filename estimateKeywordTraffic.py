# -*- coding: utf-8 -*-

#!/usr/bin/env python
#
# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This example retrieves keyword traffic estimates.

The LoadFromStorage method is pulling credentials and properties from a
"googleads.yaml" file. By default, it looks for this file in your home
directory. For more information, see the "Caching authentication information"
section of our README.

"""
import _locale
from googleads import adwords


_locale._getdefaultlocale = (lambda *args: ['en_US', 'UTF-8'])


def _CalculateMean(min_est, max_est):
    if min_est and max_est:
        return (float(min_est) + float(max_est)) / 2.0
    else:
        return None


def _FormatMean(mean):
    if mean:
        return '%.2f' % mean
    else:
        return 'N/A'


def getTraffics(min_estimate, max_estimate, scoreMode):
    """
    seperate estimated daily clicks and impressions form the results of requests.

    Args:
    min_estimate: zeep.objects.StatsEstimate containing a minimum estimate from the
    TrafficEstimatorService response.
    max_estimate: zeep.objects.StatsEstimate containing a maximum estimate from the
    TrafficEstimatorService response.
    """
    # Find the mean of the min and max values.
    # mean_avg_cpc = (_CalculateMean(min_estimate['averageCpc']['microAmount'],
    #                                max_estimate['averageCpc']['microAmount'])
    #                 if 'averageCpc' in min_estimate
    #                 and min_estimate['averageCpc'] else None)
    # mean_avg_pos = (_CalculateMean(min_estimate['averagePosition'],
    #                                max_estimate['averagePosition'])
    #                 if 'averagePosition' in min_estimate
    #                 and min_estimate['averagePosition'] else None)
    # mean_total_cost = _CalculateMean(min_estimate['totalCost']['microAmount'],
    #                                  max_estimate['totalCost']['microAmount'])

    if scoreMode == 0:
        clickThroughRate = _CalculateMean(min_estimate['clickThroughRate'],
                                          max_estimate['clickThroughRate'])
        return clickThroughRate
    elif scoreMode == 1:
        meanClicks = _CalculateMean(min_estimate['clicksPerDay'],
                                    max_estimate['clicksPerDay'])
        return meanClicks
    elif scoreMode == 2:
        meanImpression = _CalculateMean(min_estimate['impressionsPerDay'],
                                        max_estimate['impressionsPerDay'])
        return meanImpression
    else:
        meanClicks = _CalculateMean(min_estimate['clicksPerDay'],
                                    max_estimate['clicksPerDay'])
        meanImpression = _CalculateMean(min_estimate['impressionsPerDay'],
                                        max_estimate['impressionsPerDay'])
        return (meanClicks, meanImpression)



def getEstimations(client, targetKewords, scoreMode):
    # Initialize appropriate service.
    traffic_estimator_service = client.GetService('TrafficEstimatorService',
                                                  version='v201809')

    # Construct selector object and retrieve traffic estimates.
    keywords = targetKewords
    keyword_estimate_requests = []
    for keyword in keywords:
        keyword_estimate_requests.append({'keyword':
                                          {'xsi_type': 'Keyword',
                                           'matchType': keyword['matchType'],
                                           'text': keyword['text']}})

    # negative_keywords = [
    #     {'text': 'moon walk', 'matchType': 'BROAD'}
    # ]
    # for keyword in negative_keywords:
    #   keyword_estimate_requests.append({
    #       'keyword': {
    #           'xsi_type': 'Keyword',
    #           'matchType': keyword['matchType'],
    #           'text': keyword['text']
    #       },
    #       'isNegative': 'true'
    #   })

    # Create ad group estimate requests.
    adgroup_estimate_requests = [{
      'keywordEstimateRequests': keyword_estimate_requests,
      'maxCpc': {
          'xsi_type': 'Money',
          'microAmount': '1000000'
      }
  }]

    # Create campaign estimate requests.
    campaign_estimate_requests = [{
        'adGroupEstimateRequests': adgroup_estimate_requests,
        'criteria': [
            {
                'xsi_type': 'Location',
                'id': '2840'  # United States.
            },
            {
                'xsi_type': 'Language',
                'id': '1000'  # English.
            }],
  }]

    # Create the selector.
    selector = {'campaignEstimateRequests': campaign_estimate_requests,}

    # Get traffic estimates.
    estimates = traffic_estimator_service.get(selector)
    campaign_estimate = estimates['campaignEstimates'][0]

    # record the keyword estimates.
    estimationList = []
    if 'adGroupEstimates' in campaign_estimate:
        ad_group_estimate = campaign_estimate['adGroupEstimates'][0]
        if 'keywordEstimates' in ad_group_estimate:
            keyword_estimates = ad_group_estimate['keywordEstimates']
            keyword_estimates_and_requests = zip(keyword_estimates,
                                                 keyword_estimate_requests)

        for keyword_tuple in keyword_estimates_and_requests:
            if keyword_tuple[1].get('isNegative', False):
                continue
            keyword = keyword_tuple[1]['keyword']
            keyword_estimate = keyword_tuple[0]

            if scoreMode == 0:
                clickThroughRate = getTraffics(
                    keyword_estimate['min'], keyword_estimate['max'], scoreMode)
                estimationList.append({'text': keyword['text'],
                                       'clickThroughRate': clickThroughRate})
            elif scoreMode == 1:
                click = getTraffics(
                    keyword_estimate['min'], keyword_estimate['max'], scoreMode)
                estimationList.append({'text': keyword['text'], 'click': click})
            elif scoreMode == 2:
                impression = getTraffics(
                    keyword_estimate['min'], keyword_estimate['max'], scoreMode)
                estimationList.append({'text': keyword['text'],
                                       'impression': impression})
            else:
                click, impression = getTraffics(
                    keyword_estimate['min'], keyword_estimate['max'], scoreMode)

                estimationList.append({'text': keyword['text'], 'click': click,
                                       'impression': impression})

    return estimationList


def run(targetKewords, scoreMode):
    estimations = getEstimations(adwords.AdWordsClient.LoadFromStorage(),
                                 targetKewords, scoreMode)
    return estimations

if __name__ == '__main__':
    keywordRequests = []
    for eachKeyword in ['apples', 'ornage']:
        keywordRequests.append({'text': eachKeyword, 'matchType':'EXACT'})
    print(run(keywordRequests, 3))
