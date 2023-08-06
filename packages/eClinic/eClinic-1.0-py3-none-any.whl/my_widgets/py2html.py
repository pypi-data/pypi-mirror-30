import codecs

class SimpleTableCell(object):
    def __init__(self, text, header=False):
        self.text = text
        self.header = header

    def __str__(self):
        """Return the HTML code for the table cell."""
        if self.header:
            return '<th>%s</th>' %(self.text)
        else:
            return '<td>%s</td>' %(self.text.replace("\n", "<br>"))

class SimpleTableRow(object):
    def __init__(self, cells=[], header=False):
        if isinstance(cells[0], SimpleTableCell):
            self.cells = cells
        else:
            self.cells = [SimpleTableCell(cell, header=header) for cell in cells]

        self.header = header

    def __str__(self):
        """Return the HTML code for the table row and its cells as a string."""
        row = []

        row.append('<tr>')

        for cell in self.cells:
            row.append(str(cell))

        row.append('</tr>')

        return '\n'.join(row)

    def __iter__(self):
        """Iterate through row cells"""
        for cell in self.cells:
            yield cell

    def add_cell(self, cell):
        """Add a SimpleTableCell object to the list of cells."""
        self.cells.append(cell)

    def add_cells(self, cells):
        """Add a list of SimpleTableCell objects to the list of cells."""
        for cell in cells:
            self.cells.append(cell)


class SimpleTable(object):
    def __init__(self, rows=[], header_row=None, css_class=None):
        try:
            if isinstance(rows[0], SimpleTableRow):
                self.rows = rows
        except IndexError:
            self.rows =[]
        else:
            self.rows = [SimpleTableRow(row) for row in rows]

        if header_row is None:
            self.header_row = None
        elif isinstance(header_row, SimpleTableRow):
            self.header_row = header_row
        else:
            self.header_row = SimpleTableRow(header_row, header=True)

        self.css_class = css_class

    def __str__(self):
        """Return the HTML code for the table as a string."""
        table = []

        if self.css_class:
            table.append('<table class=%s>' % self.css_class)
        else:
            table.append('<table>')

        if self.header_row:
            table.append(str(self.header_row))

        for row in self.rows:
            table.append(str(row))

        table.append('</table>')

        return '\n'.join(table)

    def __iter__(self):
        """Iterate through table rows"""
        for row in self.rows:
            yield row

    def add_row(self, row):
        """Add a SimpleTableRow object to the list of rows."""
        self.rows.append(row)

    def add_rows(self, rows):
        """Add a list of SimpleTableRow objects to the list of rows."""
        for row in rows:
            self.rows.append(row)


class HTMLPage(object):
    """A class to create HTML pages containing CSS and tables."""
    def __init__(self, tables=[], css=None, title=None, encoding="utf-8"):
        self.tables = tables
        self.css = css
        self.encoding = encoding
        self.title = title

    def __str__(self):
        """Return the HTML page as a string."""
        page = []

        if self.css:
            page.append('<style type="text/css">\n%s\n</style>' % self.css)

        # Set encoding
        page.append('<meta http-equiv="Content-Type" content="text/html;'
            'charset=%s">' % self.encoding)

        for table in self.tables:
            page.append(str(table))
            page.append('<br />')

        return '\n'.join(page)

    def __iter__(self):
        """Iterate through tables"""
        for table in self.tables:
            yield table

    def save(self, filename):
        """Save HTML page to a file using the proper encoding"""
        with codecs.open(filename, 'w', self.encoding) as outfile:
            if self.title:
                outfile.write("<h1>%s</h1>"%self.title)
            for line in str(self):
                outfile.write(line)

    def add_table(self, table):
        """Add a SimpleTable to the page list of tables"""
        self.tables.append(table)

def fit_data_to_columns(data, num_cols):
    num_iterations = len(data)/num_cols

    if len(data)%num_cols != 0:
        num_iterations += 1

    return [data[num_cols*i:num_cols*i + num_cols] for i in range(num_iterations)]


css = """
    table.mytable {
        font-family: times;
        font-size:14px;
        color:#000000;
        border-width: 1px;
        border-color: #eeeeee;
        border-collapse: collapse;
        background-color: #ffffff;
        width=100%;
        table-layout:fixed;
    }
    table.mytable th {
        border-width: 1px;
        padding: 8px;
        border-style: solid;
        border-color: #000000;
        background-color: #e6eed6;
        color:blue;
    }
    table.mytable td {
        border-width: 2px;
        padding: 8px;
        border-style: solid;
        border-color: #000000;
        white-space: pre-no-wrap;
        word-wrap: break-word;
    }
    #code {
        display:inline;
        font-family: courier;
        color: #3d9400;
    }
    #string {
        display:inline;
        font-weight: bold;
    }
    """

if __name__ == "__main__":

    table1 = SimpleTable([('Hello Ugandan Cerebrities', 'world!'), ('How', 'are', 'you?')],
            header_row=['Header1', 'Header2', 'Header3'], css_class='mytable')

    table2 = SimpleTable([['Testing', 'this'], ['table', 'here']], css_class='mytable')

    page = HTMLPage(title="Mbarara Community Hospital Register")
    page.add_table(table1)
    page.add_table(table2)
    page.css = css
    page.save("test.html")
    print(page)

