class StickyStatusBar:
    def __init__(self, initial_text):
        self.initial_text = initial_text
        self.update(initial_text)

    def update(self, text):
        # ANSI escape codes for white background and black text
        styled_text = f"\033[47m\033[30m {text} \033[0m"  # 47 for white background
        print(f"\0337{styled_text}\r\0338", end="", flush=True)

    def clear(self):
        print("\033[K\r", end="", flush=True)