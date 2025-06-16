import sys
import os
from PySide6.QtWidgets import QWidget, QApplication, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QSize, QPoint

class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()
        self.drag_position = None # For window dragging
        self.is_on_top = True # For always on top toggle

        # Initial window flags
        self.update_window_flags()

        # Set attributes
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set default window size (will be adjusted to image size)
        # self.resize(150, 150) # Commented out as we'll resize to pixmap

        # Create a label to display the image
        self.image_label = QLabel(self)

        # Load the image
        script_dir = os.path.dirname(os.path.realpath(__file__))
        image_path = os.path.join(script_dir, "assets", "placeholder_pet.png")

        pixmap = QPixmap(image_path)

        if pixmap.isNull():
            print(f"Error: Could not load image at {image_path}")
            # Create a fallback pixmap (e.g., a colored square)
            # For now, let's just print an error and the window might be empty or very small.
            # A real app would handle this more gracefully.
            fallback_pixmap = QPixmap(100, 100) # Create a 100x100 pixmap
            fallback_pixmap.fill(Qt.cyan) # Fill with a color
            pixmap = fallback_pixmap
            self.image_label.setText("Image Missing") # Show text if image fails

        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True) # Scale pixmap to label size

        # Resize label and window to a fixed size or pixmap size
        # For now, let's use a fixed size for predictability in the sandbox
        fixed_size = QSize(100, 100)
        self.image_label.setFixedSize(fixed_size)
        self.resize(fixed_size)

        # Ensure the label is visible if it's just added
        self.image_label.show()

        # Show the main window
        self.show()

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
