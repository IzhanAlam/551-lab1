from flask_table import Table, Col

class Data(Table):
    isbn = Col('ISBN')
    title = Col('Title')
    author = Col('Author')
    published = Col('Date Published')

class commentdis(Table):
    id = Col('Comment Number')
    name = Col('Author')
    body = Col('Text')
    timestamp = Col('Time Posted')
