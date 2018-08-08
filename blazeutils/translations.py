import contextlib
import gettext
import json
import os
import pkg_resources

import babel.messages.mofile
import babel.messages.frontend
import babel.support
import six
import speaklater
from babel.messages.pofile import read_po
from distutils.errors import DistutilsOptionError


def enclose_package_path_exists(package_name):
    """
    Returns a `path_exists` method that searches within the specified package
    """
    # NOTE: I don't really like the `enclose_...` name, if anyone wants to
    #       refactor this name, please feel free
    provider = pkg_resources.get_provider(package_name)
    return provider.has_resource


def find_mo_filename(domain=None, localedir=None, languages=None, all=False, package_name=None, extension='mo'):
    """
    Search the filesystem and package for an appropriate .mo file, and return the path
    (or `None`, if not found)
    """
    if languages is not None:
        if not isinstance(languages, (list, tuple)):
            languages = [languages]

        languages = [str(language) for language in languages]


    for attempted_domain in (None, domain, package_name):
        if not attempted_domain:
            attempted_domain = babel.support.Translations.DEFAULT_DOMAIN

        for attempted_package_name in (
                None,
                package_name
        ):
            filename = None

            attempted_dirnames = [localedir]
            if package_name:
                attempted_dirnames.extend([
                    'locale',
                    'i18n'
                ])

            for attempted_dirname in attempted_dirnames:
                path_exists = (
                    enclose_package_path_exists(package_name)
                    if attempted_package_name is not None
                    else None
                )
                filename = gettext_find(attempted_domain, attempted_dirname, languages, all, path_exists=path_exists, extension=extension)
                if filename:
                    break

            if filename:
                break

        if filename:
            break

    # `filename` could be an empty string or an empty list; if so, normalize it to `None`
    if not filename:
        return None

    return filename


def get_mo_data(dirname=None, locales=None, domain=None, package_name=None):
    """
    Finds the .mo data for the specified parameters, and returns the binary data.
    If the .mo file cannot be found or read, returns `None`
    """
    mo_filename = find_mo_filename(localedir=dirname, languages=locales, domain=domain, package_name=package_name)

    if mo_filename is None:
        return None

    if package_name is not None:
        opener = package_open
        opener_args = (package_name, mo_filename)

    else:
        opener = open
        opener_args = (mo_filename, 'rb')

    with opener(*opener_args) as f:
        resource_data = f.read()

    return resource_data


def gettext_find(domain, localedir=None, languages=None, all=False, path_exists=None, extension='mo'):
    """
    Locate a file using the `gettext` strategy.

    This is a straight copy of `gettext.find`, with the addition of the injected parameters
    """

    if path_exists is None:
        path_exists = os.path.exists

    # Get some reasonable defaults for arguments that were not supplied
    if localedir is None:
        localedir = gettext._default_localedir
    if languages is None:
        languages = []
        for envar in ('LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG'):
            val = os.environ.get(envar)
            if val:
                languages = val.split(':')
                break
        if 'C' not in languages:
            languages.append('C')
    # now normalize and expand the languages
    nelangs = []
    for lang in languages:
        for nelang in gettext._expand_lang(lang):
            if nelang not in nelangs:
                nelangs.append(nelang)
    # select a language
    if all:
        result = []
    else:
        result = None
    for lang in nelangs:
        if lang == 'C':
            break
        mofile = os.path.join(localedir, lang, 'LC_MESSAGES', '%s.%s' % (domain, extension))
        mofile_lp = os.path.join("/usr/share/locale-langpack", lang,
                                 'LC_MESSAGES', '%s.%s' % (domain, extension))

        # first look into the standard locale dir, then into the
        # langpack locale dir

        # standard mo file
        if path_exists(mofile):
            if all:
                result.append(mofile)
            else:
                return mofile

        # langpack mofile -> use it
        if path_exists(mofile_lp):
            if all:
                result.append(mofile_lp)
            else:
                return mofile_lp

    return result


