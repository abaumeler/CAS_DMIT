import datetime
import psycopg2
import os
import configparser
import xml.etree.ElementTree as ET

from pathlib import Path
from typing import Iterable
from dotenv import load_dotenv

from textual import Logger
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.containers import Container, Vertical
from textual.widgets import Button, Header, Footer, Static, Label, TextLog, DirectoryTree,  MarkdownViewer

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
    
    # State handling
    SELECTED_FILE = None
    
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
        config = configparser.ConfigParser()
        config.read('example.ini')
    
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
        self.DBG_LOG(message)
        statusbar = self.query_one("StatusBar")
        styled_message = ":wrench: %s"%(message)
        statusbar.log_message(styled_message)
    
    def log_error(self, message):
        self.ERR_LOG(message)
        statusbar = self.query_one("StatusBar")    
        styled_message = "[bold red]:x: %s[/bold red]"%(message)
        statusbar.log_message(styled_message)
    
    def log_success(self, message):
        self.INF_LOG(message)
        statusbar = self.query_one("StatusBar")
        styled_message = "[bold green]:white_heavy_check_mark: %s[/bold green]"%(message)
        statusbar.log_message(styled_message)
    
    #----------------------------
    # Database functions
    #----------------------------  
    def connect_to_db(self):
        try:
            conn = psycopg2.connect('host=localhost port=5432 dbname=%s user=%s password=%s'%(self.DB_DATABASE, self.DB_USERNAME, self.DB_PASSWORD))
            self.log_success("connection to DB %s on %s established"%(self.DB_DATABASE, "localhost"))
            self.CONNECTION = conn
        except:
            self.log_error("failed to connect to DB")
    
    def show_db_info(self):
        if self.CONNECTION:
            cursor = self.CONNECTION.cursor()
            cursor.execute('SELECT VERSION()')
            result = cursor.fetchall()
            self.log_debug(result)

    
    #----------------------------
    # File processing functions
    #----------------------------
    def process_all_failed(self):
        self.show_db_info()
                
    def verify_file_structure(self, file):
        fileview = self.query_one("FileView")

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
        maincontent.mount(FileList())

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
        SELECTED_FILE = selected_file
        fileview = self.query_one("FileView")
        fileview.show_file(selected_file.path)
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        match button_id:
            case "list_failed":
                self.switch_to_failedlist()
            case "process":
                self.process_all_failed()
            case "home":
                self.switch_to_startscreen()
            case "verify_structure":
                self.verify_file_structure()
            case "close_file":
                self.log_debug("closing file")
                self.switch_to_failedlist()
                self.switch_to_mainmenu()
            case "exit":
                self.exit_app()
            case _:
                self.log("no valid button id")


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
        yield Button("List", id="list_failed", variant="default")
        yield Button("Process", id="process", variant="default")
        yield Button("Home", id="home", variant="success")
        yield Button("Exit", id="exit", variant="error")


#########################################
# File context menu
#########################################
class FileMenu(Container):
    """A widget to display the context menu for a file"""

    def compose(self) -> ComposeResult:
        yield Button("Verify Structure", id="verify_structure", variant="default")
        yield Button("Verify Account", id="verify_acocunt", variant="default")
        yield Button("Verify Classification", id="verify_classification", variant="default")
        yield Button("Auto Correct and Move", id="auto_correct", variant="warning")
        yield Button("No Change and Move", id="move_file", variant="warning")
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
# Filebrowser
#########################################
class FileList(Container):
    """A widgtet to display a list of files"""

    def compose(self) -> ComposeResult:
        yield FilteredRDFDirectoryTree("./testing/failed/")


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
