
class EnsemblObject:

# https://rest.ensembl.org/documentation/info/lookup
# reads the start and end of the transcript

    def __init__(self, _id, species, _end, _start):
        self._id = _id
        self.species = species
        self._end = _end
        self._start = _start
