class Encase(dict):
    """This Class is used to create dictionary style objects that
    can have key data accessed by dot (.) notation, for example,

        data = Encase()
        data.key = "Sample data"
        print(data.key)

    ..would print "Sample Data". Instances of this class can be
    nested. Existing dictionaries, including nested dictionaries,
    can be converted into Encase instances by passing the
    parent dict in as a single parameter. The init function will
    recursively convert any child dictionary into a Encase.
    (This also includes any sub-dicts contained within a list.)
    """

    def __init__(self, existing_object=None):
        if isinstance(existing_object, dict):
            for key, value in existing_object.items():
                if isinstance(value, dict):
                    self.set(key, Encase(value))
                elif isinstance(value, list):
                    self.set(key, self._convert_list(value))
                else:
                    self.set(key, value)

    def __getattr__(self, key):
        """Get value of attribute at 'key'. Do not call directly.
        Use syntax data.key instead (data is instance of this class).
        """
        if key in self:
            return self[key]
        else:
            raise AttributeError("No value set for: " + key)

    def __setattr__(self, key, value):
        """Set value of attribute at 'key'. Do not call directly.
        Use syntax data.key = value instead (data is instance of
        this class).
        """
        self[key] = value

    def get(self, key):
        """Get value of attribute at 'key'. Use this method when
        you won't know key name prior to using variable. Useful when
        pulling data programatically.
        """
        return self.__getattr__(key)

    def set(self, key, value):
        """Set value of attribute at 'key'. Use this method when
        you won't know key name prior to setting. Useful when not
        knowing how many instances or sub-sets of data will be
        returned from an API.
        """
        self.__setattr__(key, value)

    def _convert_list(self, existing_list):
        L = []
        for item in existing_list:
            if isinstance(item, dict):
                L.append(Encase(item))
            elif isinstance(item, list):
                L.append(self._convert_list(item))
            else:
                L.append(item)
        return L
