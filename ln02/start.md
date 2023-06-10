# Welcome - Verify 
This script can be used to verify RDF files against HS5. Where possible RDF files can be repaired.

# Usage
- Click on `List` to list all failed files, clicking again will refresh the tree view
- Click on `Process` to process all files (currently only shows debug information)
- Click on `Home` to show this message again
- Click `Exit` to exit the script

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