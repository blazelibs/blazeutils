try:
    import docutils
    from docutils.core import publish_programmatically
    import docutils.io as io
    have_docutils =  True
except ImportError, e:
    have_docutils = False

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

def doctree2dict(doctree):
    """
    Return the docinfo field list from a doctree

    Note: there can be multiple instances of a single field in the docinfo.
    Since a dictionary is returned, the last instance's value will win.

    Example:

        pub = rst2pub(rst_string)
        print doctree2dict(pub.document)
    """
    nodes = doctree.traverse(docutils.nodes.docinfo)
    md = {}
    for node in nodes[0]:
        # copied this logic from Sphinx, not exactly sure why they use it, but
        # I figured it can't hurt
        if isinstance(node, docutils.nodes.authors):
            md['authors'] = [author.astext() for author in node]
        elif isinstance(node, docutils.nodes.TextElement): # e.g. author
            md[node.__class__.__name__] = node.astext()
        else:
            name, body = node
            md[name.astext()] = body.astext()
    return md

def rst2html(rst_src, **kwargs):
    """
        Convert a reStructuredText string into a unicode HTML fragment.

        For `kwargs`, see `default_rst_opts` and
        http://docutils.sourceforge.net/docs/user/config.html
    """
    pub = rst2pub(rst_src, settings_overrides=kwargs, writer_name='html')
    return pub.writer.parts['body']