def load_translations(dirname=None, locales=None, domain=None, package_name=None):
    """
    Find the .mo data for the specified parameters, and returns the translations.
    If the .mo file cannot be found or read, returns `None`
    """
    mo_data = get_mo_data(dirname, locales, domain, package_name)
    if mo_data is None:
        return babel.support.NullTranslations()

    with six.BytesIO(mo_data) as fp:
        translations = babel.support.Translations(fp=fp,
                                                  domain=domain or package_name)

    return translations


@contextlib.contextmanager
def package_open(package_name, filename):
    """
    Provides a context manager for opening a file within a package.
    If successful, the file will be opened in binary reading mode.

    Example:
        with package_open('some_package', 'path/to/file') as f:
            data = f.read()
    """
    provider = pkg_resources.get_provider(package_name)
    if not provider.has_resource(filename):
        raise FileNotFoundError('No such file or directory [{}]: {}'.format(package_name, filename))

    manager = pkg_resources.ResourceManager()

    with six.BytesIO(provider.get_resource_string(manager, filename)) as f:
        yield f


def write_json(outfile, catalog, use_fuzzy=False):
    """Write `catalog` as JSON text to the specified `outfile`"""
    messages = list(catalog)
    if not use_fuzzy:
        messages[1:] = [message for message in messages[1:] if not message.fuzzy]
    messages.sort()

    jscatalog = {}
    for message in messages:
        message_id = message.id
        if isinstance(message_id, (tuple, list)):
            message_id = message_id[0]

        jscatalog[message_id] = message.string

    jscatalog[""] = {
        'language': str(catalog.locale),
        'plural-forms': catalog.plural_forms
    }

    outfile.write(
        json.dumps(
            jscatalog,
            indent=4
        )
    )


class CompileJson(babel.messages.frontend.compile_catalog):
    """Provide a distutils `compile-json` command"""

    description = 'compile message catalogs to JSON files'
    user_options = babel.messages.frontend.compile_catalog.user_options + [
        ('output-dir=', 'u',
         'path to output directory'),
    ]

    def initialize_options(self):
        super(CompileJson, self).initialize_options()
        self.output_dir = None

    def finalize_options(self):
        super(CompileJson, self).finalize_options()
        if not self.output_dir:
            self.output_dir = self.directory

    def _run_domain(self, domain):
        # copied from `babel.messages.frontend.compile_catalog._run_domain`,
        #  * switched out 'mo' for 'json'
        #  * added `output_dir` option

        po_files = []
        json_files = []

        if not self.input_file:
            if self.locale:
                po_files.append((self.locale,
                                 os.path.join(self.directory, self.locale,
                                              'LC_MESSAGES',
                                              domain + '.po')))
                json_files.append(os.path.join(self.output_dir, self.locale,
                                               'LC_MESSAGES',
                                               domain + '.json'))
            else:
                for locale in os.listdir(self.directory):
                    po_file = os.path.join(self.directory, locale,
                                           'LC_MESSAGES', domain + '.po')
                    if os.path.exists(po_file):
                        po_files.append((locale, po_file))
                        json_files.append(os.path.join(self.output_dir, locale,
                                                       'LC_MESSAGES',
                                                       domain + '.json'))
        else:
            po_files.append((self.locale, self.input_file))
            if self.output_file:
                json_files.append(self.output_file)
            else:
                json_files.append(os.path.join(self.output_dir, self.locale,
                                               'LC_MESSAGES',
                                               domain + '.json'))

        if not po_files:
            raise DistutilsOptionError('no message catalogs found')

        for idx, (locale, po_file) in enumerate(po_files):
            json_file = json_files[idx]
            with open(po_file, 'rb') as infile:
                catalog = read_po(infile, locale)

            if self.statistics:
                translated = 0
                for message in list(catalog)[1:]:
                    if message.string:
                        translated += 1
                percentage = 0
                if len(catalog):
                    percentage = translated * 100 // len(catalog)
                self.log.info(
                    '%d of %d messages (%d%%) translated in %s',
                    translated, len(catalog), percentage, po_file
                )

            if catalog.fuzzy and not self.use_fuzzy:
                self.log.info('catalog %s is marked as fuzzy, skipping', po_file)
                continue

            for message, errors in catalog.check():
                for error in errors:
                    self.log.error(
                        'error: %s:%d: %s', po_file, message.lineno, error
                    )

            self.log.info('compiling catalog %s to %s', po_file, json_file)

            if not os.path.exists(os.path.dirname(json_file)):
                os.makedirs(os.path.dirname(json_file))

            with open(json_file, 'w') as outfile:
                write_json(outfile, catalog, use_fuzzy=self.use_fuzzy)


