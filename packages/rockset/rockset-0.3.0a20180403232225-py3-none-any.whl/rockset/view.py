"""
Introduction
------------
View objects represent a single Rockset view. These objects are
generally created from a Client_ object and can be used to create,
manage and query views.

::

    from rockset import Client

    # connect to Rockset
    rs = Client(api_key=...)
    hotness = rs.View.retrieve('hotness')

You can query all documents currently present in the view. Refer
to the Query_ module for a list of supported query operators.

You can also drop the view altogether.

Example usage
-------------
::

    from rockset import Client, Q, F

    # connect securely to Rockset
    rs = Client(api_key=...)

    # retrieve the relevant view
    users = rs.View.retrieve('users')

    # construct the query you want to run on the view
    # the following query looks for all people named Smith
    # whose bio mentions mcdonalds
    mcd_smiths_q = Q((F["last_name"] == 'Smith') & (F["bio"][:] == 'mcdonalds'))

    # query the view
    docs = users.query(mcd_smiths_q).results()

.. todo::

    * API support for adding collections as view sources.
    * API support for updating various view properties

.. _View.create:

Create a new view
-----------------
Creating a view using the Client_ object is done by using the
``client.View.create()`` method::

    # use the Whitespace tokenizer to parse the 'overview'
    # field and tokenize it
    from rockset import Client, Q, F
    rs = Client()

    query = Q(F["email"].is_not_null())
    src = rs.Source.collection(name=colname, query=query,
        mappings=[(F['email_body'], 'Whitespace', F['email_body_tokens'])])

    email_search = rs.View.create('email_body_search', sources=[src])

.. automethod:: rockset.View.create

.. _View.list:

List all views
--------------
List all views using the Client_ object using::

    from rockset import Client
    rs = Client()
    views = rs.View.list()

.. automethod:: rockset.View.list

.. _View.retrieve:

Retrieve an existing view
-------------------------
Retrieve a view to run queries on that view::

    from rockset import Client
    rs = Client()
    users = rs.View.retrieve('users')

.. automethod:: rockset.View.retrieve

.. _View.describe:

Describe an existing view
-------------------------
Fetch all details about a view such as collection sources, field mappings,
and various perf & usage statistics::

    from rockset import Client
    rs = Client()
    print(rs.View.retrieve('email-search').describe())

.. automethod:: rockset.View.describe

.. _View.drop:

Drop a view
-----------
Use the ``drop()`` method to delete a view::

    from rockset import Client
    rs = Client()
    rs.View.retrieve('email-search').drop()

.. automethod:: rockset.View.drop

.. _View.query:

Query a view
------------
Binds the input query to the view and returns a Cursor_ object. The query
will not be issued to the backend until the results are fetched from the
cursor::

    from rockset import Client, Q, F

    rs = Client()
    email_search = rs.View.retrieve('email-search')

    q = Q.all.search(
            F["subject_tokens"].proximity("game of thrones").boost(1.5),
            F["email_body_tokens"].proxmity("game of thrones").boost(1.0))
    results = email_search.query(q).results()


.. automethod:: rockset.View.query

"""
import rockset
from .exception import InputError
from .resource import Resource
from .collection import Collection

class View(Resource):
    @classmethod
    def create(cls, name, description=None, sources=None, **kwargs):
        """Creates a new Rockset view.

        Use it via rockset.Client().View.create()

        Only alphanumeric characters, ``_``, ``-`` and ``.`` are allowed
        in view names.

        Args:
            name (str): name of the view to be created.
            description (str): a human readable description of the view
            sources (Source): array of Source objects that defines the set
                of data sources for this view

        Returns:
            View: View object
        """
        if 'client' not in kwargs or 'model' not in kwargs:
            raise ValueError('incorrect API usage. '
                'use rockset.Client().View.create() instead.')
        client = kwargs.pop('client')
        model = kwargs.pop('model')
        func = model.create
        request = kwargs.copy()
        request['name'] = name
        request['type'] = 'VIEW'
        request['description'] = description
        request['sources'] = sources
        view = client.apicall(method=func, request=request)['data']
        return cls(client=client, model=model, **view)

    @classmethod
    def retrieve(cls, name, **kwargs):
        """Retrieves details of a single view

        Use it via rockset.Client().View.retrieve()

        Args:
            name (str): Name of the view

        Returns:
            View: View object
        """
        if 'client' not in kwargs or 'model' not in kwargs:
            raise ValueError('incorrect API usage. '
                'use rockset.Client().View.create() instead.')
        v = cls(name=name, **kwargs)
        v.describe()
        return v

    @classmethod
    def list(cls, **kwargs):
        """Returns list of all views.

        Use it via rockset.Client().View.list()

        Returns:
                List: A list of View objects
        """
        if 'client' not in kwargs or 'model' not in kwargs:
            raise ValueError('incorrect API usage. '
                'use rockset.Client().View.create() instead.')
        client = kwargs.pop('client')
        model = kwargs.pop('model')
        func = model.list
        views = client.apicall(method=func, type='view')['data']
        return [cls(client=client, model=model, **v) for v in views]

    def __init__(self, *args, **kwargs):
        kwargs['type'] = 'COLLECTION'
        super(View, self).__init__(*args, **kwargs)

    # instance methods
    def describe(self):
        """Returns all properties of the view as a dict.

        Returns:
            dict: properties of the view
        """
        return super(View, self).describe(func=self.model.describe)
    def drop(self):
        """Deletes the view represented by this object.

        If successful, the current object will contain
        a ``dropped`` property with value ``True``

        Example::

            ...
            print(my_view.describe()
            my_view.drop()
            print(my_view.dropped)      # will print True
            ...

        """
        super(View, self).drop(func=self.model.drop)
        return
    def query(self, q, timeout=None, flood_all_leaves=False):
        # docstring is inherited from Collection.query
        # search for View.query.__doc__ below
        return super(View, self).query(q, timeout=timeout,
                                       flood_all_leaves=flood_all_leaves)

    def fence(self, commit_mark):
        return super(View, self).fence(
            self.model.fence, commit_mark)

View.query.__doc__ = Collection.query.__doc__.replace('collection', 'view')

__all__ = [
    'View',
]
