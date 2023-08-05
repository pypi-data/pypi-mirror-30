import inspect

from bson.dbref import DBRef
from pymongo import MongoClient

from snakelet.utilities import Conversion


class Collection:
    def __init__(self, manager=None, document=None):
        self.manager = manager
        self.document = document
        self.collection_name = manager.collection_name.encode(self.document.__name__)
        self.collection = self.manager.db[self.collection_name]

    def find(self, search):
        return self.manager.find(self.collection_name, search)

    def find_one(self, search):
        return self.manager.find_one(self.collection_name, search)

    def save(self, document):
        if '_id' not in document:
            self.collection.insert(document)
        else:
            self.collection.update({"_id": document['_id']}, document)

    def refresh(self, document):
        if '_id' in document:
            document.update(self.collection.find_one(document['_id']))

    def remove(self, document):
        if '_id' in document:
            self.collection.remove({"_id": document['_id']})
            document.clear()

    def paginate(self, **kwargs):
        return Paginator(self, **kwargs)

    def objectify(self, document):
        return self.manager.objectify(self.collection_name, document)


class Document(dict):
    __getattr__ = dict.get
    __delattr__ = dict.__delitem__
    __setattr__ = dict.__setitem__
    """
    def __init__(self, **kwargs):
        # Parental
        super().__init__(**kwargs)
        self.__meta__ = {}

    def __add_meta__(self, key, type):
        self.__meta__[key] = type
        return
    """


class Manager(object):

    def __init__(self, database, host=None, port=None, username=None, password=None, case=None):

        # Configuration
        self.collection_name = Conversion(case)
        self.document_name = Conversion('camel')

        # Driver
        self.client = MongoClient(host=host, port=port)
        self.client[database].authenticate(name=username, password=password)
        self.db = self.client[database]

        # Storage
        self.collections = {}
        self.documents = {}
        self.ref_types = (dict, list, DBRef)

    @staticmethod
    def identify(document):
        isclass = inspect.isclass(document)
        if isclass and issubclass(document, Document):
            return document.__name__
        elif not isclass and isinstance(document, Document):
            return type(document).__name__
        else:
            raise TypeError('Value is not an instance or subclass of Document.')

    def collection(self, target):
        if not isinstance(target, str):
            target = self.identify(target)
        if target not in self.collections:
            raise LookupError('Collection ' + target + ' does not exist.')
        return self.collections[target]

    def register(self, document):
        identifier = self.identify(document)
        if identifier in self.documents:
            raise LookupError('Document ' + identifier + ' is already registered.')
        self.documents[identifier] = document
        self.collections[identifier] = Collection(self, document)
        self.__setattr__(identifier, Collection(self, document))

    def objectify(self, collection, document):
        name = self.document_name.encode(collection)
        if name in self.documents:
            prototype = self.documents[name]()
            if document:
                prototype.update(document)
            # TODO: There needs to be a 'proxy' object that holds the DBRef and hydrates
            # self.hydrate(prototype)
            return prototype
        return document

    def hydrate(self, target):
        if isinstance(target, DBRef):
            document = self.find_one(target.collection, target.id)
            if document:
                document = self.hydrate(self.objectify(target.collection, document))
            return document
        elif isinstance(target, dict):
            for key, value in target.items():
                if isinstance(value, self.ref_types):
                    target[key] = self.hydrate(value)
        elif isinstance(target, list):
            for i, value in enumerate(target):
                if isinstance(value, self.ref_types):
                    target[i] = self.hydrate(value)

        # return target if nothing else occurred
        return target

    def find(self, collection, search):
        documents = []
        for document in self.db[collection].find(search):
            documents.append(self.objectify(collection, document))
        return documents

    def find_one(self, collection, search):
        return self.objectify(collection, self.db[collection].find_one(search))

    def save(self, document):
        self.collection(document).save(document)

    def refresh(self, document):
        self.collection(document).refresh(document)

    def remove(self, document):
        self.collection(document).remove(document)

    def shutdown(self):
        pass


class Paginator:
    def __init__(self, *args, **kwargs):
        # database
        self.collection = args[0]
        self.objectify = self.collection.objectify
        self.collection = self.collection.collection

        # parameters
        self.current = 0 if 'start' not in kwargs else kwargs['start']
        self.find = None if 'find' not in kwargs else kwargs['find']
        self.offset = 0 if 'offset' not in kwargs else kwargs['offset']
        self.sort = None if 'sort' not in kwargs else kwargs['sort']
        self.size = 30 if 'size' not in kwargs else kwargs['size']

    def __iter__(self):
        return self

    def __next__(self):
        limit = self.collection.count() - self.offset
        pages = limit // self.size
        if self.current > pages:
            raise StopIteration
        else:
            # build query
            page = self.collection
            page = page.find() if not self.find else page.find(self.find)
            if self.sort:
                key, value = self.sort
                page = page.sort(key, value)
            page = page.limit(self.size)
            if self.current > 0:
                page = page.skip(self.offset + (self.current * self.size))
            elif self.offset > 0:
                page = page.skip(self.offset)

            # objectify
            documents = []
            for document in page:
                documents.append(self.objectify(document))

            # finalize
            self.current += 1
            return documents


class Proxy:
    # TODO: Build a proxy that can load hydrate itself when accessed
    # TODO: Register models for relations to exist without needing to have separate instances
    # TODO: Use register to hydrate all models of the same type simultaneously
    pass
