import customtkinter as ctk
import tkinter as tk
import configparser as cp
import os


from src.utils.unit_conversion_updater import UnitConversionUpdater
from src.utils.translator import Translator
from src.utils.ctk_separator import CTkWindowSeparator
from src.utils.widget_walker import walk_widgets
from src.calculator import Calculator

# Constants for font styles and colors
LARGE_FONT = ("Source Sans Pro", 22, "bold")
SETTING_FONT = ("Source Sans Pro", 17)
SMALL_FONT = ("Source Sans Pro", 15)
SMALLEST_FONT = ("Source Sans Pro", 13)
COLOR_THEME = "green"

# Constants for language translations
translator = Translator()
global _
_ = translator.gettext


class MainConverter(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Converter")
        self._setup_ui()
        self.load_settings()
        self.mainloop()

    def _setup_ui(self):
        self._setup_window()
        self._setup_appearance()
        self._setup_panels()

    def _setup_window(self):
        self.geometry("860x520")
        self.resizable(0, 0)

    def _setup_appearance(self):
        if hasattr(self, "appearance_mode"):
            ctk.set_appearance_mode(self.appearance_mode)
        else:
            ctk.set_appearance_mode("system")
        ctk.set_default_color_theme(COLOR_THEME)

    def _setup_panels(self):
        self.right_panel = RightPanel(self)
        self.settings_panel = SettingsPanel(
            self, self.change_language_on_panels, self.save_settings
        )
        self.unit_updater = UnitConversionUpdater(
            self.right_panel.entries,
            self.settings_panel.remove_trailing_zeros_switch,
            self.settings_panel.current_significant_number,
        )
        self.left_panel = LeftPanel(
            self, self.settings_panel, self.toggle_settings, self.unit_updater
        )
        self._layout_panels()

    def _layout_panels(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        self.left_panel.grid(row=0, column=0, padx=(0, 20), sticky="nsw")
        self.right_panel.grid(row=0, column=1, padx=5, sticky="nsew")
        self.settings_panel.grid(row=0, column=1, padx=5, sticky="nsew")
        self.settings_panel.grid_remove()

    def toggle_settings(self):
        if self.settings_panel.winfo_ismapped():
            self.settings_panel.grid_remove()
            self.right_panel.grid()
        else:
            self.right_panel.grid_remove()
            self.settings_panel.grid()

    def change_language_on_panels(self, lang_code=None):
        if lang_code is None:
            lang_code = self.settings_panel.current_lang_code
        translator.change_language(lang_code)
        self.left_panel.update_ui()
        self.right_panel.update_ui()
        self.settings_panel.update_ui()

        # Reload the default category after language change
        self.unit_updater._load_default_category()

    def save_settings(self):
        config = cp.ConfigParser()
        config["Settings"] = {
            "AppearanceMode": str(self.settings_panel.new_mode),
            "ColorTheme": COLOR_THEME,
            "Language": str(self.settings_panel.current_lang_code),
            "RemoveTrailingZeros": str(self.settings_panel.remove_trailing_zeros.get()),
            "SignificantNumber": str(
                self.settings_panel.current_significant_number.get()
            ),
        }
        with open("settings.ini", "w") as configfile:
            config.write(configfile)

    def load_settings(self):
        config = cp.ConfigParser()
        if not os.path.exists("settings.ini"):
            self.save_settings()
        config.read("settings.ini")
        self.settings_panel.current_lang_code = config.get(
            "Settings", "Language", fallback=self.settings_panel.current_lang_code
        )
        self.settings_panel.remove_trailing_zeros.set(
            config.getboolean("Settings", "RemoveTrailingZeros", fallback=True)
        )
        self.settings_panel.current_significant_number.set(
            config.getint("Settings", "SignificantNumber", fallback=10)
        )
        self.appearance_mode = config.get(
            "Settings", "AppearanceMode", fallback="system"
        )
        self.settings_panel.new_mode = self.appearance_mode
        ctk.set_appearance_mode(self.appearance_mode)
        self.settings_panel.change_language(self.settings_panel.current_lang_code)


class LeftPanel(ctk.CTkScrollableFrame):
    CONVERSION_TYPES = [
        (_("Temperature")),
        (_("Area")),
        (_("Length")),
        (_("Volume")),
        (_("Time")),
        (_("Mass")),
        (_("Speed")),
        (_("Force")),
        (_("Fuel Consumption")),
        (_("Numeral Systems")),
        (_("Pressure")),
        (_("Energy")),
        (_("Power")),
        (_("Angles")),
        (_("Digital data")),
    ]

    def __init__(
        self,
        parent,
        setting_panel,
        setting_toggle,
        unit_updater,
    ):
        super().__init__(parent)
        self.setting_panel = setting_panel
        self.setting_toggle = setting_toggle
        self.unit_updater = unit_updater
        self.calc_window = None
        self._configure_grid()
        self._create_widgets()

    def _configure_grid(self):
        self.configure(width=210)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _create_widgets(self):
        self._create_label("PyConvert", LARGE_FONT, pady=0)
        self._create_settings_calc_buttons()
        self._add_conversion_buttons()

    def _create_label(self, text, font, **grid_kwargs):
        label = ctk.CTkLabel(self, text=text, font=font)
        label.grid(**grid_kwargs)

    def _create_settings_calc_buttons(self):
        ctk.CTkButton(
            self, text=_("Calculator"), font=SMALL_FONT, command=self._toggle_calculator
        ).grid(row=1, column=0, padx=0, pady=5)
        settings_button = ctk.CTkButton(
            self, text=(_("Settings")), font=SMALL_FONT, command=self._open_settings
        )
        settings_button.grid(row=2, column=0, padx=0, pady=5)
        separator = CTkWindowSeparator(self, size=3, length=80, color="#878787")
        separator.grid(row=3, column=0, pady=(5, 0))

    def _add_conversion_buttons(self):
        for row, conversion_type in enumerate(self.CONVERSION_TYPES, start=4):
            self._create_button(row, conversion_type)

    def _create_button(self, row, text):
        button = ctk.CTkButton(
            self,
            text=text,
            fg_color="transparent",
            border_color="red",
            text_color=("#000000", "#FFFFFF"),
            hover_color="#15905b",
            font=SMALL_FONT,
            corner_radius=10,
            command=lambda t=text: self._button_event(t),
        )
        button.grid(row=row, column=0, padx=0, pady=3)

    def _button_event(self, category_type):
        if self.setting_panel.winfo_ismapped():
            self.setting_toggle()
        self.unit_updater.load_category_from_button(category_type)

    def _open_settings(self):
        self.setting_toggle()

    def _toggle_calculator(self):
        if self.calc_window is None:
            self.calc_window = Calculator(self)
        else:
            self.calc_window.show_window()

    def update_ui(self):
        for widget in walk_widgets(self):
            if isinstance(widget, (ctk.CTkLabel, ctk.CTkButton)):
                original_text = getattr(widget, "_original_text", None)
                if original_text is None:
                    original_text = widget.cget("text")
                    setattr(widget, "_original_text", original_text)
                widget.configure(text=_(original_text))


class SettingsPanel(ctk.CTkFrame):
    LANGUAGE_OPTIONS = (
        ("en", _("English")),
        ("de", _("German")),
        ("fr", _("French")),
        ("es", _("Spanish")),
        ("it", _("Italian")),
        ("ru", _("Russian")),
    )
    TRANSLATED_LANGUAGE_NAMES = {code: _(name) for code, name in LANGUAGE_OPTIONS}
    APPEARANCE_OPTIONS = ("Light", "Dark", "System")
    APPEARANCE_OPTIONS_TRANSLATED = {
        "Light": _("Light"),
        "Dark": _("Dark"),
        "System": _("System"),
    }

    def __init__(self, parent, change_language_method, save_settings):
        super().__init__(parent)
        self.change_language = change_language_method
        self.save_settings = save_settings

        self.current_lang_code = self.LANGUAGE_OPTIONS[0][0]
        self.current_lang_name = ctk.StringVar(
            value=self.TRANSLATED_LANGUAGE_NAMES[self.current_lang_code]
        )
        self.language_codes = {_(name): code for code, name in self.LANGUAGE_OPTIONS}
        self.current_appearance = ctk.StringVar(value=_("System"))
        self.appearance_options = {_(name): name for name in self.APPEARANCE_OPTIONS}
        self.remove_trailing_zeros = ctk.BooleanVar(value=True)
        self.current_significant_number = ctk.IntVar(value=10)
        self.remove_trailing_zeros.trace_add("write", self.save_settings_wrapper)
        self.current_significant_number.trace_add("write", self.save_settings_wrapper)
        self.current_appearance.trace_add("write", self.save_settings_wrapper)

        self.new_mode = "System"

        self.about_window = None
        self.configure(fg_color="transparent")
        self._configure_grid()
        self._create_widgets()

    def _configure_grid(self):
        self.grid_columnconfigure(0, weight=1, uniform="B")
        self.grid_columnconfigure(1, weight=1, uniform="B")
        self.grid_rowconfigure(tuple(range(5)), weight=0)

    def _create_widgets(self):
        self._create_settings_label()
        self._create_language_optionmenu()
        self._create_appearance_mode_optionmenu()
        self._create_rm_trailing_zeros()
        self._create_significant_number_options()
        self._create_about_button()

    def _create_settings_label(self):
        ctk.CTkLabel(
            self,
            text=(_("Settings")),
            font=LARGE_FONT,
        ).grid(row=0, column=0, sticky="nw", pady=(40, 0), padx=(20, 0))

    def _create_language_optionmenu(self):
        ctk.CTkLabel(
            self,
            text=(_("Language:")),
            font=SETTING_FONT,
        ).grid(row=1, column=0, sticky="nw", pady=(10, 0), padx=(20, 0))

        ctk.CTkOptionMenu(
            self,
            values=list(self.TRANSLATED_LANGUAGE_NAMES.values()),
            variable=self.current_lang_name,
            dropdown_font=SMALLEST_FONT,
        ).grid(row=1, column=1, sticky="nw", pady=(10, 0), padx=(20, 0))

        self.current_lang_name.trace_add("write", self._on_language_change)

    def _on_language_change(self, *args):
        selected_lang_name = self.current_lang_name.get()
        self.current_lang_code = self.language_codes.get(selected_lang_name, "en")
        self.change_language(self.current_lang_code)
        self.TRANSLATED_LANGUAGE_NAMES = {
            code: _(name) for code, name in self.LANGUAGE_OPTIONS
        }
        self.current_lang_name.set(
            self.TRANSLATED_LANGUAGE_NAMES[self.current_lang_code]
        )
        self.save_settings()

    def update_ui(self):
        """Update the UI with the new language for the SettingsPanel."""
        for widget in walk_widgets(self):
            if isinstance(widget, (ctk.CTkLabel, ctk.CTkButton)):
                original_text = getattr(widget, "_original_text", None)
                if original_text is None:
                    original_text = widget.cget("text")
                    setattr(widget, "_original_text", original_text)
                widget.configure(text=_(original_text))
            elif isinstance(widget, ctk.CTkOptionMenu):
                if widget.cget("variable") == self.current_lang_name:
                    translated_values = list(self.TRANSLATED_LANGUAGE_NAMES.values())
                    translated_variable = self.TRANSLATED_LANGUAGE_NAMES[
                        self.current_lang_code
                    ]
                    widget.configure(values=translated_values)
                    widget.set(translated_variable)
                elif widget.cget("variable") == self.current_appearance:
                    self._update_appearance_options_translated()
                    self._update_appearance_options()

    def _update_appearance_options_translated(self):
        """Update the translated appearance options dictionary."""
        self.APPEARANCE_OPTIONS_TRANSLATED = {
            option: _(option) for option in self.APPEARANCE_OPTIONS
        }

        # Update the appearance option menu with the new translated values
        appearance_option_menu = self._get_appearance_option_menu()
        if appearance_option_menu:
            translated_values = list(self.APPEARANCE_OPTIONS_TRANSLATED.values())
            appearance_option_menu.configure(values=translated_values)
            appearance_option_menu.set(
                _(self.current_appearance.get())
            )  # Use translated value

    def _update_appearance_options(self):
        """Update the appearance options dictionary with the translated values."""
        self.appearance_options = {_(name): name for name in self.APPEARANCE_OPTIONS}

    def _get_appearance_option_menu(self):
        """Get the appearance option menu widget."""
        for widget in walk_widgets(self):
            if (
                isinstance(widget, ctk.CTkOptionMenu)
                and widget.cget("variable") == self.current_appearance
            ):
                return widget
        return None

    def _create_appearance_mode_optionmenu(self):
        """Create an option menu for appearance mode."""
        ctk.CTkLabel(self, text=_("Appearance:"), font=SETTING_FONT).grid(
            row=2, column=0, sticky="nw", pady=(10, 0), padx=(20, 0)
        )

        ctk.CTkOptionMenu(
            self,
            values=list(self.APPEARANCE_OPTIONS_TRANSLATED.values()),
            variable=self.current_appearance,
            dropdown_font=SMALLEST_FONT,
            command=self._change_appearance_mode,
        ).grid(row=2, column=1, sticky="nw", pady=(10, 0), padx=(20, 0))

    def _change_appearance_mode(self, *args):
        translated_mode = self.current_appearance.get()
        # Use the translated value to get the original English value
        self.new_mode = self.appearance_options[translated_mode]
        ctk.set_appearance_mode(self.new_mode)
        self.save_settings()

    def _create_significant_number_options(self):
        ctk.CTkLabel(self, text=_("Significant number:"), font=SETTING_FONT).grid(
            row=4, column=0, sticky="nw", pady=(10, 0), padx=(20, 0)
        )

        ctk.CTkOptionMenu(
            self,
            variable=self.current_significant_number,
            values=["4", "6", "8", "10", "12", "14", "16"],
            dropdown_font=SMALLEST_FONT,
        ).grid(row=4, column=1, sticky="nw", pady=(10, 0), padx=(20, 0))

    def _create_rm_trailing_zeros(self):
        ctk.CTkLabel(self, text=_("Remove trailing zeros"), font=SETTING_FONT).grid(
            row=5, column=0, sticky="nw", pady=(10, 0), padx=(20, 0)
        )

        self.remove_trailing_zeros_switch = ctk.CTkSwitch(
            self,
            text="",
            variable=self.remove_trailing_zeros,
        )
        self.remove_trailing_zeros_switch.grid(
            row=5, column=1, pady=(10, 0), sticky="nw", padx=(20, 0)
        )

    def _create_about_button(self):
        """Create an about button."""
        ctk.CTkButton(
            self,
            text=(_("About")),
            font=SMALL_FONT,
            command=self._open_about,
        ).grid(row=7, column=0, sticky="nw", pady=(10, 0), padx=(20, 0))

    def _open_about(self):
        if self.about_window is None or not self.about_window.winfo_exists():
            self.about_window = AboutWindow(self)
            self.about_window.transient(
                self
            )  # Make the About window transient to the main window
            self.about_window.grab_set()  # Set input focus to the About window
            self.about_window.lift()  # Bring the About window to the top
        else:
            self.about_window.lift()  # Bring the About window to the top if it already exists
            self.about_window.focus()  # Focus the About window if it already exists

    def save_settings_wrapper(self, *args):
        """Wrapper function for saving settings."""
        self.save_settings()


class AboutWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("600x420")
        self.title(_("About"))
        self._configure_grid()
        self._create_content()

    def _configure_grid(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _create_content(self):
        info_label = ctk.CTkLabel(
            self,
            text=self._get_license_text(),
            wraplength=550,
            justify="left",
            font=("Source Sans Pro", 12),
        )
        info_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def _get_license_text(self):
        license_text = (
            _(
                "MIT License\n\n"
                "Copyright (c) 2024 napHiwka\n\n"
                "Permission is hereby granted, free of charge, to any person obtaining a copy"
                'of this software and associated documentation files (the "Software"), to deal'
                "in the Software without restriction, including without limitation the rights"
                "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell"
                "copies of the Software, and to permit persons to whom the Software is"
                "furnished to do so, subject to the following conditions:\n\n"
                "The above copyright notice and this permission notice shall be included in all"
                "copies or substantial portions of the Software.\n\n"
                'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR'
                "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,"
                "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE"
                "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER"
                "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,"
                "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE"
                "SOFTWARE.\n\n"
            )
            + self._get_contact_info()
        )
        return license_text

    def _get_contact_info(self):
        return (
            _("For any inquiries or issues, please contact:\n") + "napHiwka@example.com"
        )


class RightPanel(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(fg_color="transparent")
        self._configure_grid()
        self.entries = self._create_entries()

    def _configure_grid(self):
        """Configures the grid for the RightPanel with specified weights and uniform."""
        self.grid_columnconfigure(0, weight=20, uniform="C")
        self.grid_columnconfigure(1, weight=5, uniform="C")
        self.grid_columnconfigure(2, weight=20, uniform="C")
        self.grid_columnconfigure(3, weight=5, uniform="C")
        self.grid_rowconfigure(tuple(range(8)), weight=1, uniform="C")

    def _create_entries(self):
        """Creates entries for the RightPanel and returns them as a list of tuples.
        Each tuple contains an entry, its symbol, its text, and its variable."""
        entries_list = [
            (self._create_entry(r, c)) for r in range(0, 18, 2) for c in [0, 2]
        ]
        return entries_list

    def _create_entry(self, row, column):
        """Creates a single entry at the given row and column, and returns it as a
        tuple with its symbol, text, and variable."""
        entry_var = ctk.StringVar()
        entry_text = self._create_label(row, column)
        entry = self._create_ctk_entry(row, column, entry_var)
        entry_symbol = self._create_symbol(row, column)
        return entry, entry_symbol, entry_text, entry_var

    def _create_label(self, row, column):
        """Creates a label at the given row and column, and returns it."""
        label = ctk.CTkLabel(
            self,
            text="",
            height=20,
            font=SMALLEST_FONT,
            text_color=("#000000", "gray62"),
        )
        label.grid(row=row, column=column, padx=12, pady=10, sticky="se")
        return label

    def _create_ctk_entry(self, row, column, entry_var):
        """Creates a CTkEntry at the given row and column, and returns it."""
        entry = ctk.CTkEntry(
            self, width=220, height=45, justify="right", textvariable=entry_var
        )
        entry.grid(row=row + 1, column=column, sticky="nsw")

        # Create a popup menu for the entry
        popup_menu = self._create_popup_menu(entry)

        # Bind the right-click event to the entry to show the popup menu
        entry.bind("<Button-3>", lambda event, menu=popup_menu: self.popup(event, menu))

        return entry

    def _create_popup_menu(self, entry):
        """Creates and returns a popup menu for the entry."""
        popup_menu = tk.Menu(self, tearoff=0)
        bg_color = "#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "white"
        fg_color = "white" if bg_color == "#2b2b2b" else "black"
        popup_menu.config(bg=bg_color, fg=fg_color)
        popup_menu.add_command(
            label=_("Copy"), command=lambda e=entry: self.copy_to_clipboard(e)
        )
        popup_menu.add_command(
            label=_("Paste"), command=lambda e=entry: self.paste_from_clipboard(e)
        )
        return popup_menu

    def _create_symbol(self, row, column):
        """Creates a symbol at the given row and column, and returns it."""
        symbol = ctk.CTkLabel(self, text="", font=SMALLEST_FONT, width=10)
        symbol.grid(row=row + 1, column=column + 1, sticky="w")
        return symbol

    def popup(self, event, menu):
        """Shows the popup menu at the cursor's position."""
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def copy_to_clipboard(self, entry=None):
        """Copies text from the entry to the clipboard.
        If entry is None, it copies text from the entry associated with the popup menu.
        """
        if entry is None:
            entry = self._get_entry_from_focus()

        selected_text = entry.selection_get() if entry.select_present() else entry.get()
        if selected_text:
            self.clipboard_clear()
            self.clipboard_append(selected_text)

    def paste_from_clipboard(self, entry=None):
        """Pastes the text from the clipboard into the entry.
        If entry is None, it pastes text into the entry associated with the popup menu.
        """
        if entry is None:
            entry = self._get_entry_from_focus()

        if entry:
            try:
                entry.delete("0", "end")
                entry.focus_force()
                entry.event_generate(
                    "<KeyPress>", keysym="v", state="0x0004"
                )  # Simulate Ctrl+V
                entry.event_generate(
                    "<KeyRelease>", keysym="v", state="0x0004"
                )  # Simulate Ctrl+V release
            except tk.TclError:
                pass  # No text in clipboard or other error

    def _get_entry_from_focus(self):
        """Returns the entry widget currently in focus."""
        focused_widget = self.focus_get()
        if isinstance(focused_widget, ctk.CTkEntry):
            return focused_widget
        return None

    def update_ui(self):
        """Update the UI with the new language for the RightPanel."""
        for widget in walk_widgets(self):
            if isinstance(widget, (ctk.CTkLabel, ctk.CTkButton)):
                original_text = getattr(widget, "_original_text", None)
                if original_text:
                    original_text = widget.cget("text")
                    setattr(widget, "_original_text", original_text)
                widget.configure(text=_(original_text))


if __name__ == "__main__":
    MainConverter()
