import customtkinter as ctk
import gettext

from src.utils.unit_conversion_updater import UnitConversionUpdater
from src.utils.ctk_separator import CTkWindowSeparator
from src.utils.settings import *


class LeftPanel(ctk.CTkScrollableFrame):
    def __init__(self, parent, right_panel_entries, setting_toggle, walk_widgets):
        super().__init__(parent)
        self._configure_grid()
        self._create_widgets()
        self.setting_toggle = setting_toggle
        self.walk_widgets = walk_widgets
        self.unit_updater = UnitConversionUpdater(right_panel_entries)

    def _configure_grid(self):
        """Configure the grid for the LeftPanel."""
        self.grid_columnconfigure(0, weight=1, uniform="A")
        self.grid_rowconfigure(tuple(range(12)), weight=1, uniform="A")

    def _create_widgets(self):
        """Create widgets for the LeftPanel."""
        self._create_label("PyConverter", LARGE_FONT, pady=0)  # Title creation
        self._create_settings_button()
        self._add_conversion_buttons()

    def _create_label(self, text, font=SMALL_FONT, row=0, column=0, **grid_kwargs):
        """Create a label with given text, font, row, column and grid_kwargs."""
        ctk.CTkLabel(self, text=text, font=font).grid(
            row=row, column=column, **grid_kwargs
        )

    def _create_settings_button(self):
        """Create a settings button."""
        ctk.CTkButton(
            self,
            text=(_("Settings")),
            font=SMALL_FONT,
            command=lambda: self._open_settings(),
        ).grid(row=1, column=0, padx=0, pady=0)
        CTkWindowSeparator(self, size=3, length=80, color="#878787").grid(
            row=2, column=0, pady=0
        )

    def _add_conversion_buttons(self):
        """Add buttons for each conversion type."""
        conversion_types = (
            (_("Temperature")),
            (_("Area")),
            (_("Length")),
            (_("Volume")),
            (_("Time")),
            (_("Weight")),
            (_("Speed")),
            (_("Force")),
            (_("Fuel Consumption")),
            (_("Numeral System")),
            (_("Pressure")),
            (_("Energy")),
            (_("Power")),
            (_("Angles")),
            (_("Shoe size")),
            (_("Digital data")),
        )

        for row, conversion_type in enumerate(conversion_types, start=3):
            self._create_button(row, conversion_type)

    def _create_button(self, row, text):
        """Create a button with given text and row."""
        ctk.CTkButton(
            self,
            text=text,
            font=SMALL_FONT,
            command=lambda: self._button_event(text),
        ).grid(row=row, column=0, padx=20, pady=3)

    def _button_event(self, category_type):
        """Handle button event for the given category_type."""
        self.unit_updater.load_category_from_button(category_type)

    def _open_settings(self):
        """Toggle between the settings window and the right panel."""
        self.setting_toggle()

    def update_ui(self):
        """Update the UI with the new language for the LeftPanel."""
        print("Updating UI for LeftPanel")  # Confirm update_ui is called
        for widget in self.walk_widgets(self):
            if isinstance(widget, ctk.CTkLabel) or isinstance(widget, ctk.CTkButton):
                # Update the text based on the widget's original text attribute
                original_text = getattr(widget, "_original_text", widget.cget("text"))
                translated_text = _(original_text)
                widget.configure(text=translated_text)
                # Save the original text if it hasn't been saved yet
                if not hasattr(widget, "_original_text"):
                    setattr(widget, "_original_text", original_text)


