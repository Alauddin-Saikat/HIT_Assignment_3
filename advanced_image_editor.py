class AdvancedImageEditor(ImageProcessor):
    def __init__(self, root):
        super().__init__()  # Inherit from base class
        self.root = root
        self.root.title("OOP-Based Advanced Image Editor")
        self.root.geometry("1000x600")

        # State tracking
        self.image_history = []       # For undo functionality
        self.tk_image = None          # Tkinter-compatible image
        self.zoom_scale = 100
        self.start_x = self.start_y = self.end_x = self.end_y = 0

        # Initialize GUI
        self.setup_ui()

    def setup_ui(self):
        # Create main image canvas
        self.canvas = tk.Canvas(self.root, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.canvas.bind("<ButtonPress-1>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.draw_crop)
        self.canvas.bind("<ButtonRelease-1>", self.end_crop)

        # Control panel (right side)
        control = tk.Frame(self.root, padx=10, pady=10)
        control.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons for image operations
        ttk.Button(control, text="Load Image", command=self.gui_load_image).pack(pady=5)
        ttk.Button(control, text="Undo", command=self.undo).pack(pady=5)
        ttk.Button(control, text="Crop", command=self.gui_crop_image).pack(pady=5)
        ttk.Button(control, text="Save", command=self.gui_save_image).pack(pady=5)

        # Slider for resizing cropped image
        ttk.Label(control, text="Resize (%)").pack()
        self.resize_slider = tk.Scale(control, from_=10, to=200, orient=tk.HORIZONTAL, command=self.gui_resize_image)
        self.resize_slider.set(100)
        self.resize_slider.pack(pady=5)

        # Slider for zooming view
        ttk.Label(control, text="Zoom View").pack()
        self.zoom_slider = tk.Scale(control, from_=10, to=300, orient=tk.HORIZONTAL, command=self.update_display)
        self.zoom_slider.set(100)
        self.zoom_slider.pack(pady=5)

    # =========================
    # GUI EVENT HANDLERS
    # =========================

    def gui_load_image(self):
        # Loads image via file dialog
        path = filedialog.askopenfilename()
        if path:
            try:
                img = self.load_image(path)
                self.image_history = [img.copy()]  # Track history for undo
                self.update_display()
            except Exception as e:
                messagebox.showerror("Load Error", str(e))

    def update_display(self, *_):
        # Converts OpenCV image to PIL, then to Tkinter for display
        img = self.processed_image
        if img is not None:
            zoom = self.zoom_slider.get() / 100
            h, w = img.shape[:2]
            img_resized = cv2.resize(img, (int(w * zoom), int(h * zoom)))
            img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            self.tk_image = ImageTk.PhotoImage(img_pil)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def start_crop(self, event):
        # Store initial mouse position for crop
        self.start_x, self.start_y = event.x, event.y

    def draw_crop(self, event):
        # Draw crop rectangle interactively
        self.end_x, self.end_y = event.x, event.y
        self.canvas.delete("crop_rect")
        self.canvas.create_rectangle(self.start_x, self.start_y, self.end_x, self.end_y, outline="red", tag="crop_rect")

    def end_crop(self, event):
        # Store final mouse position for crop
        self.end_x, self.end_y = event.x, event.y

    def gui_crop_image(self):
        # Uses overridden crop_image method to crop image
        if self.processed_image is None:
            return
        try:
            scale = self.zoom_slider.get() / 100
            x1 = int(min(self.start_x, self.end_x) / scale)
            y1 = int(min(self.start_y, self.end_y) / scale)
            x2 = int(max(self.start_x, self.end_x) / scale)
            y2 = int(max(self.start_y, self.end_y) / scale)

            cropped = super().crop_image(x1, y1, x2, y2)  # Polymorphic call
            self.image_history.append(cropped.copy())
            self.update_display()
        except Exception as e:
            messagebox.showerror("Crop Error", str(e))

    def gui_resize_image(self, value):
        # Resizes current cropped image using the slider
        if self.cropped_image is None:
            return
        try:
            resized = super().resize_image(int(value))  # Polymorphic call
            self.image_history.append(resized.copy())
            self.update_display()
        except Exception as e:
            messagebox.showerror("Resize Error", str(e))

    def gui_save_image(self):
        # Saves current processed image to user-specified file
        if self.processed_image is None:
            return
        path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
        if path:
            try:
                super().save_image(self.processed_image, path)
                messagebox.showinfo("Success", "Image saved successfully.")
            except Exception as e:
                messagebox.showerror("Save Error", str(e))

    def undo(self):
        # Undo last image operation
        if len(self.image_history) > 1:
            self.image_history.pop()
            self.processed_image = self.image_history[-1].copy()
            self.update_display()

# Entry point to run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedImageEditor(root)
    root.mainloop()
