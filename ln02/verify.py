import datetime
import psycopg2
import os
import shutil
import configparser
import xml.etree.ElementTree as ET

import StructureChecker

from pathlib import Path
from typing import Iterable
from dotenv import load_dotenv

from textual import Logger, on
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.containers import Container, Vertical
from textual.widgets import Button, Header, Footer, Static, Label, TextLog, DirectoryTree,  MarkdownViewer, Input, Label, Pretty
from textual.validation import Function, Regex, ValidationResult, Validator


#########################################
# App Class
#########################################
class VerifyApp(App):
    """Manage failed RDF Files"""
    #----------------------------
    # Globals
    #----------------------------
    # Database
    DB_USERNAME = None
    DB_PASSWORD = None
    DB_DATABASE = None
    CONNECTION = None
        
    # Logging
    ERR_LOG = Logger.error
    DBG_LOG = Logger.debug
    INF_LOG = Logger.info
    
    # configuration and state
    config = None
    selected_file = None
    
    # Paths
    failed_path = None
    input_path = None
    wait_path = None
    job_path = None
    
    # Textualize
    CSS_PATH = "verify.css"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("l", "list_failed", "List failed"),
    ]
    
    #----------------------------
    # Init functions
    #----------------------------
    def init_config(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.failed_path = self.config["PATHS"]["failed_path"]
        self.wait_path = self.config["PATHS"]["wait_path"]
        self.input_path = self.config["PATHS"]["input_path"]
        self.job_path = self.config["PATHS"]["job_path"]
        
    def on_load(self):
        self.log("starting inititialization")
        self.init_config()

    def on_mount(self):
        self.log(self.tree)
        self.log_success("inititialization done")
        self.connect_to_db()
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        with Container(id="app-grid"):
            with Vertical(id="sidebar-container"):
                yield SideBar()
            with Vertical(id="main-container"):
                yield MainContent()
            with Vertical(id="status-bar-container"):
                yield StatusBar()
        yield Footer()

    #----------------------------
    # Logging functions
    #----------------------------
    def log_debug(self, message):
        if self.config["LOG"].getboolean("debug"):
            self.DBG_LOG(message)
            statusbar = self.query_one("StatusBar")
            styled_message = ":wrench: %s"%(message)
            statusbar.log_message(styled_message)
    
    def log_error(self, message):
        if self.config["LOG"].getboolean("error"):     
            self.ERR_LOG(message)
            statusbar = self.query_one("StatusBar")    
            styled_message = "[bold red]:x: %s[/bold red]"%(message)
            statusbar.log_message(styled_message)
    
    def log_success(self, message):
        if self.config["LOG"].getboolean("success"):
            self.INF_LOG(message)
            statusbar = self.query_one("StatusBar")
            styled_message = "[bold green]:white_heavy_check_mark: %s[/bold green]"%(message)
            statusbar.log_message(styled_message)
    
    #----------------------------
    # Database functions
    #----------------------------  
    def connect_to_db(self):
        try:
            if self.config:
                conn = psycopg2.connect("host=%s port=%s dbname=%s user=%s password=%s"
                                        %(self.config["DB"]["host"], 
                                        self.config["DB"]["port"],
                                        self.config["DB"]["schema"],
                                        self.config["DB"]["user"],
                                        self.config["DB"]["password"]))
                self.log_success("connection to DB %s on %s established"%(self.config["DB"]["schema"], self.config["DB"]["host"]))
                self.CONNECTION = conn
            else:
             self.log_error("no config found")
        except:
            self.log_error("failed to connect to DB")
    
    def run_query(self, query):
        """run a query agains the configured DB"""
        if(self.CONNECTION != None):
            try:
                cur = self.CONNECTION.cursor()
                cur.execute(query)
                result = cur.fetchall()
                cur.close
                return result
            except Exception as e:
                if hasattr(e, 'message'):
                    self.log_error("error when executing query: %s "%(e.message))
                else:
                    self.log_error("error when executing query: %s "%(e))
                
        else:
            self.log_error("unable to run query - no DB connection")
            return None
    
    def show_db_info(self):
        if self.CONNECTION:
            cursor = self.CONNECTION.cursor()
            cursor.execute('SELECT VERSION()')
            result = cursor.fetchall()
            self.log_success(result[0])

    
    #----------------------------
    # File processing functions
    #----------------------------
    def check_connection(self):
        self.show_db_info()
    
    def verify_metadata(self):
        self.check_account_nr(self.selected_file.path)
        self.check_client_nr(self.selected_file.path)
                
    def verify_file_structure(self):
        if self.selected_file:
            self.log_debug("verifiying structure of %s"%(self.selected_file.path))
            if StructureChecker.checkXMLStructure(self, self.selected_file.path):
                self.log_success("structure of %s is ok"%(self.selected_file.path))
                return True
            else:
                self.log_error("structure of %s is not ok"%(self.selected_file.path))
                return False
                
    def verify_pdfcount(self):
        if self.selected_file:
            self.log_debug("checking referenced pdfs %s"%(self.selected_file.path))
            if(self.verify_file_structure()):
                referenced_pdfs = self.get_referenced_pdfs(self.selected_file.path)
                if(self.all_files_present(self.failed_path, referenced_pdfs)):
                    self.log_success("All referenced PDF files present in %s"%(self.failed_path))
                else:
                    self.log_error("At least one PDF is missing in %s"%(self.failed_path))
            else:
                self.log_error("Unable to verify pdf count because filestructure of %s is not correct"%(self.selected_file.path))
    
    def move_file(self, path):
        """move rdf and any referenced PDFs to the specified path"""
        if self.selected_file:
            self.log_debug("moving %s to "%(path))
            try:
                pdflist = self.get_referenced_pdfs(self.selected_file.path)
                if(pdflist and self.all_files_present(self.failed_path, pdflist)):
                    for pdf in pdflist:
                        pdfpath = Path(self.failed_path,pdf)
                        shutil.move(pdfpath,path)
                        self.log_success("moved %s to %s"%(pdfpath, path))
                else:
                    self.log_error("unable to get pdfs or pdfs not present, not trying to move referenced pdfs")
                shutil.move(self.selected_file.path, path)
                self.log_success("moved %s to %s"%(self.selected_file.path, path))
                self.switch_to_failedlist()
                self.switch_to_mainmenu()
            except Exception as e:
                if hasattr(e, 'message'):
                    self.log_error("failed to move file: %s "%(e.message))
                else:
                    self.log_error("failed to move file: %s "%(e))
    
    def get_referenced_pdfs(self, file):
        try:
            tree = ET.parse(file)
            root = tree.getroot()
            ns = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'}
            documents = []
            for document in root.findall('rdf:Description',ns):
                pdffile = document.get('sourceFileIdentifier')
                # in case there is no sourceFileIdentifier
                if pdffile:
                    documents.append(pdffile)
            print(documents)
            return documents
        except Exception as e:
                if hasattr(e, 'message'):
                    self.log_error("failed to get refrenced PDFs: %s "%(e.message))
                else:
                    self.log_error("failed to get refrenced PDFs: %s "%(e))
        
    def all_files_present(self,folder, filelist):
        """returns false if at least one of the provided files is not present in the given folder"""
        check = True
        if(filelist):
            for file in filelist:
                path = Path(folder,file)
                if not path.is_file():
                    check = False
            return check
        else:
            return False
    
    def check_account_nr(self, file):
        """retrieve and verify all account numbers in the given file"""
        try:
            tree = ET.parse(file)
            root = tree.getroot()
            ns = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                  'edoc': 'http://www.imtf.com/hypersuite/edoc/2.0/'}
            documents = root.findall('./rdf:Description/edoc:AccountNumber',ns)
            current_document = 1
            for document in documents:
                acc_nr = document.text
                query = "SELECT COUNT(*) FROM HEST_ACCOUNT WHERE NR = '%s'"%acc_nr
                self.log_debug(query)
                result = self.run_query(query)
                if (result[0][0] == 1):
                    self.log_success("(%s/%s) Account %s available in HS5"%(current_document, len(documents), acc_nr))
                else:
                    self.log_error("(%s/%s) Account %s is not available in HS5"%(current_document, len(documents), acc_nr))
                current_document += 1
        except Exception as e:
                if hasattr(e, 'message'):
                    self.log_error("unable to get account nr: %s "%(e.message))
                else:
                    self.log_error("unable to get account nr: : %s "%(e))
                    
    def check_client_nr(self, file):
        """retrieve and verify all client numbers in the given file"""
        try:
            tree = ET.parse(file)
            root = tree.getroot()
            ns = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                  'edoc': 'http://www.imtf.com/hypersuite/edoc/2.0/'}
            documents = root.findall('./rdf:Description/edoc:ClientNumber',ns)
            current_document = 1
            for document in root.findall('./rdf:Description/edoc:ClientNumber',ns):
                client_nr = document.text
                query = "SELECT COUNT(*) FROM HEST_CLIENT WHERE NR = '%s'"%client_nr
                self.log_debug(query)
                result = self.run_query(query)
                self.log_debug(result)
                if (result[0][0] == 1):
                    self.log_success("(%s/%s) Client %s available in HS5"%(current_document, len(documents), client_nr))
                else:
                    self.log_error("(%s/%s) Client %s is not available in HS5"%(current_document, len(documents), client_nr))
        except Exception as e:
                if hasattr(e, 'message'):
                    self.log_error("unable to get client nr: %s "%(e.message))
                else:
                    self.log_error("unable to get client nr: %s "%(e))
                    
    def check_archive_state(self):
        """retrieve and verify all Finnova document numbers in the given file"""
        failed_docs = self.get_failed_doc_nr()
        if(len(failed_docs) == 0):
            self.log_success("All documents in %s are archived"%self.selected_job)
        elif(len(failed_docs)<=20):
            self.log_error("The following documents in %s are not archived:"%self.selected_job)
            for doc in failed_docs:
                self.log_error(" Document with Finnova doc_nr: %s is not archived"%doc)
        else:
            self.log_error("The Job %s contains to many unarchived documents to list"%self.selected_job)
    
    def get_failed_doc_nr(self):
        try:
            tree = ET.parse(self.selected_job)
            root = tree.getroot()
            ns = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                  'edoc': 'http://www.imtf.com/hypersuite/edoc/2.0/',
                  'fin': 'http://www.imtf.com/hypersuite/fin/'}
            documents = root.findall('./rdf:Description/fin:DocumentNumber',ns)
            failed_docs = []
            for document in documents:
                doc_nr = document.text
                query = "SELECT COUNT(*) FROM EDST_CLIENTDOC WHERE DOC_NR = '%s'"%doc_nr
                self.log_debug(query)
                result = self.run_query(query)
                if (result[0][0] == 0):
                    failed_docs.append(doc_nr)
            return failed_docs
        except Exception as e:
                if hasattr(e, 'message'):
                    self.log_error("unable to get Finnova document nr: %s "%(e.message))
                else:
                    self.log_error("unable to get Finnova document nr: %s "%(e))
                
    def create_delta_rdf(self):
        failed_doc_nrs = self.get_failed_doc_nr()
        # try:
        #     tree = ET.parse(self.selected_job)
        #     root = tree.getroot()
        #     delta_rdf = root
        #     ns = {'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        #           'edoc': 'http://www.imtf.com/hypersuite/edoc/2.0/',
        #           'fin': 'http://www.imtf.com/hypersuite/fin/'}
            
        #     for description in delta_rdf.findall("rdf:Description",ns): 
        #         delta_rdf.remove(description[0])
            
        #     for doc_nr in failed_doc_nrs:
        #         rdf_description = root.findall(".//rdf:Description/[fin:DocumentNumber='%s']"%doc_nr,ns)
        #         delta_rdf.append(rdf_description)
        #     delta_rdf.write(file_or_filename="test.txt", encoding="UTF-8",xml_declaration=True)
        # except Exception as e:
        #         if hasattr(e, 'message'):
        #             self.log_error("unable to create delta rdf: %s "%(e.message))
        #         else:
        #             self.log_error("unable to create delta rdf: %s "%(e))
                                        
    #----------------------------
    # DOM manipulation functions
    #----------------------------
    def switch_to_startscreen(self):
        self.log_debug("back to start")
        maincontent = self.query_one("#main-container")
        for child in maincontent.children:
            child.remove()
        maincontent.mount(StartScreen())
    
    def switch_to_failedlist(self):
        self.log_debug("listing failed files")

        maincontent = self.query_one("#main-container")
        for child in maincontent.children:
            child.remove()
        failedList = FileList()
        failedList.setFilePath(self.failed_path)
        maincontent.mount(failedList)
    
    def switch_to_jobprompt(self):
        self.log_debug("switching to promptjob")
        maincontent = self.query_one("#main-container")
        for child in maincontent.children:
            child.remove()
        maincontent.mount(JobPrompt())
       
    def switch_to_jobpromptmenu(self):
        sidebar = self.query_one("#sidebar-container")
        for child in sidebar.children:
            child.remove()
        sidebar.mount(JobPromptMenu())
        
    def switch_to_jobmenu(self):
        sidebar = self.query_one("#sidebar-container")
        for child in sidebar.children:
            child.remove()
        sidebar.mount(JobMenu())
        
    async def switch_to_fileview(self):
        self.switch_to_filemenu()
        self.log_debug("opening file")

        maincontent = self.query_one("#main-container")
        for child in maincontent.children:
            child.remove()
        await maincontent.mount(FileView())

    def switch_to_filemenu(self):
        sidebar = self.query_one("#sidebar-container")
        for child in sidebar.children:
            child.remove()
        sidebar.mount(FileMenu())
        
    def switch_to_mainmenu(self):
        sidebar = self.query_one("#sidebar-container")
        for child in sidebar.children:
            child.remove()
        sidebar.mount(MainMenu()) 

    #----------------------------
    # Action handling
    #----------------------------  
    def action_list_failed(self):
        self.switch_to_mainmenu()
        self.switch_to_failedlist()
    
    #----------------------------
    # Event and message handling
    #----------------------------     
    async def on_directory_tree_file_selected(self, selected_file):
        await self.switch_to_fileview()
        self.switch_to_filemenu()
        self.selected_file = selected_file
        fileview = self.query_one("FileView")
        fileview.show_file(selected_file.path)
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        match button_id:
            case "list_failed":
                self.switch_to_failedlist()
            case "check":
                self.check_connection()
            case "verify_job":
                self.switch_to_jobpromptmenu()
                self.switch_to_jobprompt()
            case "open_job":
                self.log_debug("press enter to submit")
            case "close_job":
                self.switch_to_jobpromptmenu()
                self.switch_to_jobprompt()
            case "verify_arc_state":
                self.check_archive_state()
            case "create_delta_rdf":
                self.create_delta_rdf()
            case "home":
                self.switch_to_mainmenu()
                self.switch_to_startscreen()
            case "verify_metadata":
                self.verify_metadata()
            case "verify_structure":
                self.verify_file_structure()
            case "verify_pdfcount":
                self.verify_pdfcount()
            case "move_to_wait":
                self.move_file(self.wait_path)
            case "move_to_input":
                self.move_file(self.input_path)
            case "close_file":
                self.log_debug("closing file")
                self.switch_to_failedlist()
                self.switch_to_mainmenu()
            case "exit":
                self.exit_app()
            case _:
                self.log("no valid button id")
                
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Event handler called when enter is pressed in an input field"""
        print(event.value)
        if len(event.value) >= 3:
            path = Path(self.job_path,event.value)
            if not path.is_dir():
                self.log_error("No directory for this Job ID")
            else:
                await self.switch_to_fileview()
                self.switch_to_jobmenu()
                self.selected_job = Path(path,event.value+".rdf")
                fileview = self.query_one("FileView")
                fileview.show_file(self.selected_job)

  
    #----------------------------
    # Exit and cleanup functions
    #----------------------------  
    def exit_app(self):
        if self.CONNECTION:
            self.CONNECTION.close()
            self.log_debug("DB Connection closed")
        VerifyApp.exit(self)


#########################################
# Widget to display main content
#########################################
class MainContent(Container):
    """A widget to display the main content"""

    def on_mount(self):
        self.log(self.tree)

    def compose(self) -> ComposeResult:
        yield Container(StartScreen(), id="startscreen")


#########################################
# Widget to display sidebars
#########################################
class SideBar(Container):
    """A widget to display side bars"""

    def compose(self) -> ComposeResult:
        yield Container(MainMenu(), id="mainmenu")


#########################################
# Widged to display statusbar
#########################################
class StatusBar(Container):
    """A widget to display status information"""

    def compose(self) -> ComposeResult:
        yield TextLog(highlight=True, markup=True, id="statusbar-textlog")
        
    def log_message(self, message) -> None:
        """Write a message to the log"""
        text_log = self.query_one("#statusbar-textlog")
        now = datetime.datetime.now()
        timestamp = now.strftime("%H:%M:%S")
        text_log.write("%s: %s" % (timestamp, message))


#########################################
# Startscreen
#########################################
class StartScreen(Static):
    """A widget to display the main menu"""

    def compose(self) -> ComposeResult:
        with open("./start.md", "r") as file:
            document = file.read()
        yield MarkdownViewer(document, show_table_of_contents=False)


#########################################
# Mainmenu
#########################################
class MainMenu(Container):
    """A widget to display the main menu"""

    def on_mount(self):
        self.log(self.tree)

    def compose(self) -> ComposeResult:
        yield Button("List Failed", id="list_failed", variant="default")
        yield Button("Verify Job", id="verify_job", variant="default")
        yield Button("Check Connection", id="check", variant="default")
        yield Button("Home", id="home", variant="success")
        yield Button("Exit", id="exit", variant="error")


#########################################
# File context menu
#########################################
class FileMenu(Container):
    """A widget to display the context menu for a file"""

    def compose(self) -> ComposeResult:
        yield Button("Verify Structure", id="verify_structure", variant="default")
        yield Button("Verify Metadata", id="verify_metadata", variant="default")
        yield Button("Verify PDF Count", id="verify_pdfcount", variant="default")
        yield Button("Move to Wait", id="move_to_wait", variant="warning")
        yield Button("Move to Input", id="move_to_input", variant="warning")
        yield Button("Close File", id="close_file", variant="error")


#########################################
# Fileview
#########################################
class FileView(Container):
    """A widget to display the contents of a file"""

    def compose(self) -> ComposeResult:
        yield TextLog(highlight=True, markup=False, auto_scroll=False, id="filecontent-textlog")

    def show_file(self, path) -> None:
        """Display the conenten of a file"""
        # get content of the specified file
        try:
            with open(path, "r") as file:
                document = file.read()
        except:
            self.log("failed to read file")
        # get reference to filecontent textlog widget and write content
        text_log = self.query_one("#filecontent-textlog")
        text_log.write(document)

#########################################
# Jobprompt
#########################################
class JobPrompt(Container):
    """A widget to prompt for a Job Name"""
    def compose(self) -> ComposeResult:
      yield Label("Enter a Job name from the RAWDATA directory")
      yield Input(
            placeholder="Enter a job...",
            validators=[
                Regex(regex='Job\w*Jobid_\d{5,}',failure_description="Not a valid job name, expecting: Job_K_Jobid_77977")
            ],
            id = "text-prompt"
      )
      yield Pretty([])

    @on(Input.Changed)
    def show_invalid_reasons(self, event: Input.Changed) -> None:
        # Updating the UI to show the reasons why validation failed
        if not event.validation_result.is_valid:  
            self.query_one(Pretty).update(event.validation_result.failure_descriptions)
        else:
            self.query_one(Pretty).update([])
            
#########################################
# Jobview
#########################################
class JobView(Container):
    """A widget to display the contents of a job file"""

    def compose(self) -> ComposeResult:
        yield TextLog(highlight=True, markup=False, auto_scroll=False, id="jobcontent-textlog")

    def show_file(self, path) -> None:
        """Display the content of a job file"""
        # get content of the specified file
        try:
            with open(path, "r") as file:
                job = file.read()
        except:
            self.log("failed to read file")
        # get reference to jobcontent textlog widget and write content
        text_log = self.query_one("#jobcontent-textlog")
        text_log.write(job)

            
#########################################
# Jobview context menu
#########################################
class JobMenu(Container):
    """A widget to display the context menu for a file"""

    def compose(self) -> ComposeResult:
        yield Button("Verify Job Files", id="verify_job_files", variant="default")
        yield Button("Verify Archive Status", id="verify_arc_state", variant="default")
        yield Button("Create Delta RDF", id="create_delta_rdf", variant="warning")
        yield Button("Move Job to Input", id="job_move_to_input", variant="warning")
        yield Button("Move Delta to Input", id="job_move_delta_to_input", variant="warning")
        yield Button("Close Job", id="close_job", variant="error")
        
#########################################
# Jobprompt context menu
#########################################
class JobPromptMenu(Container):
    """A widget to display the context menu for the jobprompt"""

    def compose(self) -> ComposeResult:
        yield Button("Open Job", id="open_job", variant="default")
        yield Button("Home", id="home", variant="success")
        
#########################################
# Filebrowser
#########################################
class FileList(Container):
    """A widget to display a list of files"""
    file_path = None
    
    def setFilePath(self, path):
        self.file_path = path
    
    def compose(self) -> ComposeResult:
        yield FilteredRDFDirectoryTree(self.file_path)


#########################################
# Filebrowser for *.rdf
#########################################
class FilteredRDFDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if path.name.endswith(".rdf")]


#########################################
# Main entrypoint
#########################################
if __name__ == "__main__":
    app = VerifyApp()
    app.run()


