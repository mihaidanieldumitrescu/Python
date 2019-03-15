# BRANCH IS REDESIGN

from main.EntryNew import EntryNew


class GenerateSQLfile:

    def __init__(self):
        self.entries = []

    def __str__(self):
        return "\n".join([str(x) for x in self.entries])

    def add_entry(self, entry):
        if isinstance(entry, EntryNew):
            self.entries.append(entry)
        else:
            raise TypeError('Only EntryNew objects are supported for this method')


