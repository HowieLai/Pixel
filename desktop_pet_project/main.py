import sys
import os
from PySide6.QtWidgets import QWidget, QApplication, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QSize, QPoint, QTimer

class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()
        self.drag_position = None # For window dragging
        self.is_on_top = True # For always on top toggle

        # Initial window flags
        self.update_window_flags()

        # Set attributes
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Image and animation setup
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.character_images_path = os.path.join(self.script_dir, "assets", "characters")

        self.character_states = self.load_character_images()

        # Robust check for essential images, especially 'idle'
        if not self.character_states or not self.character_states.get("idle") or self.character_states.get("idle").isNull():
            print("Critical Error: Essential 'idle' character image is missing or invalid.")
            print("Application will use a fallback red square for 'idle' and may not function correctly for other states.")
            # Create a fallback for 'idle' if it's missing or the whole dict is missing
            fallback_idle_pixmap = QPixmap(100, 100)
            fallback_idle_pixmap.fill(Qt.red)
            if not self.character_states:
                self.character_states = {} # Initialize if None
            self.character_states["idle"] = fallback_idle_pixmap
            # Ensure other states have at least a None to prevent crashes if called, or use fallback too
            for state_key in ["happy", "sleepy"]:
                if not self.character_states.get(state_key):
                     self.character_states[state_key] = fallback_idle_pixmap # or None

        self.current_state_image = self.character_states.get("idle")
        # Final check, should not be needed if above logic is correct, but as a safeguard:
        if not self.current_state_image or self.current_state_image.isNull():
             print("Error: 'idle' state is still problematic. Using dark gray fallback.")
             self.current_state_image = QPixmap(100,100)
             self.current_state_image.fill(Qt.darkGray)

        # Create a label to display the image
        self.image_label = QLabel(self)
        self.image_label.setPixmap(self.current_state_image)
        self.image_label.setScaledContents(True)

        # Resize label and window to the initial image size (or a fixed size)
        # Assuming all character images are the same size (e.g., 100x100)
        fixed_size = QSize(100, 100)
        self.image_label.setFixedSize(fixed_size)
        self.resize(fixed_size) # Resize main window

        self.image_label.show()

        # Animation timer
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate_idle)
        self.animation_timer.start(3000) # 3 seconds interval
        self.idle_cycle_count = 0

        # Show the main window
        self.show()

    def load_character_images(self):
        states = ["idle", "happy", "sleepy"]
        loaded_pixmaps = {}
        all_loaded = True
        for state in states:
            path = os.path.join(self.character_images_path, f"{state}.png")
            pixmap = QPixmap(path)
            if pixmap.isNull():
                print(f"Error: Could not load image for state '{state}' at {path}")
                all_loaded = False
                # Optionally, load a fallback for this specific state or skip
                # For simplicity, we'll rely on the initial check after this function.
            loaded_pixmaps[state] = pixmap

        # If any essential image failed, the caller can decide how to handle it.
        # Return the dictionary. If any image failed to load, all_loaded will be False.
        # __init__ will then decide how to handle this (e.g., use fallbacks).
        return loaded_pixmaps # No longer returning None from here, __init__ inspects content


    def animate_idle(self):
        self.idle_cycle_count += 1
        current_emotion_state = "idle" # Default state

        if self.idle_cycle_count % 4 == 0: # Every 4th tick, try to switch to sleepy
            current_emotion_state = "sleepy"

        # Attempt to set the new state
        new_pixmap = self.character_states.get(current_emotion_state)

        if new_pixmap and not new_pixmap.isNull():
            self.current_state_image = new_pixmap
            self.image_label.setPixmap(self.current_state_image)
            print(f"Animation: Switched to {current_emotion_state}")
        else:
            # Error: The desired pixmap is missing or invalid.
            print(f"Error: Pixmap for state '{current_emotion_state}' is missing or invalid.")
            # Optionally, revert to 'idle' if the current state was not 'idle' and 'idle' is available
            if current_emotion_state != "idle":
                idle_pixmap = self.character_states.get("idle")
                if idle_pixmap and not idle_pixmap.isNull():
                    self.current_state_image = idle_pixmap
                    self.image_label.setPixmap(self.current_state_image)
                    print("Animation: Fallback to 'idle' state due to missing pixmap for target state.")
                else:
                    print("Animation: 'idle' state also missing/invalid. No change in display.")
            else:
                print("Animation: Already in 'idle' state or 'idle' state is problematic. No change in display.")


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # globalPosition() returns a QPointF, convert to QPoint for subtraction if necessary
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def update_window_flags(self):
        flags = Qt.FramelessWindowHint | Qt.Tool
        if self.is_on_top:
            flags |= Qt.WindowStaysOnTopHint
        else:
            # To ensure it's not on top, we can also set WindowStaysOnBottomHint
            # However, some window managers might interpret this differently.
            # For now, just not setting WindowStaysOnTopHint might be enough.
            # flags |= Qt.WindowStaysOnBottomHint # Optional
            pass # No specific flag to keep it "normal" other than not being on top
        self.setWindowFlags(flags)
        # Important: After changing window flags, you might need to hide and show the window
        # or call self.show() again if it's already visible.
        # self.show() # This can cause flickering if not handled carefully

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_T: # Toggle with 'T' key
            self.is_on_top = not self.is_on_top
            self.update_window_flags()
            # Re-show the window to apply flag changes
            # This is crucial for flags like WindowStaysOnTopHint to take effect reliably.
            self.show()
            print(f"Window always on top: {self.is_on_top}")
            event.accept()
        else:
            super().keyPressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DesktopPet()
    sys.exit(app.exec())
