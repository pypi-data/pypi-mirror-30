class ProgressBar(object):
        
    def __init__(self, fill='█', empty=' ', size=100, prefix='progress', current=0, buffer=100, show_percentage=True, show_balance=True, precision=2):
        """
        @params:
        
            fill                - Optional  : Bar fill character, default █ (Str)
            empty               - Optional  : Bar empty character, default blank space (Str)
            size                - Optional  : Bar size (Int)
            prefix              - Optional  : Prefix string (Str)
            current             - Optional  : Initial position (Int)
            buffer              - Optional  : Buffer size (Int)
            show_percentage     - Optional  : If True, the percentage is shown at the end, example 80% (Bool)
            show_balance        - Optional  : If True, the balance is shown at the end, example (80/100) (Bool)
            precision           - Optional  : Float precision (Int)

        >>> progress_bar = ProgressBar(size=50, show_balance=True)
        >>> progress_bar.update_progress(10, 100, True)
        >>> progress_bar.complete()

        """
        self.prefix = prefix
        self.fill = fill
        self.empty = empty
        self.size = size
        self.prefix = prefix

        self.show_percentage = show_percentage
        self.show_balance = show_balance

        self.current = current
        self.buffer = buffer
        self.precision = '.{}f'.format(precision)
        self.calculate_percentage()

    def calculate_percentage(self):
        """
        The percentage of progress is calculated
        """
        
        percentage = (self.current * 100) / self.buffer
        self.percentage_completed = float(format(percentage, self.precision))
        self.completed = self.percentage_completed == 100

    def percentage_format(self):
        return " {}%".format(self.percentage_completed) if self.show_percentage else ''

    def balance_format(self):
        return " ({}/{})".format(self.current, self.buffer) if self.show_balance else ''

    def skip_format(self):
        return "\n" if self.completed or self.skip else ""

    def bar_format(self):
        """
        Create and return the progress string
        """

        progress = int((self.percentage_completed * self.size)/100)
        outout_fill = self.fill * progress
        outout_empty = self.empty * int(self.size - progress)

        return "{}{}".format(outout_fill, outout_empty)

    def standout(self):
        """
        Create and return the full progress bar string with or without percentage or balance
        """

        return "\r{} |{}|{}{}{}".format(self.prefix, self.bar_format(), self.percentage_format(), self.balance_format(), self.skip_format())

    def update_progress(self, current, buffer, skip=False):
        """
        Updates the current, buffer and the skip attributes
        Shows in console the full progress bar sring
        """
        
        self.current, self.buffer, self.skip = current, buffer, skip

        if self.current <= self.buffer:
            self.calculate_percentage()
            self.show_progress()
        else:
            self.complete()

    def complete(self):
        """
        Updates the current attribute
        Fills the progress bar
        """

        self.current = self.buffer
        self.update_progress(self.current, self.buffer)

    def show_progress(self):
        """
        Shows in the console, in the same line the progress bar
        """
        import sys

        sys.stdout.write(self.standout())
        sys.stdout.flush()

