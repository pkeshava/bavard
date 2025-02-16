from textual.app import App
from screens.file_picker import FilePickerScreen

class Bavard(App):
    CSS = """
    Screen {
        align: center middle;
        border: round white;
        padding: 1;
    }
    .title {
        padding: 1 0;
        text-align: center;
        color: yellow;
        border: heavy green;
    }
    DataTable {
        height: 10;
        width: 80%;
        margin: 1 0;
        border: round blue;
    }
    Input {
        width: 80%;
        margin: 1 0;
        border: round magenta;
    }
    Button {
        width: 50%;
        margin: 1 0;
        border: round cyan;
    }
    RichLog {
        height: 33%;
        width: 80%;
        margin: 1 0;
        border: round red;
    }
    Static#current_dir {
        border: round magenta;
        width: 80%;
        margin: 1 0;
    }
    Static#exit_instructions {
        text-align: center;
        color: white;
        background: darkgreen;
        padding: 1;
    }
    """
    
    def on_mount(self) -> None:
        self.push_screen(FilePickerScreen())

if __name__ == "__main__":
    Bavard().run()
