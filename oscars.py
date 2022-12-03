#!/usr/bin/python
# Copyright (c) 2022 Warren Usui
# This code is licensed under the MIT license (see LICENSE for details)
"""
Scrape the Academy Awards Website
"""
import json
import requests
from bs4 import NavigableString, BeautifulSoup

def get_url_io(year):
    """ Read the site for a given year (year of ceremony) """
    return requests.get(
            f"https://www.oscars.org/oscars/ceremonies/{year}").text

def get_soup(year):
    """ Is it soup yet? """
    return BeautifulSoup(get_url_io(year), "html.parser")

def get_pg_parts(year):
    """ Limit to fields we are interested in """
    return get_soup(year).find_all("div", class_="view-content")

def win_and_nom(split_loc):
    """ Main extraction and formatting code """
    def get_str(info):
        """ Curry input and pass 0 for winner, 1 for nominee """
        def inner_get(indx):
            """ Handle missing fields """
            if len(info[indx]) == 2:
                return "---"
            return info[indx][1].strip()
        return inner_get

    def make_dict_entry(info):
        """ Set up dictionary entry return of person and film info """
        return {get_str(info)(0): get_str(info)(1)}

    def find_fields(info):
        """ Scan for actor and title """
        return info.find_all("div", class_=["views-field-field-actor-name",
                                            "views-field-title"])
    def map_records(info):
        """ """
        return make_dict_entry(list(map(lambda a : list(a.strings),
                                        find_fields(info))))

    def make_records(info):
        """ pass info on (useful because this is called in three places) """
        return list(map(map_records, info))

    def inner_winnom(info):
        """ Return dict entry, accounting for no nominee awards """
        if split_loc == 0:
            return {"Winner": make_records(info[1:])}
        return {"Winner": make_records(info[1:split_loc]),
                "Nominees": make_records(info[split_loc + 1:])}
    return inner_winnom

def splt_func(ninfo):
    """ Return nominee index """
    if ninfo[1].contents[0] == 'Nominees':
        return ninfo[0]
    return 0

def splitter(info):
    """ Find index of Nominees inside list of awards in a category """
    return sum(list(map(splt_func, list(enumerate(info)))))

def wn_wrap(f_data):
    """ Wrap winners and nominees splitting code """
    return win_and_nom(splitter(f_data))(f_data)

def get_titlev(category):
    """ Find the category name """
    return [category.find_all("div",
                               class_="view-grouping-header")[0].string][0]

def extract_info(category):
    """ Remove unusable data extracted """
    return list(filter(lambda a : not isinstance(a, NavigableString),
                category.contents[1].contents))

def parse_info(category):
    """ Return category name and all the extracted info for that category """
    return {get_titlev(category): wn_wrap(extract_info(category))}

def get_cat_list(year):
    """ Extract list of categories for this year """
    return get_pg_parts(year)[1].find_all("div", class_="view-grouping")

def get_results(year):
    """ Handle results for a given year """
    print(year)
    return {year: list(map(parse_info, list(get_cat_list(year))))}

def get_awards():
    """ Effectively loop through all years """
    return list(map(get_results, list(range(1929, 2023))))

def get_awards_io():
    """ Write data to file """
    with open("academy_awards.json", "w", encoding='utf8') as outfile:
        outfile.write(json.dumps(get_awards(), indent=4, ensure_ascii=False))

if __name__ == "__main__":
    get_awards_io()
