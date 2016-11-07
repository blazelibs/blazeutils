import logging


def clear_handlers_by_attr(attr, logger=logging.root):
    new_handlers = []
    for h in logger.handlers:
        if getattr(h, attr, False):
            h.flush()
            h.close()
        else:
            new_handlers.append(h)
    logger.handlers = new_handlers
