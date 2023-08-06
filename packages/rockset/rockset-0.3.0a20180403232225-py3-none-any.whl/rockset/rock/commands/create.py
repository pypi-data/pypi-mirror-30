import csv
import sys

from .command_auth import AuthCommand
from docopt import docopt
from rockset import Q, F

class Create(AuthCommand):
    def usage(self, subcommand=None):
        usage = """
usage:
  rock create --help
  rock create [-h] --file=YAMLFILE
  rock create collection --help
  rock create collection [-h] [--desc=TEXT] <name> [<collection_source_args> ...]
  rock create view --help
  rock create view [-h] [--desc=TEXT] <name> [<view_source_args> ...]

Create a new collection or view.

commands:
  collection          create a new collection.
                      you can optionally specify data sources to automatically
                      feed into the collection such as AWS S3

  view                create a new view from all source collections listed

arguments:
  <name>              name of the new collection or view you wish to create

options:
  -d TEXT, --desc=TEXT  human readable description of the new resource
  -f FILE, --file=FILE  create all resources in the a YAML file
  -h, --help            show this help message and exit
        """

        usage_collection = """
usage:
  rock create collection --help
  rock create collection [-h] <name> [<collection_source_args> ...]
  rock create collection [-h] <name>
        (s3 <s3_bucket_name>)
        [(prefix <s3_bucket_prefix>) ...]
        [(format <data_format>)]
        [(mask <field_mask>) ...]
        [(delimiter <field_path_delimiter>)]
        [(access_key <aws_access_key_id>)]
        [(secret_access <aws_secret_access_key>)]
        [<next_collection_source_args> ...]

Create a new collection using AWS S3 as a data source.

Optionally, fields can be masked or anonymized as they are replicated into
the collection.

arguments:
  <aws_access_key_id>      AWS access key id
  <aws_secret_access_key>  AWS secret access key
  <data_format>            Data format of objects in S3. One of "json",
                           "parquet", or "xml". [default: "json"]
  <field_mask>             field masks can anonymize or ignore fields
                           as they are replicated into the collection.
                           Each <field_mask> is a ":" colon-separated tuple of
                           an input field that needs to be masked and name of
                           the masking function such as 'SHA256' or 'NULL'.
  <field_path_delimiter>   specify field path delimiter while specifying
                           nested fields in <field_mask> [default: "."]
  <s3_bucket_name>         name of the AWS S3 bucket
  <s3_bucket_prefix>       only add objects with prefix from AWS S3 bucket

options:
  -h, --help               show this help message and exit

examples:
    Create a collection and source all contents from an AWS S3 bucket:

        $ rock create collection bkt1rocks \\
              s3 bkt1.mycompany.com

    Create a collection from an AWS S3 bucket but only pull certain paths:

        $ rock create collection bkt1rocks \\
              s3 bkt1.mycompany.com \\
              prefix '/root/path/in/bkt1' \\
              prefix '/root/path2'

    Create a collection from AWS S3 after incorporating the following two masks:
         i) anonymize input nested field from.email
        ii) overwrite input field email_body to NULL

        $ rock create collection bkt1-coll \\
              s3 bkt1.mycompany.com \\
              mask from.email:SHA256 \\
              mask email_body:NULL
        """
        usage_view = """
usage:
  rock create view --help
  rock create view [-h] <name> <view_source_args> ...
  rock create view [-h] <name>
        (collection <collection_name>)
        [(query <query>)]
        [(mapping <field_mapping>) ...]
        [<next_view_source_args> ...]

Create a new view from one or more collections.

Optionally, a filter query can be specified to sub-select documents and fields
from each source collection. By default, the entire collection will be synced
to the view.

Field mappings can be specified for each source collection to analyze a field
in a collection as the data is continuously synced with the view.

arguments:
  <collection_name>        name of the collection source
  <field_mapping>          field mapping can analyze a field from collection
                           and map it to a new output field in the view.
                           Analyzers are used for enriching or indexing
                           collection fields as they are synced to the view.
                           Each <field_mapping> is a ":" colon-separated
                           tuple with 3 entries: (<projection>, <output-field>)
                           Eg: "email_body:Whitespace:email_body_tokens"
  <query>                  filter query on the source collection as an
                           s-expression

options:
  -h, --help          show this help message and exit

examples:
    Create a view and source all documents from collection bkt1rocks
    with field "age" > 18

        $ query=$(python3 -c "from rockset import F; print(F["age"] > 18)")
        $ rock create view bkt1analysis \\
              collection bkt1rocks \\
              query "$query"

    Create a view that indexes text in email_body and email_subject fields
    from collection office365_emails:

        $ query=$(python3 -c "from rockset import F; print(Q.all.select(F["email_body"], F["email_subject"]))")
        $ rock create view email_search \\
              collection office365_emails \\
              query "$query" \\
              mapping email_body:Whitespace:email_body_tokens \\
              mapping email_subject:Whitespace:email_subject_tokens
        """
        if subcommand == 'collection':
            return usage_collection
        elif subcommand == 'view':
            return usage_view
        return usage

    def _parse_arg_pairs(self, args, heads, singles, multi, leftover):
        """ splits `args` after validation into a map.
        returns dict or None if error.
        every entry in `singles` + `multi` will be a key.
        default value for all `singles` will be None and `multi` will be [].
        expects `args` to start with one of the `heads`, and returns
        the remainder in key `leftover`.
        """
        if len(args) < 2 or len(args) % 2 != 0:
            return None
        for head in heads:
            if head not in singles or head in multi:
                return None
        if args[0] not in heads:
            return None
        pargs = {}
        for s in singles:
            pargs[s] = None
        for m in multi:
            pargs[m] = []
        i = 0
        while i < len(args):
            # pop keys and ensure we didn't hit the next head
            key = args[i]
            if i > 0 and key in heads:
                break
            # pop value and bump i
            value = args[i + 1]
            i += 2
            if key in singles:
                if pargs[key] is not None:
                    return None
                pargs[key] = value
            elif key in multi:
                pargs[key].append(value)
            else:
                return None
        pargs[leftover] = args[i:]
        return pargs

    def _source_s3(self, args):
        mappings = []
        if len(args['mask']) > 0:
            delimiter = '.'
            if args['delimiter']:
                delimiter = args['delimiter']
            for fm in args['mask']:
                mask = list(csv.reader([fm], delimiter=':')).pop()
                if len(mask) != 2:
                    raise ValueError('cannot understand '
                        'field_mask {}'.format(fm))
                input_path = list(csv.reader([mask[0]],
                    delimiter=delimiter)).pop()
                input_path_fr = F
                for i in input_path:
                    input_path_fr = input_path_fr[i]
                mappings.append(tuple([input_path_fr, mask[1]]))
        return self.client.Source.s3(bucket=args['s3'],
            data_format=args.get('format', None),
            prefixes=args.get('prefix', None),
            mappings=mappings,
            access_key=args.get('access_key', None),
            secret_access=args.get('secret_access', None))

    def _source_collection(self, args):
        mappings = []
        if len(args['mapping']) > 0:
            delimiter = '.'
            if args['delimiter']:
                delimiter = args['delimiter']
            for fm in args['mapping']:
                mapping = list(csv.reader([fm], delimiter=':')).pop()
                if len(mapping) != 2:
                    raise ValueError('cannot understand '
                        'field_mapping {}'.format(fm))
                projection = mapping[0]
                output_field_fr = F[mapping[1]]
                mappings.append(tuple([projection, output_field_fr]))
        return self.client.Source.collection(name=args['collection'],
            query=args.get('query', None),
            mappings=mappings)

    def parse_args(self, args):
        parsed_args = dict(docopt(self.usage(), argv=args, help=False))

        # handle help
        if parsed_args['--help']:
            if parsed_args['collection']:
                ret = self.usage(subcommand='collection')
            elif parsed_args['view']:
                ret = self.usage(subcommand='view')
            else:
                ret = self.usage()
            raise SystemExit(ret.strip())

        # see if YAMLFILE was specified
        fn = parsed_args['--file']
        if fn:
            self.set_batch_items('resource', self._parse_yaml_file(fn))
            return {}

        # construct a valid CreateRequest object
        resource = {}
        resource['name'] = parsed_args['<name>']
        if parsed_args['--desc']:
            resource['description'] = parsed_args['--desc']
        sources = []
        if parsed_args['collection']:
            resource['type'] = 'COLLECTION'
            if len(parsed_args['<collection_source_args>']) > 0:
                argv = parsed_args['<collection_source_args>']
                while len(argv) > 0:
                    parsed_args = self._parse_arg_pairs(argv,
                        heads=['s3'],
                        singles=['s3','delimiter','format',
                            'access_key','secret_access'],
                        multi=['prefix','mask'],
                        leftover='_next')
                    if parsed_args is None:
                        ret = self.usage(subcommand='collection')
                        raise SystemExit(ret.strip())
                    if parsed_args['s3']:
                        sources.append(self._source_s3(parsed_args))
                    argv = parsed_args['_next']
        elif parsed_args['view']:
            resource['type'] = 'VIEW'
            argv = parsed_args['<view_source_args>']
            while len(argv) > 0:
                parsed_args = self._parse_arg_pairs(argv,
                    heads=['collection'],
                    singles=['collection','query','delimiter'],
                    multi=['mapping'],
                    leftover='_next')
                if parsed_args is None:
                    ret = self.usage(subcommand='view')
                    raise SystemExit(ret.strip())
                if parsed_args['collection']:
                    sources.append(self._source_collection(parsed_args))
                argv = parsed_args['_next']
        resource['sources'] = sources
        return {'resource': resource}

    def go(self):
        self.logger.info('create {}'.format(self.resource))
        rtype = self.resource.pop('type', None)
        if rtype is None:
            return 1
        if rtype == 'COLLECTION':
            return self.go_collection(self.resource)
        if rtype == 'VIEW':
            return self.go_view(self.resource)
        return 1

    def go_collection(self, resource):
        name = resource.pop('name')
        c = self.client.Collection.create(name, **resource)
        self.lprint(0, 'Collection "%s" was created successfully.'
            % (c.name))
        return 0

    def go_view(self, resource):
        name = resource.pop('name')
        v = self.client.View.create(name, **resource)
        self.lprint(0, 'View "%s" was created successfully.'
            % (v.name))
        return 0
