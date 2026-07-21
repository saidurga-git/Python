import tkinter as tk
from PIL import Image, ImageTk, ImageFilter, ImageOps
import random
import os

IMAGE_FILE = "radha_krishna_original.jpg"

# Slower cinematic speed
PENCIL_POINTS_PER_FRAME = 700
COLOR_BLOCKS_PER_FRAME = 500
BLOCK_SIZE = 3
FRAME_DELAY = 10

CYAN = "#00c8ff"
PINK = "#ff1493"
GOLD = "#ff9d00"
PURPLE = "#b45cff"

class PixelSketchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Radha Krishna Slow Pixel Sketch - DcodeVerse")
        self.root.configure(bg="black")
        self.root.attributes("-fullscreen", True)

        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()

        self.canvas = tk.Canvas(root, width=self.sw, height=self.sh, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.root.bind("<Escape>", lambda e: self.root.destroy())

        base = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(base, IMAGE_FILE)

        self.original = Image.open(img_path).convert("RGB")
        self.display_img = self.fit_image(self.original, self.sw, self.sh)
        self.w, self.h = self.display_img.size
        self.x0 = (self.sw - self.w) // 2
        self.y0 = (self.sh - self.h) // 2

        self.pencil_img = self.make_pencil_edges(self.display_img)

        self.pencil_points = self.collect_pencil_points()
        self.color_blocks = self.collect_color_blocks()

        random.shuffle(self.pencil_points)
        random.shuffle(self.color_blocks)

        self.final_photo = ImageTk.PhotoImage(self.display_img)

        self.canvas.create_text(
            self.sw // 2, 35,
            text="Radha Krishna",
            fill="#ffffff",
            font=("Arial", 24, "bold")
        )

        self.canvas.create_text(
            self.sw // 2, self.sh - 45,
            text="Radhe Radhe",
            fill="#b45cff",
            font=("Arial", 14, "bold")
        )

        self.root.after(500, self.draw_pencil_phase)

    def fit_image(self, img, max_w, max_h):
        max_h = max_h - 110
        scale = min(max_w / img.width, max_h / img.height)
        new_w = int(img.width * scale)
        new_h = int(img.height * scale)
        return img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    def make_pencil_edges(self, img):
        gray = ImageOps.grayscale(img)
        gray = gray.filter(ImageFilter.FIND_EDGES)
        gray = ImageOps.autocontrast(gray)
        return gray

    def collect_pencil_points(self):
        pix = self.pencil_img.load()
        points = []
        step = 2

        for y in range(0, self.h, step):
            for x in range(0, self.w, step):
                val = pix[x, y]
                if val > 40:
                    points.append((x, y, val))

        return points

    def collect_color_blocks(self):
        pix = self.display_img.load()
        blocks = []

        for y in range(0, self.h, BLOCK_SIZE):
            for x in range(0, self.w, BLOCK_SIZE):
                r, g, b = pix[x, y]

                if r + g + b < 45:
                    continue

                if max(r, g, b) > 55:
                    blocks.append((x, y, r, g, b))

        return blocks

    def draw_pencil_phase(self):
        batch = self.pencil_points[:PENCIL_POINTS_PER_FRAME]
        self.pencil_points = self.pencil_points[PENCIL_POINTS_PER_FRAME:]

        for x, y, val in batch:
            shade = min(255, 120 + val)
            color = f"#{shade:02x}{shade:02x}{shade:02x}"

            self.canvas.create_line(
                self.x0 + x,
                self.y0 + y,
                self.x0 + x + 1,
                self.y0 + y + 1,
                fill=color
            )

        if self.pencil_points:
            self.root.after(FRAME_DELAY, self.draw_pencil_phase)
        else:
            self.root.after(2000, self.draw_color_phase)

    def get_glow_color(self, r, g, b):
        if b > r and b > g:
            return CYAN
        if r > 140 and b > 70 and g < 120:
            return PINK
        if r > 120 and g > 70 and b < 90:
            return GOLD
        if r > 120 and b > 120:
            return PURPLE
        return f"#{r:02x}{g:02x}{b:02x}"

    def draw_color_phase(self):
        batch = self.color_blocks[:COLOR_BLOCKS_PER_FRAME]
        self.color_blocks = self.color_blocks[COLOR_BLOCKS_PER_FRAME:]

        for x, y, r, g, b in batch:
            glow = self.get_glow_color(r, g, b)

            self.canvas.create_rectangle(
                self.x0 + x - 1,
                self.y0 + y - 1,
                self.x0 + x + BLOCK_SIZE + 1,
                self.y0 + y + BLOCK_SIZE + 1,
                fill=glow,
                outline=""
            )

            real = f"#{r:02x}{g:02x}{b:02x}"

            self.canvas.create_rectangle(
                self.x0 + x,
                self.y0 + y,
                self.x0 + x + BLOCK_SIZE,
                self.y0 + y + BLOCK_SIZE,
                fill=real,
                outline=""
            )

        if self.color_blocks:
            self.root.after(FRAME_DELAY, self.draw_color_phase)
        else:
            self.root.after(3000, self.reveal_exact_image)

    def reveal_exact_image(self):
        self.canvas.delete("all")
        self.canvas.create_image(
            self.sw // 2,
            self.sh // 2,
            image=self.final_photo,
            anchor="center"
        )

        self.canvas.create_text(
            self.sw // 2,
            35,
            text="Radha Krishna",
            fill="#ffffff",
            font=("Arial", 20, "bold")
        )

        self.canvas.create_text(
            self.sw // 2,
            self.sh - 45,
            text="Radhe Radhe",
            fill="#b45cff",
            font=("Arial", 26, "bold")
        )

        self.canvas.create_text(
            self.sw // 2,
            self.sh - 15,
            text="Final Image",
            fill="#00c8ff",
            font=("Arial", 14, "bold")
        )

def main():
    root = tk.Tk()
    PixelSketchApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
