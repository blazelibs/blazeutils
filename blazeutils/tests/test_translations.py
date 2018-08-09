import contextlib
import json
import mock

import babel.support
import pytest
import six

from blazeutils import translations
from blazeutils.datastructures import BlankObject


class TestLocalizationRegistry:
    @pytest.fixture(scope='function')
    def registry(self):
        return translations.LocalizationRegistry()

    def test_subscribe(self, registry):
        translator_a = BlankObject(locales=None)
        translator_b = BlankObject(locales=None)
        assert translator_a not in registry.translators
        assert translator_b not in registry.translators

        registry.subscribe(translator_a)
        registry.subscribe(translator_b)
        assert translator_a in registry.translators
        assert translator_b in registry.translators

    def test_unsubscribe(self, registry):
        translator_a = BlankObject(locales=None)
        translator_b = BlankObject(locales=None)
        registry.subscribe(translator_a)
        registry.subscribe(translator_b)

        registry.unsubscribe(translator_a)
        assert translator_a not in registry.translators
        assert translator_b in registry.translators

    def test_locales_setter(self, registry):
        translator = BlankObject(locales=None)
        registry.subscribe(translator)

        registry.locales = 'asdf'
        assert ['asdf'] == registry.locales
        assert ['asdf'] == translator.locales


class TestManager:
    class NullManager(translations.Manager):
        def _translations_loader(self, *args, **kwargs):
            return babel.support.NullTranslations()

    @pytest.fixture(scope='function')
    def manager(self):
        return self.NullManager()

    @pytest.fixture(scope='function')
    def _(self, manager):
        return manager.gettext

    @pytest.fixture(scope='function')
    def _n(self, manager):
        return manager.ngettext

    def test_gettext(self, _):
        assert 'a' == _('a')
        assert 'hello world' == _('hello {name}', name='world')

    @pytest.mark.parametrize('num, expected', (
            (0, '0 are hello'),
            (1, '1 is hello'),
            (2, '2 are hello'),
    ))
    def test_ngettext(self, _n, num, expected):
        assert expected == _n('{num} is {word}', '{num} are {word}', num, word='hello')


class TestWriteJson:
    class MockMessage:
        def __init__(self, id, string, fuzzy=False):
            self.id = id
            self.string = string
            self.fuzzy = fuzzy

        def __lt__(self, other):
            return self.id < other.id

    class MockCatalog:
        def __init__(self, locale, plural_forms, mock_data):
            self.locale = locale
            self.plural_forms = plural_forms
            self.mock_data = mock_data

        def __len__(self):
            return len(self.mock_data)

        def __getitem__(self, item):
            return self.mock_data[item]

    @pytest.fixture
    def catalog(self):
        return self.MockCatalog(locale='es', plural_forms='1-many', mock_data=[
            self.MockMessage(id='foo', string='FOO'),
            self.MockMessage(id='bar', string='BAR', fuzzy=True),
        ])

    def test_write_fuzzy(self, catalog):
        with contextlib.closing(six.StringIO()) as f:
            translations.write_json(f, catalog, use_fuzzy=True)
            data = json.loads(f.getvalue())

        assert {
            '': {
                'language': 'es',
                'plural-forms': '1-many'
            },
            'foo': 'FOO',
            'bar': 'BAR',
        } == data

    def test_elide_fuzzy(self, catalog):
        with contextlib.closing(six.StringIO()) as f:
            translations.write_json(f, catalog, use_fuzzy=False)
            data = json.loads(f.getvalue())

        assert {
            '': {
                'language': 'es',
                'plural-forms': '1-many'
            },
            'foo': 'FOO'
        } == data


@mock.patch('pkg_resources.get_provider', autospec=True, spec_set=True)
def test_enclose_package_path_exists(get_provider):
    get_provider.return_value.has_resource.return_value = True

    path_exists = translations.enclose_package_path_exists('foobar')
    get_provider.assert_called_with('foobar')
    assert path_exists('bar/baz') is True


@mock.patch('blazeutils.translations.enclose_package_path_exists', autospec=True,
            spec_set=True, return_value=lambda path: False)
