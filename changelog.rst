Changelog
---------

0.3.7 released ???
==========================

+ BC BREAK: changed testing.raises() to regex escape by default.  There is now a
    keyword arg to control regex escaping. Also switched it to be more lenient
    in its matching by using re.search() instead of re.match()
+ added exc_emailer() decorator

0.3.6 released 2011-08-19
==========================

- fix bug in sdist build

0.3.5 released 2011-08-18
==========================

+  XlwtHelper can now use XFStyle instances directly.

0.3.4 released 2011-06-11
==========================

+ deprecate error_handling.traceback_* functions
+ deprecate datetime module, moved safe_strftime to dates module
+ add decorators.deprecate() decorator
+ add testing.emits_deprecation() decorator (only usable w/ python >= 2.6)
+ add testing.raises() decorator
+ add dates module and ensure_date(), ensure_datetime()

0.3.3 released 2011-05-19
==========================
+ made moneyfmt/decimalfmt handle floats
