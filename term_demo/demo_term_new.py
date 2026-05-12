import tkinter as tk

class AS400Simulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Terminal Emulator - Commercial Loan Inquiry")
        self.root.configure(bg="#1A1A1A") 
        
        # Outer container anchors the screen left, leaving massive space on the right
        self.container = tk.Frame(root, bg="#1A1A1A")
        self.container.pack(side="left", anchor="nw", fill="y")

        # padx=55 and pady=57 creates the visual "5 columns" and "3 lines" of black space
        # WITHOUT breaking the 80x25 coordinate grid for your JAWS scripts.
        self.text_area = tk.Text(self.container, font=("Courier New", 14, "bold"), 
                                 width=80, height=25, 
                                 bg="black", fg="white", insertbackground="white",
                                 relief="flat", bd=0, padx=55, pady=57,
                                 blockcursor=True) # Enables the classic block terminal cursor
        self.text_area.pack()

        # Terminal Colors
        self.text_area.tag_configure("label", foreground="turquoise") 
        self.text_area.tag_configure("field", foreground="white")     
        self.text_area.tag_configure("alert", foreground="red")       
        self.text_area.tag_configure("msg", foreground="yellow")      

        self.fields = []
        self.current_field_index = 0

        # Bind tab events directly to the text widget to ensure it catches them
        self.text_area.bind("<Tab>", self.tab_next)
        self.text_area.bind("<Shift-Tab>", self.tab_prev)
        self.text_area.bind("<ISO_Left_Tab>", self.tab_prev) # Catch for Windows Shift-Tab
        self.text_area.bind("<Key>", self.intercept_typing)

        self.setup_grid()
        self.build_screen()
        
        if self.fields:
            self.focus_field()

    def setup_grid(self):
        self.text_area.delete("1.0", tk.END)
        # Initializes exactly 25 lines of exactly 80 spaces
        for _ in range(25):
            self.text_area.insert(tk.END, " " * 80 + "\n")

    def write_aligned(self, row, anchor_col, text, tag):
        """Right-aligns text ending at anchor_col (0-indexed)."""
        start_col = anchor_col - len(text)
        self.write(row, start_col, text, tag)

    def write(self, row, col, text, tag):
        """Writes text at specific 1-based Row and 0-based Col."""
        start = f"{row}.{col}"
        end = f"{row}.{col + len(text)}"
        self.text_area.delete(start, end)
        self.text_area.insert(start, text, tag)

    def write_field(self, row, col, text, length):
        """Writes data and registers it as an editable, tab-friendly field."""
        padded_text = text[:length].ljust(length)
        self.write(row, col, padded_text, "field")
        self.fields.append((row, col, length))

    def build_screen(self):
        self.fields.clear() 

        # Row 1: Header (Strictly hitting Col 1 and Col 80)
        self.write(1, 0, "LN-INQ-04", "label") # Starts at col index 0
        self.write(1, 26, "COMMERCIAL PORTFOLIO REVIEW", "label") # Centered
        self.write(1, 70, "2026-05-02", "label") # Length 10, ends exactly at index 79 (Col 80)

        # Row 3-6: Header Information (Spread out for 80 cols)
        self.write_aligned(3, 12, "ENTITY ID:", "label")
        self.write_field(3, 14, "88421-990", 12)
        self.write_aligned(3, 50, "SHORT NAME:", "label")
        self.write_field(3, 52, "GLOBAL-TECH", 14)
        self.write_aligned(3, 73, "DEPT:", "label")
        self.write_field(3, 75, "CORP", 4)

        self.write_aligned(4, 12, "LEGAL NAME:", "label")
        self.write_field(4, 14, "GLOBAL TECH SOLUTIONS", 21)
        self.write_aligned(4, 50, "RISK:", "label")
        self.write_field(4, 52, "B3", 4)
        
        self.write_aligned(5, 12, "LAST NAME:", "label")
        self.write_field(5, 14, "JENKINS", 15)
        self.write_aligned(5, 50, "FIRST NAME:", "label")
        self.write_field(5, 52, "SARAH", 15)
        self.write_aligned(5, 73, "STATUS:", "label")
        self.write(5, 75, "LATE", "alert") 

        self.write_aligned(6, 12, "EMAIL:", "label")
        self.write_field(6, 14, "S.JENKINS@GTS-CORP.COM", 22)
        self.write_aligned(6, 73, "PAGE:", "label")
        self.write(6, 75, "1/2", "label")

        # Row 8: Column Headers (5 Columns evenly spaced across 80 chars)
        self.write(8, 0, "INSTRUMENT", "label")     # Col 0
        self.write(8, 18, "BALANCE", "label")        # Col 18
        self.write(8, 35, "RATE", "label")           # Col 35
        self.write(8, 48, "MATURITY", "label")       # Col 48
        self.write(8, 66, "TRANS #", "label")        # Col 66

        # Rows 10-20: Data Rows with 5 columns
        data = [
            ("REVOLVING CR", "450,000.00", "5.25%", "2027-01-15", "TX908A1B2C"),
            ("*E* TERM LOAN", "1,200,344.12", "4.50%", "2030-06-01", "TX883J9K4L"),
            ("EQUIP LEASE", "89,322.00", "6.10%", "2026-12-20", "TX112M4N5P"),
            ("CORP REAL EST", "3,455,000.00", "4.15%", "2035-11-01", "TX445Q8R2S"),
            ("OP-OVERDRAFT", "12,000.00", "9.00%", "N/A", "TX990T1U6V"),
            ("CONSTRUCTION", "750,000.00", "5.75%", "2026-08-30", "TX221W4X9Y"),
            ("FLEET MGMT", "215,600.00", "4.85%", "2028-12-10", "TX776Z2A3B"),
            ("GOVT SUBSIDY", "50,000.00", "2.10%", "2029-03-15", "TX334C7D8E"),
            ("BRIDGE LOAN", "920,000.00", "7.50%", "2026-09-01", "TX558F1G2H"),
            ("SYNDICATED CR", "5,500,000.00", "4.00%", "2032-11-30", "TX669I4J5K"),
            ("LETTERS OF CR", "150,000.00", "3.25%", "2027-04-20", "TX882L7M8N")
        ]

        for i, (instr, bal, rate, mat, trx) in enumerate(data):
            r = 10 + i
            self.write_field(r, 0, instr, 16)
            self.write_field(r, 18, bal, 15)
            self.write_field(r, 35, rate, 6)
            self.write_field(r, 48, mat, 12)
            self.write_field(r, 66, trx, 10)

        # Rows 22-25: Bottom Messages and F-Keys
        self.write(22, 0, "MESSAGE: OUTSTANDING EXCEPTIONS ON REVOLVING CREDIT", "msg")
        self.write(23, 0, "         REVIEW RISK RATING FOR QUARTERLY AUDIT", "msg")
        self.write(25, 0, "F3=EXIT  F5=REFRESH  F7=BACKWARD  F8=FORWARD  F12=CANCEL", "label")

    def intercept_typing(self, event):
        if len(event.char) == 1 and event.keysym not in ("BackSpace", "Delete", "Tab"):
            curr_pos = self.text_area.index(tk.INSERT)
            row, col = map(int, curr_pos.split('.'))
            for f_row, f_col, f_len in self.fields:
                if row == f_row and f_col <= col < (f_col + f_len):
                    self.write(row, col, event.char, "field")
                    self.text_area.mark_set("insert", f"{row}.{col+1}")
                    return "break"
        if event.keysym not in ("Up", "Down", "Left", "Right", "Tab", "ISO_Left_Tab"):
            return "break"

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
        self.text_area.see(f"{row}.{col}") # Ensures the view scrolls to the cursor if needed

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1400x850")
    
    # Ensure the main window grabs focus immediately upon opening
    root.focus_force() 
    
    app = AS400Simulator(root)
    root.mainloop()