class LocalizationRegistry:
    """Handles updating registered translators when the active locale needs to change"""

    def __init__(self):
        self._locales = None

        self.translators = set()
        self.locales = None

    @property
    def locales(self):
        return self._locales

    @locales.setter
    def locales(self, value):
        if (
                value is not None and
                not isinstance(value, (tuple, list))
        ):
            value = [value]

        if value != self._locales:
            self._locales = value

            # now that we've updated the locale, we need to load the new translations (if they're available)
            for translator in self.translators:
                translator.locales = self._locales

    def subscribe(self, translator):
        self.translators.add(translator)

    def unsubscribe(self, translator):
        self.translators.remove(translator)


class Manager:
    """Manages translations"""

    mo_finder = find_mo_filename
    translations_loader = load_translations

    def __init__(self, dirname=None, locales=None, domain=None, package_name=None):
        self._locales = None
        self.translations = None

        self.dirname = dirname
        self.domain = domain
        self.package_name = package_name

        # `locales` has a setter that depends on the other values, so needs to be
        # initialized last
        self.locales = locales

    @property
    def locales(self):
        return self._locales

    @locales.setter
    def locales(self, value):
        if (
                value is not None and
                not isinstance(value, (tuple, list))
        ):
            value = [value]

        if (
                value != self._locales or
                self.translations is None
        ):
            self._locales = value

            # now that we've updated the locale, we need to load the new translations (if they're available)
            self.translations = self.translations_loader(self.dirname, self.locales, self.domain, self.package_name)

    def gettext(self, string, **variables):
        translations = self.translations

        # translate string
        translated_string = (
            string
            if translations is None
            else translations.gettext(string)
        )

        return (
            translated_string
            if not variables
            else translated_string.format(**variables)
        )

    def lazy_gettext(self, string, **variables):
        return speaklater.make_lazy_string(self.gettext, string, **variables)

    def lazy_ngettext(self, singular, plural, num, **variables):
        return speaklater.make_lazy_string(self.ngettext, singular, plural, num, **variables)

    def ngettext(self, singular, plural, num, **variables):
        variables.setdefault('num', num)

        string_to_translate = (
            singular
            if num == 1
            else plural
        )
        return self.gettext(string_to_translate, **variables)

    def configure_jinja_environment(self, jinja_environment):
        jinja_environment.add_extension('jinja2.ext.i18n')

        install_gettext_translations = getattr(
            jinja_environment,
            'install_gettext_translations',
            lambda *args: None
        )
        install_gettext_translations(self.translations)

        def fmf(domain=None, localedir=None, languages=None, all=False, package_name=None, extension='mo'):
            if domain is None:
                domain = self.domain

            if languages is None:
                languages = self.locales

            if package_name is None:
                package_name = self.package_name

            return self.mo_finder(
                domain=domain,
                localedir=localedir,
                languages=languages,
                all=all,
                package_name=package_name,
                extension=extension
            )

        jinja_environment.globals.update(find_mo_filename=fmf)


# Create a default registry singleton
registry = LocalizationRegistry()
