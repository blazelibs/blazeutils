import sys

import mock
from nose.tools import eq_

import blazeutils.rst
from blazeutils.testing import FailLoader, raises

ds_rst = """
Heading 1
=========

An introductory paragraph.

Heading 2.1
-----------

Secondary stuff.

Heading 2.2
-----------

More secondary stuff."""

ds_html = """<div class="section" id="heading-1">
<h1>Heading 1</h1>
<p>An introductory paragraph.</p>
<div class="section" id="heading-2-1">
<h2>Heading 2.1</h2>
<p>Secondary stuff.</p>
</div>
<div class="section" id="heading-2-2">
<h2>Heading 2.2</h2>
<p>More secondary stuff.</p>
</div>
</div>
"""

docinfo_rst = """
:f1: field value 1
:f2: field value 2
:f3: field
    value 3
:f2: 2 again

sometext

some more text
"""

class TestRST(object):

    def assert_eq(self, rst, html, **kwargs):
        converted = blazeutils.rst.rst2html(rst, **kwargs)
        assert isinstance(converted, unicode)
        eq_(html, converted)

    def test_document_structure(self):
        self.assert_eq(ds_rst, ds_html)

    def test_simple_inline(self):
        self.assert_eq(
            'This is *important*.',
            u'<p>This is <em>important</em>.</p>\n'
        )

    def test_settings(self):
        converted = blazeutils.rst.rst2html(ds_rst, doctitle_xform=True)
        # with doctitle_xform=True, the first heading should be promoted to
        # document title and therefore disappear from the body
        assert converted.startswith('<p>An introductory')

    def test_docinfo(self):
        pub = blazeutils.rst.rst2pub(docinfo_rst)
        expect = {u'f1': u'field value 1', u'f2': u'2 again', u'f3': u'field\nvalue 3'}
        eq_(expect, blazeutils.rst.doctree2dict(pub.document))

class TestNoDocutils(object):

    @classmethod
    def setup_class(cls):
        cls.fl = fl = FailLoader()
        fl.modules_from_package('docutils')
        sys.meta_path.append(fl)
        fl.delete_from_sys_modules()
        reload(blazeutils.rst)

    @classmethod
    def teardown_class(cls):
        sys.meta_path.remove(cls.fl)
        reload(blazeutils.rst)

    @raises(ImportError, 'docutils library is required')
    def test_no_docutils(self):
        blazeutils.rst.rst2html('foo')

toc_rst = """
Heading 1
=========

An introductory paragraph.

Heading 1.1
-----------

Heading 1.1.1
+++++++++++++

Heading 1.1.2
+++++++++++++

Heading 1.2
-----------

Heading 1.2.1
+++++++++++++

Heading 1.2.2
+++++++++++++
"""

all_headings_toc_html = """
<ul class="simple">
<li><a class="reference internal" href="#heading-1" id="toc-ref-1">Heading 1</a><ul>
<li><a class="reference internal" href="#heading-1-1" id="toc-ref-2">Heading 1.1</a><ul>
<li><a class="reference internal" href="#heading-1-1-1" id="toc-ref-3">Heading 1.1.1</a></li>
<li><a class="reference internal" href="#heading-1-1-2" id="toc-ref-4">Heading 1.1.2</a></li>
</ul>
</li>
<li><a class="reference internal" href="#heading-1-2" id="toc-ref-5">Heading 1.2</a><ul>
<li><a class="reference internal" href="#heading-1-2-1" id="toc-ref-6">Heading 1.2.1</a></li>
<li><a class="reference internal" href="#heading-1-2-2" id="toc-ref-7">Heading 1.2.2</a></li>
</ul>
</li>
</ul>
</li>
</ul>
""".lstrip()

depth2_toc_html = """
<ul class="simple">
<li><a class="reference internal" href="#heading-1" id="toc-ref-1">Heading 1</a></li>
</ul>
""".lstrip()

excluded_section_toc_html = """
<ul class="simple">
<li><a class="reference internal" href="#heading-1-1" id="toc-ref-1">Heading 1.1</a><ul>
<li><a class="reference internal" href="#heading-1-1-1" id="toc-ref-2">Heading 1.1.1</a></li>
<li><a class="reference internal" href="#heading-1-1-2" id="toc-ref-3">Heading 1.1.2</a></li>
</ul>
</li>
<li><a class="reference internal" href="#heading-1-2" id="toc-ref-4">Heading 1.2</a><ul>
<li><a class="reference internal" href="#heading-1-2-1" id="toc-ref-5">Heading 1.2.1</a></li>
<li><a class="reference internal" href="#heading-1-2-2" id="toc-ref-6">Heading 1.2.2</a></li>
</ul>
</li>
</ul>
""".lstrip()

href_prefix_toc_html = """
<ul class="simple">
<li><a class="reference external" href="some-page.html#heading-1" id="toc-ref-1">Heading 1</a></li>
</ul>
""".lstrip()

class TestCreatToc(object):

    def test_all_headings(self):
        pub = blazeutils.rst.rst2pub(toc_rst)
        pub, _ = blazeutils.rst.create_toc(pub.document, exclude_first_section=False)
        eq_(all_headings_toc_html, pub.writer.parts['body'])

    def test_depth(self):
        pub = blazeutils.rst.rst2pub(toc_rst)
        pub, _ = blazeutils.rst.create_toc(pub.document, exclude_first_section=False, depth=1)
        eq_(depth2_toc_html, pub.writer.parts['body'])

    def test_excluded_section(self):
        pub = blazeutils.rst.rst2pub(toc_rst)
        pub, _ = blazeutils.rst.create_toc(pub.document)
        eq_(excluded_section_toc_html, pub.writer.parts['body'])

    def test_href_prefix(self):
        pub = blazeutils.rst.rst2pub(toc_rst)
        pub, _ = blazeutils.rst.create_toc(pub.document, exclude_first_section=False, depth=1, href_prefix='some-page.html')
        eq_(href_prefix_toc_html, pub.writer.parts['body'])
