import tkinter as tk

class AS400Simulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Terminal Emulator - Commercial Loan Inquiry")
        self.root.configure(bg="#1A1A1A") 
        
        # Container anchored to the left, leaving the right side empty for JAWS popups
        self.container = tk.Frame(root, bg="#1A1A1A", padx=40, pady=40)
        self.container.pack(side="left", anchor="nw")

        self.text_area = tk.Text(self.container, font=("Courier New", 14), 
                                 width=80, height=25, 
                                 bg="black", insertbackground="white",
                                 relief="flat", bd=0)
        self.text_area.pack()

        self.text_area.tag_configure("label", foreground="turquoise") 
        self.text_area.tag_configure("field", foreground="white")     
        self.text_area.tag_configure("alert", foreground="red")       
        self.text_area.tag_configure("msg", foreground="yellow")      

        self.fields = []
        self.current_field_index = 0

        self.root.bind("<Tab>", self.tab_next)
        self.root.bind("<Shift-Tab>", self.tab_prev)
        self.text_area.bind("<Key>", self.intercept_typing)

        self.setup_grid()
        self.build_screen()
        
        if self.fields:
            self.focus_field()

    def setup_grid(self):
        self.text_area.delete("1.0", tk.END)
        for _ in range(25):
            self.text_area.insert(tk.END, " " * 80 + "\n")

    def write_aligned(self, row, anchor_col, text, tag):
        start_col = anchor_col - len(text)
        self.write(row, start_col, text, tag)

    def write(self, row, col, text, tag):
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
        self.fields.clear() # Reset fields

        # Row 1: Header[cite: 4]
        self.write(1, 0, "LN-INQ-04", "label")
        self.write(1, 28, "COMMERCIAL PORTFOLIO REVIEW", "label")
        self.write(1, 68, "2026-05-02", "label")

        # Row 3-4: Header Information[cite: 4]
        self.write_aligned(3, 13, "ENTITY ID:", "label")
        self.write_field(3, 15, "88421-990", 12)
        self.write_aligned(3, 40, "SHORT NAME:", "label")
        self.write_field(3, 42, "GLOBAL-TECH", 15)
        self.write_aligned(3, 65, "DEPT:", "label")
        self.write_field(3, 67, "CORP-01", 10)

        self.write_aligned(4, 13, "LEGAL NAME:", "label")
        self.write_field(4, 15, "GLOBAL TECHNOLOGY SOLUTIONS INC", 35)
        self.write_aligned(4, 65, "RISK:", "label")
        self.write_field(4, 67, "B3", 10)
        
        # Row 5: Reversed Contact Name[cite: 4]
        self.write_aligned(5, 13, "LAST NAME:", "label")
        self.write_field(5, 15, "JENKINS", 15)
        self.write_aligned(5, 40, "FIRST NAME:", "label")
        self.write_field(5, 42, "SARAH", 15)
        self.write_aligned(5, 65, "STATUS:", "label")
        self.write(5, 67, "PAST DUE", "alert") 

        # Row 6: Email and Page Number[cite: 4]
        self.write_aligned(6, 13, "EMAIL:", "label")
        self.write_field(6, 15, "S.JENKINS@GTS-CORP.COM", 35)
        self.write(6, 67, "Page 1 of 2", "label")

        # Row 8: Column Headers[cite: 4]
        self.write(8, 2, "LOAN INSTRUMENT", "label")
        self.write(8, 25, "CURR BALANCE", "label")
        self.write(8, 45, "INT RATE", "label")
        self.write(8, 60, "NEXT MATURITY", "label")

        # Rows 10-20: 11 Data Rows[cite: 4]
        data = [
            ("REVOLVING CR", "450,000.00", "5.25%", "2027-01-15"),
            ("*E* TERM LOAN-01", "1,200,344.12", "4.50%", "2030-06-01"),
            ("EQUIP LEASE", "89,322.00", "6.10%", "2026-12-20"),
            ("CORP REAL EST", "3,455,000.00", "4.15%", "2035-11-01"),
            ("OP-OVERDRAFT", "12,000.00", "9.00%", "N/A"),
            ("CONSTRUCTION", "750,000.00", "5.75%", "2026-08-30"),
            ("FLEET MGMT", "215,600.00", "4.85%", "2028-12-10"),
            ("GOVT SUBSIDY", "50,000.00", "2.10%", "2029-03-15"),
            ("*E* BRIDGE LOAN", "920,000.00", "7.50%", "2026-09-01"),
            ("SYNDICATED CR", "5,500,000.00", "4.00%", "2032-11-30"),
            ("LETTERS OF CR", "150,000.00", "3.25%", "2027-04-20")
        ]

        for i, (instr, bal, rate, mat) in enumerate(data):
            r = 10 + i
            # By using write_field, every cell in the table is tabible
            self.write_field(r, 2, instr, 18)
            self.write_field(r, 25, bal, 15)
            self.write_field(r, 45, rate, 10)
            self.write_field(r, 60, mat, 12)

        # Rows 22-25: Bottom Messages and F-Keys[cite: 4]
        self.write(22, 2, "MESSAGE: OUTSTANDING EXCEPTIONS ON REVOLVING CREDIT", "msg")
        self.write(23, 2, "         REVIEW RISK RATING FOR QUARTERLY AUDIT", "msg")
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
        if event.keysym not in ("Up", "Down", "Left", "Right"):
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

if __name__ == "__main__":
    root = tk.Tk()
    # 1400px wide creates massive space on the right for JAWS popups
    root.geometry("1400x850")
    app = AS400Simulator(root)
    root.mainloop()