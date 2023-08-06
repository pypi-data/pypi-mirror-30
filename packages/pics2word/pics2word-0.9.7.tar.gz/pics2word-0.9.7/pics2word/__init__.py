#!/usr/bin/env python3
import os, sys, logging, errno, json
from .pics2word import *
from .LogGen import set_up_logging
from .WriteHelp import writehelp

logger = logging.getLogger(__name__)

def ExecuteHelp():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"help.json")
    if not os.path.exists(path):
        try:
            print("Creating help file...")
            writehelp(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    return path

def help(arg):
    helppath = ExecuteHelp()
    with open(helppath, 'r') as fp:
        help = json.load(fp)
        return help[arg]

def SavePath(Name):
    # Save the module in the main directory
    path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(path, "modules", Name + ".json")

def Check4Directory(file):
    path = os.path.dirname(file)
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

def remDictKey(d, key):
    '''Returns a new dictionary with a key-value pair removed'''
    logger.debug("removing %s from arg list dictionary" % key)
    new_d = d.copy()
    new_d.pop(key)
    return new_d

# Method to parse command line arguements into command-value pairs
def getopts(argv):
    opts = {}  # Empty dictionary to store key-value pairs.
    while argv:  # While there are arguments left to parse...
        if argv[0][0] == '-':  # Found a "-name value" pair.
            logging.debug("Adding %s as a value to %s command." % (argv[1], argv[0]))
            opts[argv[0]] = argv[1]  # Add key and value to the dictionary.
        argv = argv[1:]  # Reduce the argument list by copying it starting from index 1.
    return opts

def LoadSave(IniArgs):
    if '-m' in IniArgs: 
        mod = SavePath(IniArgs['-m'])
        try:
            # Try to look for the file in the directory
            logger.info("Found module %s. Loading arg list." % mod)
            with open(mod,'r') as fp:
                return json.load(fp)
        except FileNotFoundError:
            # If theres an error loading the file we assume the file does not exist and so one is set up
            logger.info("Module %s not found. creating module called %s" % (mod,mod))
            myargs = remDictKey(IniArgs, '-m') # dont resave save function
            # If the directory does not exist, create directory
            Check4Directory(mod)
            with open(mod,'w') as fp:
                json.dump(myargs, fp)
            return myargs
    else:
        return IniArgs

def main():
    #Arglist passed as immutable for key to dict 
    set_up_logging(tuple(sys.argv))
    # Parse the arguments then either Load or save an arg template
    myargs = LoadSave(getopts(sys.argv))

    Doc = pics2word()  
    if '-h' in myargs:
        print(help(myargs['-h']))
    if '-P' in myargs:
        # Override the default path
        Doc.SetPath(myargs['-P'])
    if '-f' in myargs:
        # Set as table or default
        Doc.SetFormat(format=myargs['-f'])
    if '-T' in myargs:
        # Set a title to override the default
        Doc.SetTitle(title=myargs['-T'],date=myargs['-Td'])
    if '-pw' in myargs:
        # Override the default picture width
        Doc.SetPicWidth(float(myargs['-pw']))
    if '-ph' in myargs:
        # Override the default picture height
        Doc.SetPicHeight(float(myargs['-ph'])) 
    if '-tw' in myargs:
        if Doc.format[0] != 't' :
            raise ValueError("Must enable table format to format table width!")
        else:
            Doc.SetTableWidth(int(myargs['-tw']))
    
    # after all optional parameters have been changed and not asked for help, then write document.
    if '-h' not in myargs:
        Doc.WriteDoc()
        print("\n........Done!\n")

if __name__ == '__main__':
    main()
