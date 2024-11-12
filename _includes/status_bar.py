class StickyStatusBar:
    def __init__(self, initial_text):
        self.initial_text = initial_text
        self.update(initial_text)

    def update(self, text):
        print(f"\0337{text}\r\0338", end="", flush=True)  # Use \r for more reliable updates

    def clear(self):
        print("\033[K\r", end="", flush=True)  # Clear the line and reset cursor