@mock.patch('blazeutils.translations.gettext_find', autospec=True, spec_set=True, return_value=None)
def test_find_mo_filename(gettext_find, enclose_package_path_exists):
    translations.find_mo_filename(domain='domain', localedir='localedir', languages=['es'],
                                  package_name='package_name', extension='ext')
    DEFAULT_DOMAIN = babel.support.Translations.DEFAULT_DOMAIN
    path_exists = enclose_package_path_exists.return_value

    # attempted_domain, attempted_dirname, languages, all, path_exists=path_exists
    assert [
        mock.call(DEFAULT_DOMAIN, 'localedir', ['es'], False, path_exists=None, extension='ext'),
        mock.call(DEFAULT_DOMAIN, 'locale', ['es'], False, path_exists=None, extension='ext'),
        mock.call(DEFAULT_DOMAIN, 'i18n', ['es'], False, path_exists=None, extension='ext'),
        mock.call(DEFAULT_DOMAIN, 'localedir', ['es'], False,
                  path_exists=path_exists, extension='ext'),
        mock.call(DEFAULT_DOMAIN, 'locale', ['es'], False,
                  path_exists=path_exists, extension='ext'),
        mock.call(DEFAULT_DOMAIN, 'i18n', ['es'], False, path_exists=path_exists, extension='ext'),

        mock.call('domain', 'localedir', ['es'], False, path_exists=None, extension='ext'),
        mock.call('domain', 'locale', ['es'], False, path_exists=None, extension='ext'),
        mock.call('domain', 'i18n', ['es'], False, path_exists=None, extension='ext'),
        mock.call('domain', 'localedir', ['es'], False, path_exists=path_exists, extension='ext'),
        mock.call('domain', 'locale', ['es'], False, path_exists=path_exists, extension='ext'),
        mock.call('domain', 'i18n', ['es'], False, path_exists=path_exists, extension='ext'),

        mock.call('package_name', 'localedir', ['es'], False, path_exists=None, extension='ext'),
        mock.call('package_name', 'locale', ['es'], False, path_exists=None, extension='ext'),
        mock.call('package_name', 'i18n', ['es'], False, path_exists=None, extension='ext'),
        mock.call('package_name', 'localedir', ['es'], False,
                  path_exists=path_exists, extension='ext'),
        mock.call('package_name', 'locale', ['es'], False,
                  path_exists=path_exists, extension='ext'),
        mock.call('package_name', 'i18n', ['es'], False, path_exists=path_exists, extension='ext'),
    ] == gettext_find.call_args_list


@mock.patch('blazeutils.translations.open', new_callable=mock.mock_open, read_data='asdf')
@mock.patch('blazeutils.translations.package_open', new_callable=mock.mock_open, read_data='ASDF')
@mock.patch('blazeutils.translations.find_mo_filename',
            autospec=True, spec_set=True, return_value='asdf.mo')
class TestGetMoData:
    def test_no_filename_found(self, find_mo_filename, *args):
        find_mo_filename.return_value = None
        assert translations.get_mo_data() is None

    def test_parameters(self, find_mo_filename, *args):
        find_mo_filename.return_value = None
        translations.get_mo_data(dirname='dirname', locales='locales', domain='domain',
                                 package_name='package_name')
        find_mo_filename.assert_called_with(localedir='dirname', languages='locales',
                                            domain='domain', package_name='package_name')

    def test_filesystem_opener(self, find_mo_filename, package_open, open):
        mo_data = translations.get_mo_data()
        assert not package_open.called
        open.assert_called_with('asdf.mo', 'rb')

        assert 'asdf' == mo_data

    def test_package_opener(self, find_mo_filename, package_open, open):
        mo_data = translations.get_mo_data(package_name='foo')
        assert not open.called
        package_open.assert_called_with('foo', 'asdf.mo')

        assert 'ASDF' == mo_data


@mock.patch('os.path.exists', autospec=True, spec_set=True)
class TestGettextFind:
    def test_os_path_exists(self, os_path_exists):
        translations.gettext_find('domain')
        assert os_path_exists.called

    def test_custom_path_exists(self, os_path_exists):
        custom_path_exists = mock.Mock()
        translations.gettext_find('domain', path_exists=custom_path_exists)

        assert not os_path_exists.called
        assert custom_path_exists.called


@mock.patch('blazeutils.translations.get_mo_data', autospec=True, spec_set=True)
class TestLoadTranslations:
    def test_load_fails(self, get_mo_data):
        get_mo_data.return_value = None
        translation = translations.load_translations()
        assert isinstance(translation, babel.support.NullTranslations)

    def test_load_parameters(self, get_mo_data):
        get_mo_data.return_value = None

        translations.get_mo_data(dirname='dirname', locales='locales', domain='domain',
                                 package_name='package_name')
        get_mo_data.assert_called_with(dirname='dirname', locales='locales',
                                       domain='domain', package_name='package_name')

    @mock.patch('babel.support.Translations', autospec=True, spec_set=True)
    def test_load(self, Translations, get_mo_data):
        get_mo_data.return_value = b'asdf'
        translations.load_translations()
        assert Translations.called


@mock.patch('pkg_resources.get_provider', autospec=True, spec_set=True)
class TestPackageOpen:
    def test_open_fails(self, get_provider):
        provider = get_provider.return_value
        provider.has_resource.return_value = False

        with pytest.raises(IOError):
            with translations.package_open('foobar', '/foo'):
                pass

    def test_open(self, get_provider):
        provider = get_provider.return_value
        provider.has_resource.return_value = True
        provider.get_resource_string.return_value = b'asdf'

        with translations.package_open('foobar', '/foo') as f:
            data = f.read()

        assert b'asdf' == data
