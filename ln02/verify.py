import datetime
from pathlib import Path
from typing import Iterable

from textual import log
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.containers import Container, Vertical
from textual.widgets import Button, Header, Footer, Static, Label, TextLog, DirectoryTree,  MarkdownViewer


class VerifyApp(App):
    """Manage failed RDF Files"""
    CSS_PATH = "verify.css"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("l", "list_failed", "List failed")
    ]
    
    def on_load(self):
        self.log("app starting")
    
    def on_mount(self):
        self.log(self.tree)
        
    def log_status(self, message):
        statusbar = self.query_one("StatusBar")
        statusbar.log_message(message)
        
        
    def switch_to_startscreen(self):
        self.log_status("back to start")
        
        maincontent = self.query_one("#main-container")
        for child in maincontent.children:
            child.remove()
        maincontent.mount(StartScreen())
        
        
    def switch_to_failedlist(self):
        self.log_status("listing failed files")
        
        maincontent = self.query_one("#main-container")
        for child in maincontent.children:
            child.remove()
        maincontent.mount(FileList())
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Container(id="app-grid"):
            with Vertical(id="side-bar-container"):
                yield SideBar()
            with Vertical(id="main-container"):
                yield MainContent()
            with Vertical(id="status-bar-container"):
                yield StatusBar()   
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        if button_id == "list_failed":
            self.switch_to_failedlist()
        elif button_id == "home":
            self.switch_to_startscreen()
        
        elif button_id == "exit":
            VerifyApp.exit(self)



            
# Widget to display the main content
class MainContent(Container):
    """A widget to display the main content"""
    def on_mount(self):
        self.log(self.tree)
    def compose(self) -> ComposeResult:
        yield Container(StartScreen(), id="startscreen")
  
# Widget to display side bars  
class SideBar(Container):
    """A widget to display side bars"""
    
    def compose(self) -> ComposeResult:
        yield Container(MainMenu(), id="mainmenu")      

     
class StatusBar(Container):
    """A widget to display status information"""
    def compose(self) -> ComposeResult:
        yield TextLog(highlight=True, markup=True, id="statusbar-textlog")
        
    def log_message(self, message) -> None:
        """Write a message to the log"""
        text_log = self.query_one("#statusbar-textlog")
        now = datetime.datetime.now()
        timestamp = now.strftime("%H:%M:%S")
        text_log.write("%s: %s" %(timestamp, message))
        
class StartScreen(Static):
    """A widget to display the main menu"""
    def compose(self) -> ComposeResult:
        with open("./start.md", "r") as file:
            document = file.read()
        yield MarkdownViewer(document, show_table_of_contents = False)
    
# Main menu
class MainMenu(Container):
    """A widget to display the main menu"""
    def on_mount(self):
        self.log(self.tree)
        
    def compose(self) -> ComposeResult:
        yield Button("List", id="list_failed", variant="default")
        yield Button("Process", id="process", variant="default")
        yield Button("Home", id="home", variant="success")
        yield Button("Exit", id="exit", variant="error")
            
# Context menu for single file
class FileMenu(Container):
    """A widget to display the context menu for a file"""
    def compose(self) -> ComposeResult:
        yield Label("File Menu")
    
class FileList(Container):
    """A widgtet to display a list of files"""
    def compose(self) -> ComposeResult:
        yield FilteredRDFDirectoryTree("./testing/failed/")
        
class FilteredRDFDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if path.name.endswith(".rdf")]
    
if __name__ == "__main__":
    app = VerifyApp()
    app.run()