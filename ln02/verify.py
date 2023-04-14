import glob
from pathlib import Path
from typing import Iterable

from textual import log
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.containers import Container, Vertical
from textual.widgets import Button, Header, Footer, Static, Label, TextLog, DirectoryTree


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
        
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Container(id="app-grid"):
            with Vertical(id="side-bar-container"):
                yield Container(SideBar())
            with Vertical(id="main-container"):
                yield Container(MainContent())
            with Vertical(id="status-bar-container"):
                yield Container(StatusBar(), id="status-bar")     
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        if button_id == "list_failed":
            statusbar = self.query_one("StatusBar")
            statusbar.log_message("listing failed files")
            try:
               startscreen = self.query_one("#startscreen")
               if startscreen:
                  startscreen.remove()
            except:
                log("no start screen")
               
            maincontent = self.query_one("MainContent")
            if maincontent:
                filelist = None
                try:
                    filelist = self.query_one("FileList")
                except:
                    log("no file list loaded")
                if filelist is None:
                   maincontent.mount(FileList())
        elif button_id == "process":
            statusbar = self.query_one("StatusBar")
            statusbar.log_message("processing files")
        
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
        yield TextLog(highlight=True, markup=True)
        
    def on_ready(self) -> None:
        """Called when DOM is ready"""
        text_log = self.query_one(TextLog)
        text_log.write("Application ready")
    
    def log_message(self, message) -> None:
        """Write a message to the log"""
        text_log = self.query_one(TextLog)
        text_log.write(message)
        
class StartScreen(Static):
    """A widget to display the main menu"""
    def compose(self) -> ComposeResult:
        yield Label("Start Screen - Welcome")
    
# Main menu
class MainMenu(Container):
    """A widget to display the main menu"""
    def on_mount(self):
        self.log(self.tree)
        
    def compose(self) -> ComposeResult:
        yield Button("List", id="list_failed", variant="default")
        yield Button("Process", id="process", variant="default")
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