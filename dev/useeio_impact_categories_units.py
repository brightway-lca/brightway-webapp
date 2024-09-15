# %%
import bw_graph_tools as bgt
import bw2io as bi
import bw2data as bd
import bw2calc as bc
import pandas as pd

import csv

if 'USEEIO-1.1' not in bd.projects:
    bi.install_project(project_key="USEEIO-1.1", overwrite_existing=True)
    bd.projects.set_current("USEEIO-1.1")
else:
    bd.projects.set_current("USEEIO-1.1")

useeio = bd.Database("USEEIO-1.1")


def generate_methods_objects():
    """
    dict_methods = {
        'HRSP': ('Impact Potential', 'HRSP'),
        'OZON': ('Impact Potential', 'OZON'),
        ...
    }
    """
    dict_methods = {i[-1]:[i] for i in bd.methods}

    """
    dict_method_names = {
        'HRSP': 'Human Health: Respiratory effects',
        'OZON': 'Ozone Depletion',
        ...
    }
    """
    # hardcoded for better Pyodide performance
    dict_methods_names = {
        "HRSP": "Human Health - Respiratory Effects",
        "OZON": "Ozone Depletion",
        "HNC": "Human Health Noncancer",
        "WATR": "Water",
        "METL": "Metals",
        "EUTR": "Eutrophication",
        "HTOX": "Human Health Cancer and Noncancer",
        "LAND": "Land",
        "NREN": "Nonrenewable Energy",
        "ETOX": "Freshwater Aquatic Ecotoxicity",
        "PEST": "Pesticides",
        "REN": "Renewable Energy",
        "MINE": "Minerals and Metals",
        "GCC": "Global Climate Change",
        "ACID": "Acid Rain",
        "HAPS": "Hazardous Air Pollutants",
        "HC": "Human Health Cancer",
        "SMOG": "Smog Formation",
        "ENRG": "Energy"
    }
    # path_impact_categories_names: str = '../app/_data/USEEIO_impact_categories_names.csv'
    # dict_methods_names = {}
    # with open(path_impact_categories_names, mode='r', newline='', encoding='utf-8-sig') as file:
    #    reader = csv.reader(file)
    #    dict_methods_names = {rows[0]: rows[1] for rows in reader}

    """
    dict_methods_units = {
        'HRSP': '[kg PM2.5 eq]',
        'OZON': '[kg O3 eq]',
        ...
    }
    """
    # hardcoded for better Pyodide performance
    dict_methods_units = {
        "HRSP": "[kg PM2.5 eq]",
        "OZON": "[kg O3 eq]",
        "HNC": "[CTUh]",
        "WATR": "[m3]",
        "METL": "[kg]",
        "EUTR": "[kg N eq]",
        "HTOX": "[CTUh]",
        "LAND": "[m2*yr]",
        "NREN": "[MJ]",
        "ETOX": "[CTUe]",
        "PEST": "[kg]",
        "REN": "[MJ]",
        "MINE": "[kg]",
        "GCC": "[kg CO2 eq]",
        "ACID": "[kg SO2 eq]",
        "HAPS": "[kg]",
        "HC": "[CTUh]",
        "SMOG": "[kg O3 eq]",
        "ENRG": "[MJ]"
    }
    # path_impact_categories_units: str = '../app/_data/USEEIO_impact_categories_units.csv'
    # dict_methods_units = {}
    # with open(path_impact_categories_units, mode='r', newline='', encoding='utf-8-sig') as file:
    #    reader = csv.reader(file)
    #    dict_methods_units = {rows[0]: str('[')+rows[1]+str(']') for rows in reader}

    """
    dict_methods_enriched = {
            'HRSP': [('Impact Potential', 'HRSP'), 'Human Health - Respiratory effects', '[kg PM2.5 eq]'],
            'OZON': [('Impact Potential', 'OZON'), 'Ozone Depletion', '[kg O3 eq]'],
            ...
        }
    """
    dict_methods_enriched = {
        key: [dict_methods[key][0], dict_methods_names[key], dict_methods_units[key]]
        for key in dict_methods
    }

    """
    list_methods_for_autocomplete = [
        ('HRSP', 'Human Health: Respiratory effects', '[kg PM2.5 eq]'),
        ('OZON', 'Ozone Depletion', '[kg O3 eq]'),
        ...
    ]
    """
    list_methods_for_autocomplete = [(key, value[1], value[2]) for key, value in dict_methods_enriched.items()]

    return dict_methods_enriched, list_methods_for_autocomplete


dict_methods, list_methods = generate_methods_objects()