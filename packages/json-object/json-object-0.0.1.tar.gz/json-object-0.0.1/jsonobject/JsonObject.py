import json

class JsonObject:
    def __init__(self, entries):

        if not isinstance(entries,dict):
            raise ValueError('parameter is not a dictionary')

        for key, entry in entries.items():
            if isinstance(entry,dict):
                entries[key] = JsonObject(entry)
            elif isinstance(entry,list):
                for pos, nodel in enumerate(entry):
                    if isinstance(nodel,dict):
                        entries[key][pos] = JsonObject(nodel)

        self.__dict__.update(**entries)

    def __len__(self):
        return len(self.__dict__)

    def __getattr__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def deepcopy(self):
        return JsonObject(self.serialize())

    def pop(self, key):
        self.__dict__.pop(key, None)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def serialize(self):
        entries = {}
        for key, item in  self.__dict__.items():
            if type(item) == JsonObject:
                entries[key] = item.serialize()
            elif type(item) == list:
                new_list = []
                for pos, nodel in enumerate(item):
                    if type(nodel) == JsonObject:
                        new_list.append(nodel.serialize())
                    else:
                        new_list.append(nodel)

                entries[key] = new_list
            else:
                entries[key] = item

        return entries

    def toJson(self):
        return json.dumps(self.serialize(), indent=2, ensure_ascii=False)
