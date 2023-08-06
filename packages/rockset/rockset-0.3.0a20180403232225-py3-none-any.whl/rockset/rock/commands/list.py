from .command_rest import RESTCommand

class List(RESTCommand):
    @classmethod
    def what(cls):
        return('ls', 'List all collections and views')

    def usage(self):
        return """
usage: rock ls [-h]

List all collections and views.

options:
  -h, --help            show this help message and exit
        """

    def go(self):
        if not self.format:
            self.format = 'text'
        items = self.get('/', params={'type': 'all'})['data']
        sorted_items= sorted(items, key=lambda k: k['type'] + ':' + k['name'])
        return (0, sorted_items)

    def print_result(self, result):
        self.print_list(0, result, ['type', 'name', 'status', 'description'])
