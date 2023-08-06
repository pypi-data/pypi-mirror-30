from .command_auth import AuthCommand

class Remove(AuthCommand):
    def usage(self):
        return """
usage: rock rm [-h] <name> <document_id>...

Remove one or more documents from a Rockset collection.

arguments:
    <name>              name of the collection or view
    <document_id>       id of the documents you wish to remove from the
                        collection or view

options:
    -h, --help          show this help message and exit
        """

    def go(self):
        resource = self.client.Collection.retrieve(self.name)
        docs = [{':id': docid} for docid in self.document_id]
        if not self.format:
            self.format = 'text'
        self.print_list(0, resource.remove_docs(docs=docs)[0],
            field_order=[':collection', ':id', 'status', 'error'])
        return 0
