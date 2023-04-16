import datetime
import time
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
        ("l", "list_failed", "List failed"),
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

    async def switch_to_fileview(self):
        self.switch_to_filemenu()
        self.log_status("opening file")

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

    async def on_directory_tree_file_selected(self, file):
        await self.switch_to_fileview()
        fileview = self.query_one("FileView")
        fileview.show_file(file.path)

    def action_list_failed(self):
        self.switch_to_mainmenu()
        self.switch_to_failedlist()
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        match button_id:
            case "list_failed":
                self.switch_to_failedlist()
            case "home":
                self.switch_to_startscreen()
            case "close_file":
                self.log_status("closing file")
                self.switch_to_failedlist()
                self.switch_to_mainmenu()
            case "exit":
                VerifyApp.exit(self)
            case _:
                self.log("no valid button id")

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Container(id="app-grid"):
            with Vertical(id="sidebar-container"):
                yield SideBar()
            with Vertical(id="main-container"):
                yield MainContent()
            with Vertical(id="status-bar-container"):
                yield StatusBar()
        yield Footer()

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
        text_log.write("%s: %s" % (timestamp, message))


class StartScreen(Static):
    """A widget to display the main menu"""

    def compose(self) -> ComposeResult:
        with open("./start.md", "r") as file:
            document = file.read()
        yield MarkdownViewer(document, show_table_of_contents=False)

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

#  Context menu for single file


class FileMenu(Container):
    """A widget to display the context menu for a file"""

    def compose(self) -> ComposeResult:
        yield Button("Verify Structure", id="verify_structure", variant="default")
        yield Button("Verify Account", id="verify_acocunt", variant="default")
        yield Button("Verify Classification", id="verify_classification", variant="default")
        yield Button("Auto Correct and Move", id="auto_correct", variant="warning")
        yield Button("No Change and Move", id="move_file", variant="warning")
        yield Button("Close File", id="close_file", variant="error")


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
