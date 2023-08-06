
# evt-can-tools #

In this repository one can find tools for parsing DBC files along with EVT's copies of its own DBC files.


# Usage
## Getting a Database from dbc file

    from evtcantools.dbcmaker import DataBaseMaker

    DataBaseMaker.db_from_repo() # Get the most recent dbc revision from package
    DataBaseMaker.db_from_path("Path/to/dbc/file") # Load a file for a given file path

## Messages for a particular device
 	db = DataBaseMaker.db_from_repo() # Get the most recent dbc revision from package
	db.Load() # Parse the file and load message objects
	db.MessagesForDevice("BMS0") # Fetch messages for particular Device Name
# Installation
You have two  options, to get the most recent code  from release install from source
or use pip for official tag release installations.

## From Source

    git clone https://bitbucket.org/evt/evt-can-tools
    cd evt-can-tools
    sudo python3 setup.py install

## Pip install
	pip install evtcantools
	#python3
	pip3 install evtcantols
