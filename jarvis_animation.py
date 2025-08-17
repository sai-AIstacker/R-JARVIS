import tkinter as tk
from PIL import Image, ImageTk, ImageSequence

GIF_PATH = r"C:\Users\rudra\Documents\jarvis\ApiG.gif"  # Your GIF path

class AnimatedGIF(tk.Label):
    def __init__(self, master, path, *args, **kwargs):
        im = Image.open(path)
        seq = []
        try:
            while True:
                seq.append(im.copy())
                im.seek(len(seq))
        except EOFError:
            pass
        # Use LANCZOS for high-quality resizing (Pillow >= 10.0.0)
        self.frames = [ImageTk.PhotoImage(img.resize((731, 731), Image.Resampling.LANCZOS)) for img in seq]
        self.idx = 0
        super().__init__(master, image=self.frames[0], *args, **kwargs)
        self.after(0, self.play)

    def play(self):
        self.idx = (self.idx + 1) % len(self.frames)
        self.config(image=self.frames[self.idx])
        self.after(100, self.play)

def show_gif_window():
    root = tk.Tk()
    root.title("Jarvis Animation")

    window_width = 731
    window_height = 731

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = screen_width - window_width - 20  # 20px margin from right edge
    y = (screen_height - window_height) // 2

    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.configure(bg='black')

    gif_label = AnimatedGIF(root, GIF_PATH, bg='black')
    gif_label.place(relx=0.5, rely=0.5, anchor='center')
    root.mainloop()

if __name__ == "__main__":
    show_gif_window()