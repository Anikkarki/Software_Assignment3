import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageOps, ImageSequence
import tensorflow as tf
import numpy as np
import os
import threading
import queue

# Multiple decorators to check for file existence and supported image formats
def file_exists(func):
    def wrapper(*args, **kwargs):
        if args[0].image_path and os.path.isfile(args[0].image_path):
            return func(*args, **kwargs)
        else:
            messagebox.showerror('Error', 'File not found!')
            return None
    return wrapper

def supported_format(func):
    def wrapper(*args, **kwargs):
        if args[0].image_path and args[0].image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            return func(*args, **kwargs)
        else:
            messagebox.showerror('Error', 'Unsupported file format! Only PNG/JPG/JPEG allowed')
            return None
    return wrapper

class ImageClassifier(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Image Classifier App")
        self.geometry("800x600")
        self.configure(bg="#f0f0f0")  # Change background color
        self.image_path = None  # Hidden variable that stores the image path
        self.model = self.load_model()  # Load pre-trained model
        self.loading_images = []  # List to hold frames of loading animation
        self.animation_label = None  # Label to display the loading animation
        self.result_queue = queue.Queue()  # Queue to hold classification results
        self.init_gui()  # Initialize user interface

    # Method for loading the pre-trained model
    def load_model(self):
        try:
            # Load a pre-trained EfficientNetB0 model from TensorFlow
            return EfficientNetB0(weights='imagenet')
        except Exception as e:
            messagebox.showerror('Model Error', f'Error loading AI model: {e}')
            self.quit()

    def init_gui(self):
        # Add a title label at the top
        self.title_label = tk.Label(self, text="AI Image Classifier", font=("Helvetica", 24, "bold"), bg="#f0f0f0")
        self.title_label.pack(pady=10)

        # Create main frame
        self.main_frame = tk.Frame(self, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create frames for image and results side by side
        self.image_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.image_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.result_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        self.result_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        # Buttons at the bottom
        self.button_frame = tk.Frame(self, bg="#f0f0f0")
        self.button_frame.pack(pady=10)

        # Define styles for buttons
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Helvetica', 12, 'bold'), padding=6)
        self.style.map('TButton', foreground=[('disabled', '#d9d9d9')])

        # Button to upload an image
        self.upload_btn = ttk.Button(self.button_frame, text="Upload Image", command=self.upload_image, style='TButton')
        self.upload_btn.pack(side=tk.LEFT, padx=10)

        # Button to classify the image (disabled by default)
        self.classify_btn = ttk.Button(self.button_frame, text="Classify Image", command=self.classify_image, style='TButton')
        self.classify_btn.pack(side=tk.LEFT, padx=10)
        self.classify_btn.state(['disabled'])  # Disable the button initially

        # Label to display the uploaded image
        self.image_label = tk.Label(self.image_frame, bg="#f0f0f0")
        self.image_label.pack()

        # Label to display the classification result
        self.result_label = tk.Label(self.result_frame, text="Classification Result:", font=("Helvetica", 16), bg="#f0f0f0", justify=tk.LEFT)
        self.result_label.pack(anchor='n')

        # Load animation frames
        self.load_animation_frames()

    def load_animation_frames(self):
        try:
            # Load an animated GIF
            loader_gif_path = os.path.join(os.path.dirname(__file__), 'loader.gif')
            print(f"Attempting to load loader.gif from: {loader_gif_path}")
            loader_gif = Image.open(loader_gif_path)
            self.loading_images = []
            for frame_number, frame in enumerate(ImageSequence.Iterator(loader_gif)):
                img = frame.copy()
                img = img.resize((50, 50), Image.LANCZOS)
                self.loading_images.append(ImageTk.PhotoImage(img.convert('RGBA')))
            print(f"Loaded {len(self.loading_images)} frames from loader.gif")
        except Exception as e:
            messagebox.showerror('Animation Error', f'An error occurred while loading animation frames:\n{e}')
            print(f"Error loading animation frames: {e}")
            self.loading_images = []

    # Method to animate the loader
    def animate_loader(self, frame=0):
        if not self.loading_images:
            print("No loading images available to animate.")
            return  # Exit the function if there are no loading images
        if self.animation_label is None:
            self.animation_label = tk.Label(self.result_frame, bg="#f0f0f0")
            self.animation_label.pack(pady=10)
        frame %= len(self.loading_images)
        self.animation_label.configure(image=self.loading_images[frame])
        self.animation_label.image = self.loading_images[frame]  # Keep a reference
        # Check if classification is still running
        if not self.classification_running:
            # Remove the loader animation
            self.animation_label.destroy()
            self.animation_label = None
            return
        self.after(100, self.animate_loader, frame + 1)

    # Method to upload an image
    def upload_image(self):
        self.image_path = filedialog.askopenfilename()
        if self.image_path:
            img = Image.open(self.image_path)
            img = ImageOps.contain(img, (350, 350))  # Resize image to fit
            img = ImageTk.PhotoImage(img)
            self.image_label.configure(image=img)
            self.image_label.image = img
            self.result_label.config(text="Classification Result:")
            if self.animation_label:
                self.animation_label.destroy()
                self.animation_label = None
            # Enable the classify button after image upload
            self.classify_btn.state(['!disabled'])

    # Decorators used to ensure file existence and supported image formats
    @file_exists
    @supported_format
    def classify_image(self):
        # Disable the classify button to prevent multiple clicks
        self.classify_btn.state(['disabled'])
        # Set classification running flag
        self.classification_running = True
        # Start the loader animation
        self.animate_loader()
        self.update_idletasks()

        # Start the classification in a new thread
        threading.Thread(target=self.run_classification).start()

    def run_classification(self):
        try:
            # Classification process
            img = Image.open(self.image_path).convert('RGB')  # Convert to RGB
            img_resized = img.resize((224, 224))
            img_array = np.array(img_resized)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = preprocess_input(img_array)  # Use EfficientNet's preprocessing

            print("Starting model prediction...")  # Debugging statement
            predictions = self.model.predict(img_array)
            print("Model prediction completed.")  # Debugging statement

            decoded_predictions = decode_predictions(predictions, top=3)[0]
            print("Decoded predictions obtained.")  # Debugging statement

            # Format the results with labels and confidence scores
            results_text = "Classification Result:\n"
            for i, (imagenet_id, label, confidence) in enumerate(decoded_predictions):
                results_text += f"{i+1}. {label.replace('_', ' ').title()} ({confidence*100:.2f}%)\n"

            # Put the result in the queue
            self.result_queue.put(results_text)
        except Exception as e:
            # Put the exception in the queue
            self.result_queue.put(e)
        finally:
            # Set classification running flag to False
            self.classification_running = False
            # Schedule GUI update
            self.after(0, self.process_classification_result)

    def process_classification_result(self):
        # Retrieve the result from the queue
        result = self.result_queue.get()
        # Hide animation
        if self.animation_label:
            self.animation_label.destroy()
            self.animation_label = None
        # Re-enable the classify button
        self.classify_btn.state(['!disabled'])
        if isinstance(result, Exception):
            messagebox.showerror('Classification Error', f'An error occurred during classification:\n{result}')
            print(f"Classification error: {result}")  # Debugging statement
        else:
            self.result_label.config(text=result, justify=tk.LEFT, font=("Helvetica", 14))

class EnhancedClassifier(ImageClassifier):
    def __init__(self):
        super().__init__()
        self.title("Enhanced AI Image Classifier App")  # Method overriding: Change window title
        self.geometry("800x700")  # Method overriding: Change window size

    # Polymorphism: Changing the behavior of classify_image to provide more output
    @file_exists
    @supported_format
    def classify_image(self):
        # Disable the classify button to prevent multiple clicks
        self.classify_btn.state(['disabled'])
        # Set classification running flag
        self.classification_running = True
        # Start the loader animation
        self.animate_loader()
        self.update_idletasks()

        # Start the classification in a new thread
        threading.Thread(target=self.run_classification).start()

    def run_classification(self):
        try:
            # Classification process
            img = Image.open(self.image_path).convert('RGB')  # Convert to RGB
            img_resized = img.resize((224, 224))
            img_array = np.array(img_resized)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = preprocess_input(img_array)

            print("Starting model prediction...")  # Debugging statement
            predictions = self.model.predict(img_array)
            print("Model prediction completed.")  # Debugging statement

            decoded_predictions = decode_predictions(predictions, top=5)[0]
            print("Decoded predictions obtained.")  # Debugging statement

            # Format the results with labels and confidence scores
            results_text = "Top 5 Classification Results:\n"
            for i, (imagenet_id, label, confidence) in enumerate(decoded_predictions):
                results_text += f"{i+1}. {label.replace('_', ' ').title()} ({confidence*100:.2f}%)\n"

            # Put the result in the queue
            self.result_queue.put(results_text)
        except Exception as e:
            # Put the exception in the queue
            self.result_queue.put(e)
        finally:
            # Set classification running flag to False
            self.classification_running = False
            # Schedule GUI update
            self.after(0, self.process_classification_result)

if __name__ == "__main__":
    app = EnhancedClassifier()
    app.mainloop()
