import customtkinter as ctk
from tkinter import filedialog, messagebox, Canvas
import fitz  # PyMuPDF
from PIL import Image, ImageTk, ImageOps
import os

ctk.set_appearance_mode("Dark")

class NexusMobile(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("N PDF Opner")
        self.geometry("1100x850")
        self.configure(fg_color="#0a0a0a")

        # --- Internal State ---
        self.doc = None
        self.current_page = 0
        self.zoom_level = 1.8
        self.night_mode = False
        self.tool = "view"
        self._image_ref = None # CRITICAL: Prevents image from disappearing

        # --- UI LAYOUT ---
        # 1. Main Canvas (Document Area)
        self.canvas = Canvas(self, bg="#0a0a0a", highlightthickness=0, bd=0)
        self.canvas.pack(expand=True, fill="both")

        # 2. Glassmorphism Top Bar
        self.top_bar = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=20, height=50)
        self.top_bar.place(relx=0.5, rely=0.03, anchor="n", relwidth=0.85)
        
        self.open_btn = ctk.CTkButton(self.top_bar, text="📂", width=40, fg_color="transparent", command=self.load_pdf)
        self.open_btn.pack(side="left", padx=15)

        self.title_lbl = ctk.CTkLabel(self.top_bar, text="Ready for PDF...", font=("Inter", 13, "bold"))
        self.title_lbl.pack(side="left", expand=True)

        self.night_btn = ctk.CTkButton(self.top_bar, text="🌙", width=40, fg_color="transparent", command=self.toggle_night)
        self.night_btn.pack(side="right", padx=15)

        # 3. Mobile Floating Tool Dock (Bottom)
        self.dock = ctk.CTkFrame(self, fg_color="#110D0D", corner_radius=30, height=70)
        self.dock.place(relx=0.5, rely=0.96, anchor="s")

        tools = [("🖐️", "view"), ("✏️", "pencil"), ("🖍️", "highlight"), ("🔍+", "zoom_in"), ("🔍-", "zoom_out"), ("📋", "copy")]
        for icon, mode in tools:
            btn = ctk.CTkButton(self.dock, text=icon, width=55, height=50, fg_color="transparent", 
                                hover_color="#282222", command=lambda m=mode: self.handle_action(m))
            btn.pack(side="left", padx=5, pady=8)

        # --- BINDINGS ---
        self.canvas.bind("<MouseWheel>", self.on_zoom_scroll)
        self.canvas.bind("<Button-4>", self.on_zoom_scroll) # Linux
        self.canvas.bind("<Button-5>", self.on_zoom_scroll) # Linux
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)

    def load_pdf(self):
        f = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if f:
            self.doc = fitz.open(f)
            self.current_page = 0
            self.title_lbl.configure(text=os.path.basename(f))
            self.render_page()

    def handle_action(self, mode):
        if mode == "zoom_in": 
            self.zoom_level *= 1.2
            self.render_page()
        elif mode == "zoom_out":
            self.zoom_level *= 0.8
            self.render_page()
        elif mode == "copy":
            if self.doc:
                txt = self.doc[self.current_page].get_text()
                self.clipboard_clear()
                self.clipboard_append(txt)
                messagebox.showinfo("Nexus", "Page text copied!")
        else:
            self.tool = mode
            print(f"Tool changed to: {mode}")

    def on_zoom_scroll(self, event):
        if not self.doc: return
        # Windows uses event.delta, Linux/Mac uses event.num
        if event.delta > 0 or event.num == 4:
            self.zoom_level *= 1.1
        else:
            self.zoom_level *= 0.9
        self.zoom_level = max(0.5, min(self.zoom_level, 5.0))
        self.render_page()

    def on_press(self, event):
        self.canvas.scan_mark(event.x, event.y)
        self.last_x, self.last_y = event.x, event.y

    def on_drag(self, event):
        if self.tool == "view":
            self.canvas.scan_dragto(event.x, event.y, gain=1)
        else:
            color = "#ff4444" if self.tool == "pencil" else "#ffff00"
            width = 2 if self.tool == "pencil" else 20
            self.canvas.create_line(self.last_x, self.last_y, event.x, event.y, 
                                    fill=color, width=width, capstyle="round", smooth=True)
            self.last_x, self.last_y = event.x, event.y

    def toggle_night(self):
        self.night_mode = not self.night_mode
        self.render_page()

    def render_page(self):
        if not self.doc: return
        try:
            page = self.doc.load_page(self.current_page)
            # High-DPI Scaling for clarity
            pix = page.get_pixmap(matrix=fitz.Matrix(self.zoom_level, self.zoom_level))
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            if self.night_mode:
                img = ImageOps.invert(img)

            # Keep a strong reference to the image to prevent flickering/vanishing
            self._image_ref = ImageTk.PhotoImage(img)
            self.canvas.delete("all")
            self.canvas.create_image(self.canvas.winfo_width()//2, 20, anchor="n", image=self._image_ref)
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
        except Exception as e:
            print(f"Render error: {e}")

if __name__ == "__main__":
    app = NexusMobile()
    app.mainloop()