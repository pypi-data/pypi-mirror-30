from .command_rest import RESTCommand

class Describe(RESTCommand):
    def usage(self):
        return """
usage: rock describe [-ah] <name> ...

Show details about Rockset collections and views.

arguments:
    <name>              name of the collection or view

options:
    -a, --all           display extended stats
    -h, --help          show this help message and exit"""

    def go(self):
        if not self.format:
            self.format = 'yaml'
        for name in self.name:
            deets = self.get('/{}'.format(name))
            if 'data' in deets and 'sources' in deets['data']:
                nsrcs = []
                for src in deets['data']['sources']:
                    nsrcs.append({k:v for k,v in src.items() if v})
                deets['data']['sources'] = nsrcs
            desc = {}
            if 'data' in deets:
                desc = {k:v for k,v in deets['data'].items() if v}
            self.print_one(0, desc)
        return 0
