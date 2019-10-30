from __future__ import absolute_import
from __future__ import unicode_literals

try:
    import docutils
    from docutils.core import publish_programmatically, Publisher
    from docutils.transforms.parts import Contents
    import docutils.io as io
    from docutils.utils import new_document
    have_docutils = True
except ImportError:
    have_docutils = False

from blazeutils.datastructures import BlankObject

# see http://docutils.sourceforge.net/docs/user/config.html
default_rst_opts = {
    'no_generator': True,
    'no_source_link': True,
    'tab_width': 4,
    'stylesheet_path': None,
    'halt_level': 1,
    'doctitle_xform': False,
    'raw_enabled': False,
    'traceback': True,
    'file_insertion_enabled': False,
}


def rst2pub(source, source_path=None, source_class=None,
            destination_path=None,
            reader=None, reader_name='standalone',
            parser=None, parser_name='restructuredtext',
            writer=None, writer_name='pseudoxml',
            settings=None, settings_spec=None,
            settings_overrides=None, config_section=None,
            enable_exit_status=None):
    """
    Like docutils.core.publish_parts, but returns the publisher and sets
    some default settings, see `default_rst_opts`.

    Parameters: see `docutils.core` functions for explanation.

    Example:

        pub = rst2pub(rst_string)
        print doctree2dict(pub.document)

    """
    if not have_docutils:
        raise ImportError('docutils library is required to use reStructuredText conversion')

    final_settings_overrides = default_rst_opts.copy()
    if settings_overrides:
        final_settings_overrides.update(settings_overrides)

    source_class = source_class or io.StringInput

    output, pub = publish_programmatically(
        source=source, source_path=source_path, source_class=source_class,
        destination_class=io.StringOutput,
        destination=None, destination_path=destination_path,
        reader=reader, reader_name=reader_name,
        parser=parser, parser_name=parser_name,
        writer=writer, writer_name=writer_name,
        settings=settings, settings_spec=settings_spec,
        settings_overrides=final_settings_overrides,
        config_section=config_section,
        enable_exit_status=enable_exit_status)
    return pub


def docinfo2dict(doctree):
    """
    Return the docinfo field list from a doctree as a dictionary

    Note: there can be multiple instances of a single field in the docinfo.
    Since a dictionary is returned, the last instance's value will win.

    Example:

        pub = rst2pub(rst_string)
        print docinfo2dict(pub.document)
    """
    nodes = doctree.traverse(docutils.nodes.docinfo)
    md = {}
    if not nodes:
        return md
    for node in nodes[0]:
        # copied this logic from Sphinx, not exactly sure why they use it, but
        # I figured it can't hurt
        if isinstance(node, docutils.nodes.authors):
            md['authors'] = [author.astext() for author in node]
        elif isinstance(node, docutils.nodes.TextElement):  # e.g. author
            md[node.__class__.__name__] = node.astext()
        else:
            name, body = node
            md[name.astext()] = body.astext()
    return md

# deprecate eventually
doctree2dict = docinfo2dict  # noqa: E305


def create_toc(doctree, depth=9223372036854775807, writer_name='html',
               exclude_first_section=True, href_prefix=None, id_prefix='toc-ref-'):
    """
    Create a Table of Contents (TOC) from the given doctree

    Returns: (docutils.core.Publisher instance, output string)

    `writer_name`: represents a reST writer name and determines the type of
        output returned.

    Example:

        pub = blazeutils.rst.rst2pub(toc_rst)
        pub, html_output = blazeutils.rst.create_toc(pub.document)

        # a full HTML document (probably not what you want most of the time)
        print html_output

        # just the TOC
        print pub.writer.parts['body']
    """
    # copy the doctree since Content alters some settings on the original
    # document
    doctree = doctree.deepcopy()

    # we want to be able to customize ids to avoid clashes if needed
    doctree.settings.auto_id_prefix = id_prefix

    details = {
        'depth': depth,
    }

    # Assuming the document has one primary heading and then sub-sections, we
    # want to be able to give just the sub-sections
    startnode = None
    if exclude_first_section:
        nodes = doctree.traverse(docutils.nodes.section)
        if nodes:
            startnode = nodes[0]

    # use the Contents transform to build the TOC node structure from the
    # document
    c = Contents(doctree)
    # this startnode isn't really used as the start node, its only used for
    # to pull settings from
    c.startnode = BlankObject(details=details)
    # since this toc is detached from the rest of the document, we don't want
    # backlinks
    c.backlinks = 'none'
    # build the nodes
    toc_nodes = c.build_contents(startnode or doctree)

    # create a new document with the new nodes
    toc_doc = new_document(None)
    toc_doc += toc_nodes

    # fix fragements that reference the same page
    if href_prefix:
        prefix_refids(toc_doc, href_prefix)

    # setup a publisher and publish from the TOC document
    reader = docutils.readers.doctree.Reader(parser_name='null')
    pub = Publisher(
        reader, None, None,
        source=io.DocTreeInput(toc_doc),
        destination_class=io.StringOutput
    )
    pub.set_writer(writer_name)

    final_settings_overrides = default_rst_opts.copy()
    pub.process_programmatic_settings(
        None, final_settings_overrides, None)

    output = pub.publish()
    return pub, output


def rst2html(rst_src, **kwargs):
    """
        Convert a reStructuredText string into a unicode HTML fragment.

        For `kwargs`, see `default_rst_opts` and
        http://docutils.sourceforge.net/docs/user/config.html
    """
    pub = rst2pub(rst_src, settings_overrides=kwargs, writer_name='html')
    return pub.writer.parts['body']


def prefix_refids(document, href_prefix):
    # The href comes out as just a fragment, but its possible that the HTML
    # will be used on a page where relative links don't resolve to the current
    # page.  In that case, an href_prefix can be sent in.  The only downfall
    # to doing this way is that the writer automatically sets an "external"
    # class on a reference with 'refuri' instead of 'refid'.
    nodes = document.traverse(docutils.nodes.reference)
    for node in nodes:
        node['refuri'] = '{0}#{1}'.format(href_prefix, node['refid'])
        del node['refid']
