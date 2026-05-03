import tkinter as tk

class AS400Simulator:
    def __init__(self, root):
        self.root = root
        self.root.title("AS/400 Banking System - ltrOne Demo")
        
        # Standard AS/400 is often 24x80, but we'll use 25 rows for a status line
        self.text_area = tk.Text(root, font=("Courier New", 14), 
                                 width=80, height=25, 
                                 bg="black", insertbackground="white")
        self.text_area.pack()

        # Terminal Color Scheme
        self.text_area.tag_configure("label", foreground="turquoise") # Protected text
        self.text_area.tag_configure("field", foreground="white")     # Unprotected/Data
        self.text_area.tag_configure("alert", foreground="red")       # Flags/Errors
        self.text_area.tag_configure("status", foreground="green")     # Success/Messages

        self.fields = []
        self.current_field_index = 0
        self.root.bind("<Tab>", self.tab_next)
        self.root.bind("<Shift-Tab>", self.tab_prev)

        self.build_as400_screen()

    def add_element(self, row, col, text, tag):
        # Coordinates must be exactly positioned for JAWS scraping
        pos = f"{row}.{col}"
        # We use a padding trick to ensure the text stays in the right "column"
        self.text_area.insert(pos, text, tag)
        if tag == "field":
            self.fields.append(pos)

    def build_as400_screen(self):
        self.text_area.delete("1.0", tk.END)
        # Pad with 25 lines of 80 spaces to ensure the coordinate grid is solid
        for i in range(25):
            self.text_area.insert(f"{i+1}.0", " " * 80 + "\n")

        # --- Header Section ---
        self.add_element(1, 1, "ACCT-5542", "label")
        self.add_element(1, 30, "CUSTOMER PAYMENT OVERVIEW", "label")
        self.add_element(1, 65, "SYS-REFR", "label")

        self.add_element(3, 1, "CUSTOMER:", "label")
        self.add_element(3, 11, " CLIFFORD DRAKE", "field")
        self.add_element(3, 50, "STATUS:", "label")
        self.add_element(3, 58, " PAST DUE", "alert") # Flag for Auto-Read

        # --- Column Header Section ---
        self.add_element(6, 5, "ITEM DESCRIPTION", "label")
        self.add_element(6, 40, "AMOUNT DUE", "label")
        self.add_element(6, 60, "DUE DATE", "label")

        # --- Data Columns (Line 8-12) ---
        # Column 1: Item Descriptions with *E* flags
        items = ["*E* MORTGAGE PMT", "UTILITIES - NS", "PROPERTY TAX", "*E* REPAIR-HVAC", "CABLE/INTERNET"]
        amounts = ["2,450.00", "312.45", "890.00", "1,200.00", "155.00"]
        
        for i, (item, amt) in enumerate(zip(items, amounts)):
            row = 8 + i
            # Column 1 starts at col 5
            self.add_element(row, 5, item, "field")
            # Column 2 starts at col 40
            self.add_element(row, 40, amt, "field")

        # --- Footer/Messages ---
        self.add_element(20, 2, "MESSAGE: PLEASE REVIEW ENTRIES MARKED WITH *E*", "status")
        self.add_element(22, 1, "F3=EXIT   F5=REFRESH   F12=CANCEL", "label")

    def tab_next(self, event):
        self.current_field_index = (self.current_field_index + 1) % len(self.fields)
        self.focus_field()
        return "break"

    def tab_prev(self, event):
        self.current_field_index = (self.current_field_index - 1) % len(self.fields)
        self.focus_field()
        return "break"

    def focus_field(self):
        pos = self.fields[self.current_field_index]
        self.text_area.mark_set("insert", pos)
        self.text_area.focus_set()

if __name__ == "__main__":
    root = tk.Tk()
    app = AS400Simulator(root)
    root.mainloop()