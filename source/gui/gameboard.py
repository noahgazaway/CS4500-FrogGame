from tkinter import ttk, Tk, messagebox
from functools import partial
from datetime import datetime, timedelta
from gui.base import ContextBase
from localization import localizer
from util.utils import func_bundle


class GameboardContext(ContextBase):
    """
    The main game window. Has the gameboard, all game buttons, etc.
    """

    def __init__(self, *args, **kwargs) -> None:
        ContextBase.__init__(self, *args, **kwargs)

        self.start_time = None
        self.timer_task = None
        self.paused_time = None
        self.paused_delta = None

        self.rowconfigure(index=0, weight=5, minsize=100)
        self.rowconfigure(index=1, weight=90, minsize=100)
        self.rowconfigure(index=2, weight=5, minsize=100)
        # Title
        self.title = ttk.Label(
            self,
            justify="center",
            font=("-size", 30, "-weight", "bold"),
            text=localizer.get("GAME_TITLE"),
        )
        self.title.grid(row=0, column=1, padx=(10, 10), pady=(20, 10), sticky="n")

        self.timer = ttk.Label(
            self,
            justify="center",
            font=("-size", 18, "-weight", "bold"),
            text=localizer.get("TIMER_LABEL") + "00:00",
        )
        self.timer.grid(row=0, column=0, padx=(10, 10), pady=(20, 10), sticky="sw")

        self.help_btn = ttk.Button(
            self, text="HELP", command=partial(print, "TODO: GOTO HELP")
        )
        self.help_btn.grid(row=0, column=2, padx=(10, 10), sticky="se")

        # Middle panel
        self.scores_panel = ttk.Labelframe(
            self,
            padding=(5, 5),
        )
        self.scores_panel.grid(
            row=1, column=0, columnspan=self.num_columns, sticky="nsew"
        )

        # Bottom Buttons
        self.mainmenu_btn = ttk.Button(
            self,
            text=localizer.get("ARROW_LEFT") + localizer.get("MAIN_MENU_BUTTON"),
            command=partial(
                self.__confirm_quit, partial(print, "TODO: RETURN MAIN MENU")
            ),
        )
        self.mainmenu_btn.grid(row=2, column=0, padx=(10, 10), pady=(10, 10))

        self.pause_btn = ttk.Button(
            self, text=localizer.get("PAUSE_BUTTON"), command=self.__pause_timer
        )
        self.pause_btn.grid(row=2, column=1, padx=(10, 10), pady=(10, 10))

        self.highscores_btn = ttk.Button(
            self,
            text=localizer.get("HIGHSCORES_BUTTON") + localizer.get("ARROW_RIGHT"),
            command=partial(print, "TODO: GOTO LAST CONTEXT"),
        )
        self.highscores_btn.grid(row=2, column=2, padx=(10, 10), pady=(10, 10))

    def __confirm_quit(self, func) -> None:
        self.__pause_timer()
        ret = messagebox.askyesno(
            title="Are you sure?", message="Are you sure you want to quit?"
        )
        if ret:
            self.__stop_timer()
            func()

    def __update_timer(self) -> None:
        # Get the delta time from when we started the game to now
        d_time: timedelta = datetime.now() - self.start_time

        # If there is time on the paused delta subtract that
        if self.paused_delta:
            d_time = d_time - self.paused_delta

        # calcluate hrs, mins, and secs
        hours, rem = divmod(d_time.seconds, 3600)
        minutes, seconds = divmod(rem, 60)

        # If we have hours display that, if not do not
        if hours > 0:
            self.timer.configure(
                text=localizer.get("TIMER_LABEL")
                + f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            )
        else:
            self.timer.configure(
                text=localizer.get("TIMER_LABEL") + f"{minutes:02d}:{seconds:02d}"
            )

        # Run this function again in 1s
        self.timer_task = self.app.after(100, self.__update_timer)

    def start_timer(self) -> None:
        self.start_time = datetime.now()
        self.__update_timer()

    def __stop_timer(self) -> None:
        if self.timer_task:
            self.app.after_cancel(self.timer_task)
        # Change paused button to pause
        self.pause_btn.configure(
            text=localizer.get("PAUSE_BUTTON"), command=self.__pause_timer
        )
        self.paused_time = None
        self.paused_delta = None
        self.start_time = None
        self.timer_task = None

    def __pause_timer(self) -> None:
        if self.timer_task:
            # Remove the timer task and get the current time for when it was paused
            self.app.after_cancel(self.timer_task)
            self.timer_task = None
            self.paused_time = datetime.now()

            # Change pause button to unpause
            self.pause_btn.configure(
                text=localizer.get("UNPAUSE_BUTTON"), command=self.__unpause_timer
            )

    def __unpause_timer(self) -> None:
        if self.paused_time:
            # Add/set initial difference from when the clock was paused to now
            if self.paused_delta:
                self.paused_delta += datetime.now() - self.paused_time
            else:
                self.paused_delta = datetime.now() - self.paused_time

            # Change paused button to pause
            self.pause_btn.configure(
                text=localizer.get("PAUSE_BUTTON"), command=self.__pause_timer
            )

            # Reset when the clock was paused, and continue to update timer
            self.paused_time = None
            self.__update_timer()

    def set_mainmenu_cmd(self, command) -> None:
        self.mainmenu_btn.configure(command=partial(self.__confirm_quit, func=command))

    def set_highscores_cmd(self, command) -> None:
        # Pause timer on switching to leaderboard
        self.highscores_btn.configure(
            command=partial(func_bundle, (command, self.__pause_timer))
        )

    def set_help_cmd(self, command) -> None:
        self.help_btn.configure(command=command)


if __name__ == "__main__":
    root = Tk()
    app = GameboardContext(master=root, rows=3, columns=3, theme=None, name="")
    app.pack(fill="both", expand=True)

    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
    y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
    root.geometry("+{}+{}".format(x_cordinate, y_cordinate))
    root.mainloop()
