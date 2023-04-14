import argparse
import configparser
import glob
from os import listdir
from os.path import isfile, join, getmtime, getsize
from datetime import datetime

from rich.console import Console
from rich.table import Table

console = Console()

# Init arg parser
parser = argparse.ArgumentParser(description='Verify failed RDF files')
parser.add_argument('--list', action='store_true',
                    help='list failed RDF files')
parser.add_argument('--fix', action='store_true',
                    help='attempt to fix failed files')
parser.add_argument('--debug', action='store_true',
                    help='print additional debug information')


# init config parser
config = configparser.ConfigParser()
config.read('config.ini')

######################################
# FUNCTIONS
######################################

def getFailedRDF(path):
    failedRDF = glob.glob(join(path,'*.rdf'))
    return failedRDF

def printFileList(fileList, title):
    table = Table(title=title)
    table.add_column("File Date", justify="right", style="cyan", no_wrap=True)
    table.add_column("File Name", style="magenta")
    table.add_column("File Size", justify="right", style="green")
    
    for file in fileList:
        date = datetime.fromtimestamp(getmtime(file)).strftime('%d.%m.%Y %H:%M')
        size = str(getsize(file))
        table.add_row(date, file, size)
        
    console.print(table)
        

######################################
# RUN
######################################
args = parser.parse_args() 
failed_path = config['main']['failed_path']
input_path = config['main']['input_path']

if(args.debug):
    console.print ("failed path: %s" % failed_path)
    console.print ("input path: %s" % input_path)
    
if (args.list):
    failedRDF = getFailedRDF(failed_path)
    printFileList(failedRDF, 'Failed RDF Files')