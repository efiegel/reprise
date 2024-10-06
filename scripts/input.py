import tkinter as tk
from tkinter import ttk

from reprise.db import database_context
from reprise.llm import Agent
from reprise.repository import add_motif


class MultiInputDialog(tk.Toplevel):
    def __init__(self, parent, initial_texts):
        super().__init__(parent)
        self.title("Review motifs")
        self.entries = []

        self.entry_frame = ttk.Frame(self)
        self.entry_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=5)

        for text in initial_texts:
            self.add_entry(text)

        add_button = ttk.Button(self, text="+", command=self.add_entry)
        add_button.grid(row=1, column=0, padx=10, pady=5)

        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, columnspan=2, pady=10)
        ok_button = ttk.Button(button_frame, text="OK", command=self.on_ok)
        ok_button.pack(side=tk.LEFT, padx=5)
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.on_cancel)
        cancel_button.pack(side=tk.LEFT, padx=5)

        self.result = None

    def add_entry(self, text=""):
        row = len(self.entries)
        entry = ttk.Entry(self.entry_frame, width=50)
        entry.insert(0, text)
        entry.grid(row=row, column=0, padx=10, pady=5)
        delete_button = ttk.Button(
            self.entry_frame, text="del", command=lambda e=entry: self.delete_entry(e)
        )
        delete_button.grid(row=row, column=1, padx=10, pady=5)
        self.entries.append(entry)

    def delete_entry(self, entry):
        row = self.entries.index(entry)
        self.entries.pop(row).destroy()
        for widget in self.entry_frame.grid_slaves():
            if int(widget.grid_info()["row"]) > row:
                widget.grid(row=int(widget.grid_info()["row"]) - 1)

    def on_ok(self):
        self.result = [entry.get() for entry in self.entries if entry.get()]
        self.destroy()

    def on_cancel(self):
        self.destroy()


def validate_snippets(initial_texts: list[str]) -> list[str]:
    root = tk.Tk()
    root.withdraw()

    dialog = MultiInputDialog(root, initial_texts)
    root.wait_window(dialog)

    return dialog.result


if __name__ == "__main__":
    text = input("enter some text: ")
    agent = Agent(model_name="gpt-4o-mini")
    with database_context():
        snippets = agent.extract_information(text)
        validated_snippets = validate_snippets(snippets)
        if validated_snippets:
            for snippet in validated_snippets:
                add_motif(snippet, None)
