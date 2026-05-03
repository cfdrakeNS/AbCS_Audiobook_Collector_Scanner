import tkinter as tk

class TerminalEmu:
    def __init__(self, root):
        self.root = root
        self.root.title("ltrOne Terminal Simulator")
        
        # Fixed 80x25 grid style
        self.text_area = tk.Text(root, font=("Courier New", 14), 
                                 width=80, height=25, 
                                 bg="black", insertbackground="white")
        self.text_area.pack()

        # Define styles for the terminal
        self.text_area.tag_configure("label", foreground="turquoise")
        self.text_area.tag_configure("field", foreground="white")
        self.text_area.tag_configure("message", foreground="yellow")

        # Logic for tabbing between fields
        self.fields = []
        self.current_field_index = 0
        self.root.bind("<Tab>", self.tab_next)
        self.root.bind("<Shift-Tab>", self.tab_prev)

        self.build_screen()

    def add_element(self, row, col, text, tag):
        pos = f"{row}.{col}"
        self.text_area.insert(pos, text, tag)
        if tag == "field":
            self.fields.append(pos)

    def build_screen(self):
        # Clear area
        self.text_area.delete("1.0", tk.END)
        
        # Example: Building from your Screen Testing01 layout[cite: 2]
        self.add_element(1, 0, "TESTING01", "label")
        self.add_element(1, 33, "         BILL PAYMENT", "label")
        
        self.add_element(2, 0, "CARD NUMBER ", "label")
        self.add_element(2, 12, "4531234567890123", "field")
        
        self.add_element(2, 41, " STAFF ", "label")
        self.add_element(2, 48, "Y", "field")

        self.add_element(8, 2, "08 Column-1 line-1", "field")
        self.add_element(8, 24, "08 Column-2 line-1", "field")

    def tab_next(self, event):
        self.current_field_index = (self.current_field_index + 1) % len(self.fields)
        self.focus_field()
        return "break" # Prevent default tab behavior

    def tab_prev(self, event):
        self.current_field_index = (self.current_field_index - 1) % len(self.fields)
        self.focus_field()
        return "break"

    def focus_field(self):
        pos = self.fields[self.current_field_index]
        self.text_area.mark_set("insert", pos)
        self.text_area.see(pos)
        self.text_area.focus_set()

if __name__ == "__main__":
    root = tk.Tk()
    app = TerminalEmu(root)
    root.mainloop()