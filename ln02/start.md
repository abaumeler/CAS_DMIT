# Welcome - Verify 
This script can be used to verify RDF files against HS5. Inspected files can then be moved to the input or wait directories to process them again or perform further checks.

This script can also be used to verify an entire Domtrac Job folder. The script will verify that each document in the job is archived.
# Usage
- Click on `List Failed` to list all failed files, clicking again will refresh the tree view
- Click on `Verify Job` to enter a Job Nr to verify. Various checks can be performed on the selected Job file. The Job name has to be entred in the format: `Job_K_Jobid_99999` where only the number part is changeable
- Click on `Check Connection` to print debug information about the database connection in use
- Click on `Home` to show this message again
- Click `Exit` to exit the script

# Configuration
This script expects a config file called `config.ini` next to the `*.py` File. 

The configuration file is divided into three sections:
- Paths (PATHS)
- Database (DB)
- Log (LOG)

## Path Configuration
All paths must be specified as absolute paths. The user is responsible to ensure that the script has the required access rights on the configured paths. No access checks are performed by the script. The user that executes this script must have read and write access to all paths configurable below. The following paths are configurable:
- `failed_path`: This path is used by the script to list the files that could not be archived. This setting should point to the failed path configured in Hypersuite
- `input_path`: This path is used by the script to re-archive single files and Jobs. This setting should point to the directory where Hypersuite watches for files to import
- `wait_path`This path is used to specifiy a directory that holds files for further manual examination. It can point to any convinient location on the filesystem.
- `job_path` This path is used to look for processed job files when the user selects the menu point "Verify Job". This path should point to the directory where the RDF Preloader places processed job files (e.g. /root/somepath/rawdata/done)

## Database Configuration
This section is used to configure the connection to the Hypersuite Database. No write access is required by the script, however all SQL queries used by the script assume you use the owner of the archive tabels who has write access. If you prefere to use another user, the queries in this script have to be changed to respect that.

- host: IP or DNS entry to the Hypersuite databasea
- port: Port used by the database listener
- schema: Name of the schema that is used for the archive
- user: Username to connect to the database. See comment above if you want to use an user other than the shema owner.
- password: Password corresponding to the username specified above

## Logging Configuration
There are three message types that can be activated individually by setting the corresponding entry to `True` or `False`:
- success
- error
- debug

For normal operation the info and error messags should be enabled. If more information is needed debug can be enabled

# Document verification
The application lists all *.rdf documents present in the configured failed directory. To process a Document click on a document in the file system tree on the right screen. When an RDF file is selected the application attempts to open its contents. If the application is able to open the file, the filecontent is displayed. Use the buttons on the left screen to perform checks on the currently selected file and to move the file to other directories for further processing.
 ## Verify Structure
Performs a basic check on the RDF structure. If no errors are detected a message will appear in the lower screen.

## Verify Metadata
Reads select metadata from the file and checks if those values are present in the connected HS5 metadata Database. Currently the following metadata are verified.
- Account Nr.
- Client Nr.

## Verify PDF Count
Verifys that all PDFs referenced in the currently selected RDF file are present in the failed directory. This check is important in order to re-process an RDF file.

Please note that only the existence of a file with an *.PDF descriptor is checked. No checks are performed on permissions or the actual file contents of the PDF files.

## Move to Wait
Moves the currently selected RDF file and all referenced PDF files to the specified wait directory. This function can be used for RDF Files that need further manual processing.

## Move to Input
Moves the currently selected RDF file and all referenced PDF files to the specified input directory. This means the HS5 System will attempt another import of these documents.

## Close File
Does not perform any action on the selected file. Will close the current screen and return to the file system tree screen.

# Job verification
By selecting the button `Verify Job` the script will prompt you for a job name. You have to specify a valid Job name in the Format `Job_K_Jobid_99999`. The script will then look in the configured job direcotry for a job with this name. If such a Job exists the job RDF file will be displayed alongside various actions that can be performed with this job. In the case you have provided a valid Jobname but no such job exists in the configured job directory, the script will print the error message: `No direcotry for this Job ID`.

For a valid Job you can choose from the following actions:
- `Verify Job Files`: (*Not yet implemented*)  Verifies that all pdfs specified in the job RDF are present on the fileystem.
- `Verify Archive Status` Verifies that each pdf referenced in the job RDF has been archived. Verification is done by checking if the corresponding Finnova Document number (`fin:DocumentNumber`) is present in the `EDST_CLIENTDOC` table
- `Create Delta RDF` (*Not yet implemented*) Creates a new job RDF with the header information form the current job and description elements for all PDF files of the current job that have not yet been archived.
- `Move Job to Input` (*Not yet implemented*) Moves the currently selected job file and all referenced pdfs to the input directory for processing
- `Move Delta to Input` (*Not yet implemented*) If a delta RDF has been created the delta RDF and all PDFs referenced in the delta RDF will be moved to the input directory. If no delta RDF has been created the Script will print an error message.