# -*- coding: utf-8 -*-

#!/usr/bin/env python
# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This example generates keyword ideas from a list of seed keywords."""


import argparse
import sys
import _locale
from google.ads.google_ads.client import GoogleAdsClient
from google.ads.google_ads.errors import GoogleAdsException


_locale._getdefaultlocale = (lambda *args: ['en_US', 'UTF-8'])



# Location IDs are listed here: https://developers.google.com/adwords/api/docs/appendix/geotargeting
# and they can also be retrieved using the GeoTargetConstantService as shown
# here: https://developers.google.com/google-ads/api/docs/targeting/location-targeting
_DEFAULT_LOCATION_IDS = ['1012825', '9040379']  # location ID for New Taipei and Taipei city (Max 10)
# A language criterion ID. For example, specify 1000 for English. For more
# information on determining this value, see the below link:
# https://developers.google.com/adwords/api/docs/appendix/codes-formats#languages.
_DEFAULT_LANGUAGE_ID = '1018'  # language ID for traditional chinese


def map_keywords_to_string_values(client, keywords):
    keyword_protos = []
    for keyword in keywords:
        string_val = client.get_type('StringValue')
        string_val.value = keyword
        keyword_protos.append(string_val)
    return keyword_protos


def map_locations_to_string_values(client, location_ids):
    gtc_service = client.get_service('GeoTargetConstantService', version='v3')
    locations = []
    for location_id in location_ids:
        location = client.get_type('StringValue')
        location.value = gtc_service.geo_target_constant_path(location_id)
        locations.append(location)
    return locations


def map_language_to_string_value(client, language_id):
    language = client.get_type('StringValue')
    language.value = client.get_service('LanguageConstantService',
                                        version='v3').language_constant_path(
                                            language_id)
    return language


def getKeywordIdeas(client, location_ids, language_id, customer_id,  keywords, page_url, moreInfo):
    keyword_plan_idea_service = client.get_service('KeywordPlanIdeaService',
                                                   version='v3')
    keyword_competition_level_enum = (
        client.get_type('KeywordPlanCompetitionLevelEnum', version='v3')
        .KeywordPlanCompetitionLevel)
    keyword_plan_network = client.get_type(
        'KeywordPlanNetworkEnum', version='v3').GOOGLE_SEARCH_AND_PARTNERS
    locations = map_locations_to_string_values(client, location_ids)
    language = map_language_to_string_value(client, language_id)

    # Only one of these values will be passed to the KeywordPlanIdeaService
    # depending on whether keywords, a page_url or both were given.
    url_seed = None
    keyword_seed = None
    keyword_url_seed = None

    # Either keywords or a page_url are required to generate keyword ideas
    # so this raises an error if neither are provided.
    if not (keywords or page_url):
        raise ValueError('At least one of keywords or page URL is required, '
                         'but neither was specified.')

    # To generate keyword ideas with only a page_url and no keywords we need
    # to initialize a UrlSeed object with the page_url as the "url" field.
    if not keywords and page_url:
        url_seed = client.get_type('UrlSeed', version='v3')
        url_seed.url.value = page_url


    # To generate keyword ideas with only a list of keywords and no page_url
    # we need to initialize a KeywordSeed object and set the "keywords" field
    # to be a list of StringValue objects.
    if keywords and not page_url:
        keyword_seed = client.get_type('KeywordSeed', version='v3')
        keyword_protos = map_keywords_to_string_values(client, keywords)
        keyword_seed.keywords.extend(keyword_protos)

    # To generate keyword ideas using both a list of keywords and a page_url we
    # need to initialize a KeywordAndUrlSeed object, setting both the "url" and
    # "keywords" fields.
    if keywords and page_url:
        keyword_url_seed = client.get_type('KeywordAndUrlSeed', version='v3')
        keyword_url_seed.url.value = page_url
        keyword_protos = map_keywords_to_string_values(client, keywords)
        keyword_url_seed.keywords.extend(keyword_protos)


    try:
        keyword_ideas = keyword_plan_idea_service.generate_keyword_ideas(
            customer_id, language, locations, keyword_plan_network,
            url_seed=url_seed, keyword_seed=keyword_seed,
            keyword_and_url_seed=keyword_url_seed)

        ideaList = [] # record keywords
        for idea in keyword_ideas.results:
            competition_value = keyword_competition_level_enum.Name(
                idea.keyword_idea_metrics.competition)

            # optional: idea.keyword_idea_metrics.avg_monthly_searches.value,
            # competition_value
            if moreInfo == 0:
                ideaList.append(idea.text.value)
            else:
                ideaList.append((idea.text.value,
                                 idea.keyword_idea_metrics.avg_monthly_searches.value,
                                 competition_value))

        return ideaList

    except GoogleAdsException as ex:
        print('Request with ID "{}" failed with status "{}" and includes the '
              'following errors:'.format(ex.request_id, ex.error.code().name))
        for error in ex.failure.errors:
            print('\tError with message "{}".'.format(error.message))
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print('\t\tOn field: {}'.format(
                        field_path_element.field_name))
        sys.exit(1)


def run(customer_id, targets, mode=0, moreInfo=0):
    # GoogleAdsClient will read the google-ads.yaml configuration file in the
    # home directory if none is specified.
    google_ads_client = GoogleAdsClient.load_from_storage()
    location_ids = _DEFAULT_LOCATION_IDS
    language_id = _DEFAULT_LANGUAGE_ID
    customer_id = customer_id
    # choos to use keywords file or url, 0:for file(default), 1:for url
    if mode ==0:
        keywords = targets
        page_url = None
    else:
        page_url =targets
        keywords = None

    keywordIdeas = getKeywordIdeas(google_ads_client, location_ids,
                                   language_id, customer_id, keywords,
                                   page_url, moreInfo)

    return keywordIdeas


if __name__ == '__main__':
    # GoogleAdsClient will read the google-ads.yaml configuration file in the
    # home directory if none is specified.
    google_ads_client = GoogleAdsClient.load_from_storage()
    location_ids = _DEFAULT_LOCATION_IDS
    language_id = _DEFAULT_LANGUAGE_ID
    customer_id = '3566761997'

    page_url = None
    keywords = ['SEO']
    moreInfo = 0
    keywordIdeas = getKeywordIdeas(google_ads_client, location_ids,
                                   language_id, customer_id, keywords,
                                   page_url, moreInfo)
    print(keywordIdeas)
