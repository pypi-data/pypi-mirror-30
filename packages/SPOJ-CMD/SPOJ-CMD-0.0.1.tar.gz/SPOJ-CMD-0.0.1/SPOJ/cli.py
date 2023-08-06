#! /usr/bin/python3

import click
import requests
from bs4 import BeautifulSoup


# The entry point of the app
@click.command()
def main():
    # Show the user the intro message
    get_intro()

    # Prompt the user to pick a range
    probs_source = click.prompt("  Please select the required range of problems or press enter for problems in range 1-49", default=1)

    # Dictionary containing the range of problems
    probs_dict = get_probs_sources()

    if probs_source in probs_dict.keys():
        probs_statements(probs_source)
    else:
        click.echo(click.style("Wrong input try again", fg='red'))


# Return the problems sources
def get_probs_sources():
    return {1: '1-49', 2: '50-99', 3: '100-149', 4: '150-199'}


# Return the intro message to show the user
def get_intro():
    click.secho("-" * 100, fg='yellow')
    click.secho("\t\tWelcome to Spoj Catalogue", fg='blue')
    click.secho("-" * 100, fg='yellow')
    click.echo("\n")

    click.secho("\t\tCHOOSE PROBLEMS FROM THE GIVEN RANGE", fg='green')
    click.secho('''        
        1 - 1-49
        2 - 50-100 
        3 - 100-149
        4 - 150-199
    ''', fg='blue')


# Function to get problem and links from the specified source, range 1-50 as the default.
def probs_statements(source):
    if source == 1:
        data = requests.get('http://www.spoj.com/problems/classical/sort=6')
    elif source == 2:
        data = requests.get('http://www.spoj.com/problems/classical/sort=6,start=50')     
    elif source == 3:
        data = requests.get('http://www.spoj.com/problems/classical/sort=6,start=100')    
    else:
        data = requests.get('http://www.spoj.com/problems/classical/sort=6,start=150')
    if data.status_code == 200:
        bs_Obj = BeautifulSoup(data.text,'lxml')
        print("\n")
        for problem in bs_Obj.findAll('td',{'align':'left'}):
            link = problem.find("a")['href'] 
            title = (problem.get_text().strip().encode('utf-8'))
            click.secho("-" * 100, fg='yellow')
            print(" TITLE: {} \t LINK: {}\n".format(title, ('http://www.spoj.com'+link)))
    else:
        click.echo("An error occurred try again later")

if __name__ == "__main__":
    main()

