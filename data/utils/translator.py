import gettext


class Translator:
    def __init__(
        self,
        domain="base",
        localedir="src/locales",
        default_lang="en",
    ):
        self.domain = domain
        self.localedir = localedir
        self.default_lang = default_lang
        self.current_lang = None
        self.translation = None
        self.setup_gettext()

    def setup_gettext(self):
        gettext.bindtextdomain(self.domain, self.localedir)
        gettext.textdomain(self.domain)
        self.translation = gettext.translation(
            self.domain, self.localedir, languages=[self.default_lang], fallback=True
        )
        self.current_lang = self.default_lang
        self.translation.install()

    def change_language(self, lang_code):
        self.translation = gettext.translation(
            self.domain, self.localedir, languages=[lang_code], fallback=True
        )
        self.current_lang = lang_code
        self.translation.install()

    def gettext(self, message):
        return self.translation.gettext(message)