class SettingsPanel(ctk.CTkFrame):
    def __init__(self, parent, walk_widgets, change_language_method):
        super().__init__(parent)
        self.configure(fg_color="transparent")
        self._configure_grid()
        self.change_language = change_language_method
        self.walk_widgets = walk_widgets
        self.language_variable = ctk.StringVar(value="en")
        self.about_window = None
        self._create_widgets()

    def _configure_grid(self):
        self.grid_columnconfigure(0, uniform="B")
        self.grid_columnconfigure(1, uniform="B")
        self.grid_rowconfigure(tuple(range(5)), weight=0)

    def _create_widgets(self):
        self._create_settings_label()
        self._create_language_optionmenu()
        # self._crete_rm_trailing_zeros()  # TODO: Implement
        self._create_appearance_mode_optionmenu()
        self._create_about()

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
            font=SMALL_FONT,
        ).grid(row=1, column=0, sticky="nw", pady=(10, 0), padx=(20, 0))

        language_options = (
            ("en", _("English")),
            ("de", _("German")),
            ("fr", _("French")),
            ("es", _("Spanish")),
            ("it", _("Italian")),
            ("ru", _("Russian")),
        )
        self.language_variable.set(
            language_options[0][0]
        )  # Set default language to English

        # Create a dictionary to map language names to codes
        self.language_name_to_code = {name: code for code, name in language_options}

        ctk.CTkOptionMenu(
            self,
            values=[name for code, name in language_options],
            variable=self.language_variable,
            dropdown_font=SMALLEST_FONT,
        ).grid(row=1, column=1, sticky="nw", pady=(5, 0), padx=(20, 0))

        self.language_variable.trace_add("write", self._on_language_change)

    def _on_language_change(self, *args):
        lang_code = self.language_variable.get()
        print("Language variable changed to:", lang_code)
        self.change_language(lang_code)

    def update_ui(self):
        """Update the UI with the new language for the SettingsPanel."""
        print("Updating UI for SettingsPanel")
        for widget in self.walk_widgets(self):
            if isinstance(widget, ctk.CTkLabel) or isinstance(widget, ctk.CTkButton):
                # Update the text based on the widget's original text attribute
                original_text = getattr(widget, "_original_text", widget.cget("text"))
                translated_text = _(original_text)
                widget.configure(text=translated_text)
                # Save the original text if it hasn't been saved yet
                if not hasattr(widget, "_original_text"):
                    setattr(widget, "_original_text", original_text)

    def _create_appearance_mode_optionmenu(self):
        """Create an option menu for appearance mode."""
        ctk.CTkLabel(self, text=_("Appearance:"), font=SMALL_FONT).grid(
            row=2, column=0, sticky="nw", pady=(10, 0), padx=(20, 0)
        )

        appearance_options = (_("Light"), (_("Dark")), (_("System")))
        self.appearance_variable = ctk.StringVar(value=appearance_options[2])

        ctk.CTkOptionMenu(
            self,
            values=appearance_options,
            variable=self.appearance_variable,
            dropdown_font=SMALLEST_FONT,
            command=self._change_appearance_mode,
        ).grid(row=2, column=1, sticky="nw", pady=(5, 0), padx=(20, 0))

    def _change_appearance_mode(self, new_mode):
        """Change the appearance mode to the new_mode."""
        mode_mapping = {
            _("Light"): "Light",
            _("Dark"): "Dark",
            _("System"): "System",
        }
        ctk.set_appearance_mode(mode_mapping.get(new_mode, "System"))

    def _create_about(self):
        """Create an about button."""
        ctk.CTkButton(
            self,
            text=(_("About")),
            font=SMALL_FONT,
            command=self._open_about,
        ).grid(row=3, column=0, sticky="nw", pady=(10, 0), padx=(20, 0))

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


class AboutWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry("550x400")
        self.title("About")
        self._configure_grid()
        self._create_info()

    def _configure_grid(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _create_info(self):
        contact_info = _("For any inquiries or issues, please contact:\n")
        license_text = (
            (
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
            + contact_info
            + "napHiwka@example.com"
        )

        ctk.CTkLabel(self, text=license_text, wraplength=500, justify="left").grid(
            row=0, column=0, padx=10, pady=10, sticky="nsew"
        )


class RightPanel(ctk.CTkScrollableFrame):
    def __init__(self, parent, walk_widgets):
        super().__init__(parent)
        self.configure(fg_color="transparent")
        self._configure_grid()
        self.entries = self._create_entries()
        self.walk_widgets = walk_widgets

    def _configure_grid(self):
        """Configures the grid for the RightPanel with specified weights and uniform."""
        self.grid_columnconfigure(0, weight=25, uniform="C")
        self.grid_columnconfigure(1, weight=5, uniform="C")
        self.grid_columnconfigure(2, weight=25, uniform="C")
        self.grid_columnconfigure(3, weight=5, uniform="C")
        self.grid_rowconfigure(tuple(range(8)), weight=1, uniform="C")

    def _create_entries(self):
        """Creates entries for the RightPanel and returns them as a list of tuples.
        Each tuple contains an entry, its symbol, its text, and its variable."""
        entries_list = [
            (self._create_entry(r, c)) for r in range(0, 16, 2) for c in [0, 2]
        ]
        return entries_list

    def _create_entry(self, row, column):
        """Creates a single entry at the given row and column, and returns it as a
        tuple with its symbol, text, and variable."""
        entry_var = ctk.StringVar()
        entry_text = self._create_label(row, column)
        entry = self._create_ctk_entry(row, column, entry_var)
        entry_symbol = self._create_symbol(row, column)
        return (entry, entry_symbol, entry_text, entry_var)

    def _create_label(self, row, column):
        """Creates a label at the given row and column, and returns it."""
        label = ctk.CTkLabel(
            self,
            text="",
            height=20,
            font=SMALLEST_FONT,
            text_color=("gray52", "gray62"),
        )
        label.grid(row=row, column=column, padx=(0, 5), pady=10, sticky="se")
        return label

    def _create_ctk_entry(self, row, column, entry_var):
        """Creates a CTkEntry at the given row and column, and returns it."""
        entry = ctk.CTkEntry(
            self, width=220, height=40, justify="right", textvariable=entry_var
        )
        entry.grid(row=row + 1, column=column, sticky="nse")
        return entry

    def _create_symbol(self, row, column):
        """Creates a symbol at the given row and column, and returns it."""
        symbol = ctk.CTkLabel(self, text="", font=SMALL_FONT, width=10)
        symbol.grid(row=row + 1, column=column + 1, sticky="w", padx=(5, 0))
        return symbol

    def update_ui(self):
        """Update the UI with the new language for the RightPanel."""
        print("Updating UI for RightPanel")
        for widget in self.walk_widgets(self):
            if isinstance(widget, ctk.CTkLabel):
                original_text = getattr(widget, "_original_text", widget.cget("text"))
                if original_text:  # Check that original_text is not empty
                    translated_text = _(original_text)
                    widget.configure(text=translated_text)
                # Save the original text if it hasn't been saved yet
                if not hasattr(widget, "_original_text"):
                    setattr(widget, "_original_text", original_text)


class MainConverter(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Converter")
        self.setup_gettext()
        self._setup_ui()
        self.change_language()
        self.mainloop()

    def setup_gettext(self):
        # Set the default language to English or retrieve it from a config file
        default_lang = "en"
        localedir = "locales"  # Path to locales directory
        domain = "base"  # Name of the .po/.mo files
        gettext.bindtextdomain(domain, localedir)
        gettext.textdomain(domain)
        lang = gettext.translation(
            domain, localedir, languages=[default_lang], fallback=True
        )
        lang.install()
        global _  # Make the _ function global so it can be used throughout the file
        _ = lang.gettext

    def _setup_ui(self):
        """Setup the user interface by setting up the window, appearance and layout."""
        self._setup_window()
        self._setup_appearance()
        self._layout_panels()

    def _setup_window(self):
        """Setup the window with a specific geometry and make it non-resizable."""
        self.geometry("800x500")
        self.resizable(0, 0)

    def _setup_appearance(self):
        """Setup the appearance of the window with dark mode and a dark-blue theme."""
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

    def _layout_panels(self):
        """Configure the layout of panels with specific grid settings and positions."""
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        self.right_panel = RightPanel(self, self.walk_widgets)
        self.right_panel.grid(row=0, column=1, padx=5, sticky="nsew")

        self.settings_panel = SettingsPanel(
            self, self.walk_widgets, self.change_language
        )
        self.settings_panel.grid(row=0, column=1, padx=5, sticky="nsew")
        self.settings_panel.grid_remove()

        self.left_panel = LeftPanel(
            self, self.right_panel.entries, self.toggle_settings, self.walk_widgets
        )
        self.left_panel.grid(row=0, column=0, sticky="nsw")

    def toggle_settings(self):
        """Toggle between the settings window and the right panel."""
        if self.settings_panel.winfo_ismapped():
            # If the settings panel is currently visible, hide it and show the right panel
            self.settings_panel.grid_remove()
            self.right_panel.grid()
        else:
            # If the settings panel is not visible, hide the right panel and show the settings panel
            self.right_panel.grid_remove()
            self.settings_panel.grid()

    def change_language(self, lang_code=None):
        print("Changing language to", lang_code)
        if lang_code is None:
            lang_code = self.settings_panel.language_variable.get()
        localedir = "src/locales"
        domain = "base"
        translation = gettext.translation(
            domain, localedir=localedir, languages=[lang_code], fallback=True
        )
        translation.install()
        global _
        _ = translation.gettext
        print("Translation object:", translation)  # Print the translation object

        # Update the UI for all panels
        self.left_panel.update_ui()
        self.right_panel.update_ui()
        self.settings_panel.update_ui()

    def walk_widgets(self, parent):
        """Generator function to walk through all child widgets of a given parent widget."""
        for child in parent.winfo_children():
            yield child
            if child.winfo_children():
                yield from self.walk_widgets(child)


if __name__ == "__main__":
    MainConverter()
