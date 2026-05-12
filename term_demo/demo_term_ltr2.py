import tkinter as tk

class AS400Simulator:
    def __init__(self, root):
        self.root = root
        self.root.title("AS/400 Terminal - ltrOne Demo")
        
        # Standard Terminal Grid: 80x25
        self.text_area = tk.Text(root, font=("Courier New", 14), 
                                 width=80, height=25, 
                                 bg="black", insertbackground="white")
        self.text_area.pack()

        # Tags for Colors and Protection
        self.text_area.tag_configure("label", foreground="turquoise") # Locked
        self.text_area.tag_configure("field", foreground="white")     # Editable
        self.text_area.tag_configure("msg", foreground="yellow")      # Locked

        # Coordinates for Tab Stops (Row, Col, Length)
        # These match your provided layout specifically
        self.fields = [
            (2, 12, 16), (2, 41, 1), (2, 60, 5), # Card, Staff, Transit
            (3, 9, 20), (3, 54, 2),              # Company, Level
            (4, 9, 3), (4, 21, 15), (4, 48, 15), # Title, Surname, First Name
            (5, 9, 25), (6, 9, 25), (6, 41, 12)  # Address lines, Bus
        ]
        self.current_field_index = 0

        # Bindings
        self.root.bind("<Tab>", self.tab_next)
        self.root.bind("<Shift-Tab>", self.tab_prev)
        self.text_area.bind("<Key>", self.intercept_typing)

        self.setup_grid()
        self.build_screen()
        self.focus_field()

    def setup_grid(self):
        """Initializes a rock-solid 80x25 character buffer."""
        self.text_area.delete("1.0", tk.END)
        for _ in range(25):
            self.text_area.insert(tk.END, " " * 80 + "\n")

    def write(self, row, col, text, tag):
        """Overwrites text at coordinates without shifting the grid."""
        start = f"{row}.{col}"
        end = f"{row}.{col + len(text)}"
        self.text_area.delete(start, end)
        self.text_area.insert(start, text, tag)

    def build_screen(self):
        # Header Row 1[cite: 2]
        self.write(1, 0, "TESTING01", "label")
        self.write(1, 33, "BILL PAYMENT", "label")

        # Data Row 2[cite: 2]
        self.write(2, 0, "CARD NUMBER ", "label")
        self.write(2, 12, "4531234567890123", "field")
        self.write(2, 33, "STAFF ", "label")
        self.write(2, 39, "Y", "field")
        self.write(2, 52, "TRANSIT ", "label")
        self.write(2, 60, "60293", "field")

        # Row 3 & 4[cite: 2]
        self.write(3, 0, "Company ", "label")
        self.write(3, 9, "Acme Consulting", "field")
        self.write(3, 48, "LEVEL ", "label")
        self.write(3, 54, "A9", "field")
        
        self.write(4, 2, "TITLE ", "label")
        self.write(4, 9, "Mr.", "field")
        self.write(4, 13, "SURNAME ", "label")
        self.write(4, 21, "Public", "field")
        self.write(4, 48, "FIRST NAME ", "label")
        self.write(4, 59, "John Q.", "field")

        # Address & Page Info[cite: 2]
        self.write(5, 0, "ADDRESS ", "label")
        self.write(5, 9, "99 Some Terace", "field")
        self.write(5, 53, "SCREEN 01 OF 02", "label")
        self.write(6, 9, "Some City, X1Z 1X2", "field")
        self.write(6, 53, "BUS ", "label")
        self.write(6, 57, "900-123-4567", "field")

        # Locked Columns (Rows 8-12)[cite: 2]
        for i in range(5):
            r = 8 + i
            num = f"0{8+i}" if r < 10 else f"{r}"
            self.write(r, 2, f"{num} Column-1", "label")
            self.write(r, 24, f"{num} Column-2", "label")
            self.write(r, 49, f"{num} Column 3", "label")

        # Message Lines[cite: 2]
        self.write(20, 3, "Message Line 1 for testing 1", "msg")
        self.write(21, 3, "Message Line 2 for testing 2", "msg")

    def intercept_typing(self, event):
        """Forces overwrite mode so the screen layout never breaks."""
        if len(event.char) == 1 and event.keysym not in ("BackSpace", "Delete", "Tab"):
            curr_pos = self.text_area.index(tk.INSERT)
            row, col = map(int, curr_pos.split('.'))
            
            # Check if current cursor is inside an editable field
            for f_row, f_col, f_len in self.fields:
                if row == f_row and f_col <= col < (f_col + f_len):
                    self.write(row, col, event.char, "field")
                    self.text_area.mark_set("insert", f"{row}.{col+1}")
                    return "break"
        
        if event.keysym not in ("Up", "Down", "Left", "Right"):
            return "break" # Lock everything else

    def tab_next(self, event):
        self.current_field_index = (self.current_field_index + 1) % len(self.fields)
        self.focus_field()
        return "break"

    def tab_prev(self, event):
        self.current_field_index = (self.current_field_index - 1) % len(self.fields)
        self.focus_field()
        return "break"

    def focus_field(self):
        row, col, _ = self.fields[self.current_field_index]
        self.text_area.mark_set("insert", f"{row}.{col}")
        self.text_area.focus_set()

if __name__ == "__main__":
    root = tk.Tk()
    app = AS400Simulator(root)
    root.mainloop()