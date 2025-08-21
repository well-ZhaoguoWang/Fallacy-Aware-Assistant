import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json
import threading
import time
from tkinter import font
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class FloatingWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.is_collapsed = False
        self.is_animating = False
        self.expanded_size = (450, 600)
        self.collapsed_size = (60, 60)
        self.expanded_position = None  # remembers the top-left corner when expanded
        self.setup_window()
        self.create_widgets()
        self.flask_url = "http://localhost:5000"
        self.check_flask_connection()

    def setup_window(self):
        """Borderless, always-on-top, semi-transparent window anchored top-right."""
        self.root.title("Logical Fallacy Detector")
        self.root.geometry(f"{self.expanded_size[0]}x{self.expanded_size[1]}")
        self.root.minsize(300, 400)

        try:
            self.root.iconphoto(False, tk.PhotoImage(file="icon.png"))
        except:
            pass

        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        self.root.attributes('-alpha', 0.96)
        self.root.configure(bg='#2c3e50')

        screen_width = self.root.winfo_screenwidth()
        initial_x = screen_width - self.expanded_size[0] - 20
        initial_y = 20
        self.root.geometry(f"{self.expanded_size[0]}x{self.expanded_size[1]}+{initial_x}+{initial_y}")
        self.expanded_position = (initial_x, initial_y)

        self.bind_drag_events()

    def bind_drag_events(self):
        self.drag_data = {"x": 0, "y": 0}

    def start_drag(self, event):
        self.drag_data["x"] = event.x_root - self.root.winfo_x()
        self.drag_data["y"] = event.y_root - self.root.winfo_y()

    def drag_window(self, event):
        x = event.x_root - self.drag_data["x"]
        y = event.y_root - self.drag_data["y"]
        self.root.geometry(f"+{x}+{y}")

        # Keep expanded-position consistent when the icon is dragged in collapsed state
        if self.is_collapsed:
            self.expanded_position = (x - (self.expanded_size[0] - self.collapsed_size[0]), y)
        else:
            self.expanded_position = (x, y)

    def create_widgets(self):
        self.main_frame = tk.Frame(self.root, bg='#2c3e50', bd=0)
        self.main_frame.pack(fill='both', expand=True, padx=2, pady=2)

        self.create_custom_border()
        self.create_expanded_interface()
        self.create_collapsed_interface()
        self.show_expanded()

    def create_custom_border(self):
        # Title bar
        self.title_bar = tk.Frame(self.main_frame, bg='#34495e', height=40)
        self.title_bar.pack(fill='x', side='top')
        self.title_bar.pack_propagate(False)

        title_label = tk.Label(
            self.title_bar,
            text="🔍 Logical Fallacy Detector",
            font=("Arial", 11, "bold"),
            bg='#34495e',
            fg='#ecf0f1',
            anchor='w'
        )
        title_label.pack(side='left', padx=15, pady=8)

        control_frame = tk.Frame(self.title_bar, bg='#34495e')
        control_frame.pack(side='right', padx=5)

        self.collapse_btn = tk.Button(
            control_frame, text="─", font=("Arial", 12, "bold"),
            bg='#f39c12', fg='white', bd=0, width=3, height=1,
            cursor='hand2', command=self.toggle_collapse
        )
        self.collapse_btn.pack(side='left', padx=2)

        close_btn = tk.Button(
            control_frame, text="✕", font=("Arial", 10, "bold"),
            bg='#e74c3c', fg='white', bd=0, width=3, height=1,
            cursor='hand2', command=self.close_window
        )
        close_btn.pack(side='left', padx=2)

        # Make title bar draggable
        self.title_bar.bind('<Button-1>', self.start_drag)
        self.title_bar.bind('<B1-Motion>', self.drag_window)
        title_label.bind('<Button-1>', self.start_drag)
        title_label.bind('<B1-Motion>', self.drag_window)

    def create_expanded_interface(self):
        self.content_frame = tk.Frame(self.main_frame, bg='#2c3e50')
        self.content_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.create_status_indicator()
        self.create_news_input()
        self.create_comment_input()
        self.create_buttons()
        self.create_result_area()
        self.create_bottom_info()

    def create_status_indicator(self):
        status_frame = tk.Frame(self.content_frame, bg='#2c3e50')
        status_frame.pack(fill='x', pady=5)

        self.status_canvas = tk.Canvas(status_frame, width=12, height=12, bg='#2c3e50', highlightthickness=0)
        self.status_canvas.pack(side='left')
        self.status_dot = self.status_canvas.create_oval(2, 2, 10, 10, fill='#e74c3c', outline='')

        self.status_label = tk.Label(
            status_frame, text="Checking service connection...",
            font=("Arial", 9), bg='#2c3e50', fg='#bdc3c7'
        )
        self.status_label.pack(side='left', padx=8)

    def create_news_input(self):
        news_label = tk.Label(
            self.content_frame, text="📰 News Background",
            font=("Arial", 10, "bold"), bg='#2c3e50', fg='#ecf0f1'
        )
        news_label.pack(anchor='w', pady=(15, 5))

        news_frame = tk.Frame(self.content_frame, bg='#34495e', bd=1, relief='solid')
        news_frame.pack(fill='x', pady=5)

        self.news_text = scrolledtext.ScrolledText(
            news_frame, height=4, wrap=tk.WORD, font=("Arial", 9),
            bg='#34495e', fg='#ecf0f1', bd=0, highlightthickness=0,
            insertbackground='#ecf0f1', selectbackground='#3498db'
        )
        self.news_text.pack(fill='both', expand=True, padx=2, pady=2)

    def create_comment_input(self):
        comment_label = tk.Label(
            self.content_frame, text="💬 Comment Content",
            font=("Arial", 10, "bold"), bg='#2c3e50', fg='#ecf0f1'
        )
        comment_label.pack(anchor='w', pady=(15, 5))

        comment_frame = tk.Frame(self.content_frame, bg='#34495e', bd=1, relief='solid')
        comment_frame.pack(fill='x', pady=5)

        self.comment_text = scrolledtext.ScrolledText(
            comment_frame, height=4, wrap=tk.WORD, font=("Arial", 9),
            bg='#34495e', fg='#ecf0f1', bd=0, highlightthickness=0,
            insertbackground='#ecf0f1', selectbackground='#3498db'
        )
        self.comment_text.pack(fill='both', expand=True, padx=2, pady=2)

    def create_buttons(self):
        button_frame = tk.Frame(self.content_frame, bg='#2c3e50')
        button_frame.pack(fill='x', pady=15)

        self.detect_button = tk.Button(
            button_frame, text="🔍 Detect Fallacies", command=self.detect_fallacy,
            font=("Arial", 10, "bold"), bg='#3498db', fg='white', bd=0,
            padx=25, pady=10, cursor='hand2', relief='flat'
        )
        self.detect_button.pack(side='left', padx=5)

        clear_button = tk.Button(
            button_frame, text="🗑️ Clear", command=self.clear_text,
            font=("Arial", 10), bg='#95a5a6', fg='white', bd=0,
            padx=25, pady=10, cursor='hand2', relief='flat'
        )
        clear_button.pack(side='left', padx=5)

        self.add_button_hover_effect(self.detect_button, '#2980b9', '#3498db')
        self.add_button_hover_effect(clear_button, '#7f8c8d', '#95a5a6')

    def create_result_area(self):
        result_label = tk.Label(
            self.content_frame, text="📊 Detection Results",
            font=("Arial", 10, "bold"), bg='#2c3e50', fg='#ecf0f1'
        )
        result_label.pack(anchor='w', pady=(15, 5))

        result_frame = tk.Frame(self.content_frame, bg='#34495e', bd=1, relief='solid')
        result_frame.pack(fill='both', expand=True, pady=5)

        self.result_text = scrolledtext.ScrolledText(
            result_frame, height=6, wrap=tk.WORD, font=("Arial", 9),
            bg='#34495e', fg='#ecf0f1', bd=0, highlightthickness=0,
            state='disabled', insertbackground='#ecf0f1', selectbackground='#3498db'
        )
        self.result_text.pack(fill='both', expand=True, padx=2, pady=2)

    def create_bottom_info(self):
        bottom_frame = tk.Frame(self.content_frame, bg='#2c3e50')
        bottom_frame.pack(fill='x', pady=5)

        info_label = tk.Label(
            bottom_frame,
            text="💡 Ctrl+Enter for quick detection | Click ─ to collapse window",
            font=("Arial", 8), bg='#2c3e50', fg='#7f8c8d'
        )
        info_label.pack()

        self.root.bind('<Control-Return>', lambda e: self.detect_fallacy())

    def create_collapsed_interface(self):
        self.collapsed_frame = tk.Frame(self.main_frame, bg='#3498db')

        # Try icon.png; if unavailable, fall back to a simple canvas icon
        try:
            self.icon_image = tk.PhotoImage(file="icon.png")
            self.icon_image = self.icon_image.subsample(
                max(1, self.icon_image.width() // 48),
                max(1, self.icon_image.height() // 48)
            )
            self.icon_label = tk.Label(self.collapsed_frame, image=self.icon_image, bg='#3498db', bd=0)
            self.icon_label.pack(expand=True, fill='both')
            self.bind_collapsed_events_to_label()
        except tk.TclError:
            self.create_default_icon()

    def bind_collapsed_events_to_label(self):
        """Treat short stationary clicks as toggle; longer movement as drag."""
        self.click_start_time = 0
        self.drag_threshold = 5
        self.start_pos = None

        def on_button_press(event):
            self.click_start_time = time.time()
            self.start_pos = (event.x_root, event.y_root)
            self.start_drag(event)

        def on_button_release(event):
            if self.start_pos:
                dx = abs(event.x_root - self.start_pos[0])
                dy = abs(event.y_root - self.start_pos[1])
                if dx < self.drag_threshold and dy < self.drag_threshold and (time.time() - self.click_start_time) < 0.3:
                    self.toggle_collapse()

        def on_motion(event):
            if self.start_pos:
                dx = abs(event.x_root - self.start_pos[0])
                dy = abs(event.y_root - self.start_pos[1])
                if dx > self.drag_threshold or dy > self.drag_threshold:
                    self.drag_window(event)

        self.icon_label.bind('<Button-1>', on_button_press)
        self.icon_label.bind('<ButtonRelease-1>', on_button_release)
        self.icon_label.bind('<B1-Motion>', on_motion)

    def create_default_icon(self):
        self.icon_canvas = tk.Canvas(self.collapsed_frame, width=56, height=56, bg='#3498db', highlightthickness=0)
        self.icon_canvas.pack(padx=2, pady=2)
        self.icon_canvas.create_oval(2, 2, 54, 54, fill='#2980b9', outline='#1abc9c', width=2)
        self.icon_canvas.create_text(28, 28, text="🔍", font=("Arial", 20), fill='white')
        self.bind_collapsed_events()

    def bind_collapsed_events(self):
        """Same click-vs-drag logic for the canvas fallback."""
        self.click_start_time = 0
        self.drag_threshold = 5
        self.start_pos = None

        def on_button_press(event):
            self.click_start_time = time.time()
            self.start_pos = (event.x_root, event.y_root)
            self.start_drag(event)

        def on_button_release(event):
            if self.start_pos:
                dx = abs(event.x_root - self.start_pos[0])
                dy = abs(event.y_root - self.start_pos[1])
                if dx < self.drag_threshold and dy < self.drag_threshold and (time.time() - self.click_start_time) < 0.3:
                    self.toggle_collapse()

        def on_motion(event):
            if self.start_pos:
                dx = abs(event.x_root - self.start_pos[0])
                dy = abs(event.y_root - self.start_pos[1])
                if dx > self.drag_threshold or dy > self.drag_threshold:
                    self.drag_window(event)

        for widget in [self.icon_canvas, self.collapsed_frame]:
            widget.bind('<Button-1>', on_button_press)
            widget.bind('<ButtonRelease-1>', on_button_release)
            widget.bind('<B1-Motion>', on_motion)

    def add_button_hover_effect(self, button, hover_color, normal_color):
        def on_enter(e):
            button.config(bg=hover_color)

        def on_leave(e):
            button.config(bg=normal_color)

        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)

    def toggle_collapse(self):
        if self.is_animating:
            return
        self.is_animating = True
        if self.is_collapsed:
            self.show_expanded()
        else:
            self.show_collapsed()
        self.is_collapsed = not self.is_collapsed
        self.is_animating = False

    def show_expanded(self):
        self.collapsed_frame.pack_forget()
        self.title_bar.pack(fill='x', side='top')
        self.content_frame.pack(fill='both', expand=True, padx=10, pady=5)

        if self.expanded_position:
            x, y = self.expanded_position
            self.root.geometry(f"{self.expanded_size[0]}x{self.expanded_size[1]}+{x}+{y}")
        else:
            self.root.geometry(f"{self.expanded_size[0]}x{self.expanded_size[1]}")

        self.root.minsize(300, 400)
        self.collapse_btn.config(text="─")

    def show_collapsed(self):
        # Collapse to the top-right corner of the expanded rectangle
        if not self.is_collapsed:
            self.expanded_position = (self.root.winfo_x(), self.root.winfo_y())

        self.title_bar.pack_forget()
        self.content_frame.pack_forget()
        self.collapsed_frame.pack(fill='both', expand=True)

        if self.expanded_position:
            exp_x, exp_y = self.expanded_position
            collapsed_x = exp_x + self.expanded_size[0] - self.collapsed_size[0]
            collapsed_y = exp_y
        else:
            screen_width = self.root.winfo_screenwidth()
            collapsed_x = screen_width - self.collapsed_size[0] - 20
            collapsed_y = 20

        self.root.geometry(f"{self.collapsed_size[0]}x{self.collapsed_size[1]}+{collapsed_x}+{collapsed_y}")
        self.root.minsize(60, 60)

    def close_window(self):
        self.root.destroy()

    def check_flask_connection(self):
        """Ping Flask service; disable the Detect button until reachable."""
        def check():
            try:
                requests.get(f"{self.flask_url}/", timeout=3)
                self.update_status("Service connection normal", "#27ae60")
                if hasattr(self, 'detect_button'):
                    self.detect_button.config(state='normal')
            except:
                self.update_status("Service connection failed", "#e74c3c")
                if hasattr(self, 'detect_button'):
                    self.detect_button.config(state='disabled')
                # Retry after 5 seconds
                self.root.after(5000, self.check_flask_connection)

        threading.Thread(target=check, daemon=True).start()

    def update_status(self, text, color):
        if hasattr(self, 'status_label'):
            self.status_label.config(text=text)
            self.status_canvas.itemconfig(self.status_dot, fill=color)

    def detect_fallacy(self):
        """Send request to /moderate and display the result."""
        if self.is_collapsed:
            self.toggle_collapse()
            return

        news = self.news_text.get("1.0", tk.END).strip()
        comment = self.comment_text.get("1.0", tk.END).strip()

        if not news or not comment:
            messagebox.showwarning("Warning", "Please enter news background and comment content")
            return

        # Loading state
        self.detect_button.config(text="🔄 Detecting...", state='disabled', bg='#f39c12')
        self.update_result("🔄 Analyzing, please wait...")

        def detect():
            try:
                resp = requests.post(
                    f"{self.flask_url}/moderate",
                    json={"news_text": news, "comment_text": comment, "language": "en"},
                    timeout=30
                )
                if resp.status_code == 200:
                    result = resp.json()
                    if result.get("ok"):
                        self.update_result(result.get("data", "Detection completed"))
                    else:
                        self.update_result(f"❌ Error: {result.get('msg', 'Unknown error')}")
                else:
                    self.update_result(f"❌ Request failed: HTTP {resp.status_code}")
            except requests.exceptions.Timeout:
                self.update_result("⏱️ Request timeout, please check network connection or service status")
            except requests.exceptions.ConnectionError:
                self.update_result("🔌 Connection failed, please ensure Flask service is running")
            except Exception as e:
                self.update_result(f"❌ Detection failed: {str(e)}")
            finally:
                # Restore button state
                self.root.after(0, lambda: self.detect_button.config(
                    text="🔍 Detect Fallacies", state='normal', bg='#3498db'
                ))

        threading.Thread(target=detect, daemon=True).start()

    def update_result(self, text):
        if hasattr(self, 'result_text'):
            self.result_text.config(state='normal')
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert("1.0", text)
            self.result_text.config(state='disabled')

    def clear_text(self):
        if hasattr(self, 'news_text'):
            self.news_text.delete("1.0", tk.END)
        if hasattr(self, 'comment_text'):
            self.comment_text.delete("1.0", tk.END)
        self.update_result("")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = FloatingWindow()
    app.run()
