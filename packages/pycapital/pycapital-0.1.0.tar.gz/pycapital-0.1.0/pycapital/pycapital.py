#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sys import argv
import argparse
import country_data

"""Main module."""

TTY = False  # Flag will be set to true when running script interactively
COUNTRY_DATA = country_data.country_data  # Get list of countries and capitals


def parse_arguments(arg):
    # Handles Commandline input
    PROGRAM = "pycapital"
    DESCRIPTION = "Displays capital city of specified country."

    parser = argparse.ArgumentParser(
        prog=PROGRAM, description=DESCRIPTION,
        usage='%(prog)s [country]'
    )
    parser.add_argument('country', help="Displays the capital of country.",
                        nargs='+')
    args = parser.parse_args(arg)
    country_data_list = ' '.join(args.country)
    return country_data_list


def get_list_of_countries():
    return COUNTRY_DATA

def capital(country):
    """Prints capital of any given country."""
    countries = get_list_of_countries()
    usr_country = country
    if TTY:
        try:
            if usr_country.istitle():
                print("The Capital city of %s is %s." %
                      (usr_country, countries[usr_country]))
            else:
                usr_country = usr_country.title()
                print("The Capital City of %s is %s." %
                      (usr_country, countries[usr_country]))
        except:
            print("Please enter a valid country name.")
    else:
        try:
            if usr_country.istitle():
                return countries[usr_country]
            else:
                usr_country = usr_country.title()
                return countries[usr_country]
        except:
            return 0


def main(country_arg):
    capital(parse_arguments(country_arg))


if __name__ == "__main__":
    # Everything except the script name is passed to main
    TTY = True
    main(argv[1:])
