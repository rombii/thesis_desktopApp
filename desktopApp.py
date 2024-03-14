import os
import sys
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk
from PIL import Image, ImageTk
import io
import base64
import tensorflow as tf
import threading
from ConditioningAugmentation.text_encoder import get_embedding

if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    inner_dir = ''
else:
    base_path = os.path.dirname(os.path.abspath(__file__))
    inner_dir = 'res'

encoder_path = os.path.join(base_path, 'ConditioningAugmentation')
gif_path = os.path.join(base_path, inner_dir, 'loading.gif')
gen_path = os.path.join(base_path, inner_dir, 'generator.h5')
generator = tf.keras.models.load_model(gen_path)


def generate_image():
    image_label.unload()
    image_label.load(gif_path)
    warning_label.config(text="This may take a few seconds. Please wait...")

    button.config(state=tk.DISABLED)
    save_button.config(state=tk.DISABLED)
    text_input.config(state=tk.DISABLED)

    text = text_input.get("1.0", "end")
    embed = get_embedding([text])
    noise = tf.random.normal([1, 100])
    image = generator([embed, noise], training=False)

    image = image[0].numpy()
    image = (image * 127.5 + 127.5).astype('uint8')

    image = Image.fromarray(image)
    image_label.original_image = image
    image = image.resize((256, 256))

    image_byte_arr = io.BytesIO()
    image.save(image_byte_arr, format='PNG')
    image_byte_arr = image_byte_arr.getvalue()
    image_b64 = base64.b64encode(image_byte_arr)
    image_b64 = base64.b64decode(image_b64)
    image_byte_arr = io.BytesIO(image_b64)
    image = Image.open(image_byte_arr)

    root.after(0, update_image, image)

    button.config(state=tk.NORMAL)
    text_input.config(state=tk.NORMAL)
    warning_label.config(
        text="This image has size of 64x64 but is being displayed as 256x256 for better visualization.")
    save_button.config(state=tk.NORMAL)


def update_image(image):
    photo = ImageTk.PhotoImage(image)

    image_label.unload()
    image_label.config(image=photo)
    image_label.load(image)


def save_image():
    image = image_label.original_image
    file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG files", "*.png")],
                                             initialfile="generated_image.png")
    if file_path:
        image.save(file_path)
        warning_label.config(text=f"Image saved as {file_path}")


class ImageLabel(tk.Label):
    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
        self.loc = 0
        self.frames = []

        try:
            for i in range(1000):
                photo = ImageTk.PhotoImage(im.copy())
                self.frames.append(photo)
                im.seek(i)
        except EOFError:
            pass

        try:
            self.delay = im.info['duration']
        except:
            self.delay = 100

        if len(self.frames) == 1:
            self.config(image=self.frames[0])
        else:
            self.next_frame()

    def unload(self):
        self.config(image=None)
        self.frames = None
        self.loc = 0
        self.cancel()

    def next_frame(self):
        if self.frames:
            self.loc += 1
            self.loc %= len(self.frames)
            self.config(image=self.frames[self.loc])
            self.after_id = self.after(self.delay, self.next_frame)

    def cancel(self):
        if hasattr(self, 'after_id'):
            self.after_cancel(self.after_id)
            del self.after_id


root = tk.Tk()
root.geometry("800x600")
root['bg'] = "#303030"
root.title("Bird generator")
root.resizable(False, False)
style = ttk.Style()
style.theme_use('default')

label = ttk.Label(root, text="Type a description of a bird:", style="TLabel")
style.configure("TLabel", foreground="#da95e6", background=root['bg'], font=("Helvetica", 16, "bold"))
label.pack(pady=10)

text_input = tk.Text(root, width=20, height=3, wrap="word", font=("Helvetica", 12))
text_input.pack(pady=10)

frame = tk.Frame(root, bg=root['bg'])
frame.pack(pady=10)

button = ttk.Button(frame, text="Generate!", style="TButton",
                    command=lambda: threading.Thread(target=generate_image).start())
style.configure("TButton", foreground="#da95e6", background="#36013F", color="black",
                font=("Helvetica", 12, "bold"), padding=10, borderwidth=0, focuscolor="#36013F")
button.pack(side=tk.LEFT, padx=10, pady=10)

image_label = ImageLabel(root, background=root['bg'])
image_label.pack(pady=10)

warning_label = ttk.Label(root, text="", style="Warning.TLabel")
style.configure("Warning.TLabel", foreground="#FF0000", background=root['bg'], font=("Helvetica", 8))
warning_label.pack(pady=10)

save_button = ttk.Button(frame, text="Save image", style="TButton", state=tk.DISABLED,
                         command=lambda: threading.Thread(target=save_image).start())
save_button.pack(side=tk.RIGHT, padx=10, pady=10)

root.mainloop()
