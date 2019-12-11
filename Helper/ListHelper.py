

class ListHelper(object):

    @staticmethod
    def convert_dict_list(properties):
        sort_list = list()
        for property in properties:
            for key, value in property.items():
                sort_list.append((key, value))
        return sort_list
