
try:
    import xlwt
    
    class XlwtHelper(object):
        """
            code from : http://panela.blog-city.com/pyexcelerator_xlwt_cheatsheet_create_native_excel_from_pu.htm
        """
        
        STYLE_FACTORY = {}
        FONT_FACTORY = {}
        
        def __init__(self):
            self.ws = None
            
        def set_sheet(self, ws):
            self.ws = ws
        
        def write(self, row, col, data, style=None):
            """
            Write data to row, col of worksheet (ws) using the style
            information.
    
            Again, I'm wrapping this because you'll have to do it if you
            create large amounts of formatted entries in your spreadsheet
            (else Excel, but probably not OOo will crash).
            """
            ws = self.ws
            if not ws:
                raise Exception('you must use set_sheet() before write()')
                
            if style:
                s = self.get_style(style)
                ws.write(row, col, data, s)
            else:
                ws.write(row, col, data)
        
        def get_style(self, style):
            """
            Style is a dict maping key to values.
            Valid keys are: background, format, alignment, border
    
            The values for keys are lists of tuples containing (attribute,
            value) pairs to set on model instances...
            """
            #print "KEY", style
            style_key = tuple(style.items())
            s = self.STYLE_FACTORY.get(style_key, None)
            if s is None:
                s = xlwt.XFStyle()
                for key, values in style.items():
                    if key == "background":
                        p = xlwt.Pattern()
                        for attr, value in values:
                            p.__setattr__(attr, value)
                        s.pattern = p
                    elif key == "format":
                        s.num_format_str = values
                    elif key == "alignment":
                        a = xlwt.Alignment()
                        for attr, value in values:
                            a.__setattr__(attr, value)
                        s.alignment = a
                    elif key == "border":
                        b = xlwt.Formatting.Borders()
                        for attr, value in values:
                            b.__setattr__(attr, value)
                        s.borders = b
                    elif key == "font":
                        f = self.get_font(values)
                        s.font = f
                self.STYLE_FACTORY[style_key] = s
            return s
    
        def get_font(self, values):
            """
            'height' 10pt = 200, 8pt = 160
            """
            font_key = values
            f = self.FONT_FACTORY.get(font_key, None)
            if f is None:
                f = xlwt.Font()
                for attr, value in values:
                    f.__setattr__(attr, value)
                self.FONT_FACTORY[font_key] = f
            return f
except ImportError:
    class XlwtHelper(object):
        def __init__(*args, **kwargs):
            raise ImportError('you must have xlwt installed to use XlwtHelper')
