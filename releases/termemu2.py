import tkinter as tk

def start_emu():
    root = tk.Tk()
    root.title("Legacy Terminal Simulator")
    # Set the window class name if you want to match ltrOne expectations
    root.geometry("800x600") 
    
    # Use a Text widget with a fixed-width font
    # 80 characters wide, 25 lines high
    text_area = tk.Text(root, font=("Courier New", 12), 
                        width=80, height=25, 
                        bg="black", fg="green",
                        insertbackground="white")
    
    # Insert your sample screen data here
    sample_data = """TESTING01                        BILL PAYMENT                               
CARD NUMBER 4531234567890123     	  STAFF Y           TRANSIT 60293         
Company  Acme Consulting                 	        LEVEL A9
  TITLE  Mr. SURNAME Public                       FIRST NAME John Q.
ADDRESS  99 Some Terace                              SCREEN 01 OF 02 
         Some City, X1Z 1X2                          BUS 900-123-4567   """
    
    text_area.insert("1.0", sample_data)
    text_area.pack()
    
    # This prevents the app from closing immediately
    root.mainloop()

if __name__ == "__main__":
    start_emu()