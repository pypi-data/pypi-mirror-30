import itertools

class zip_(zip):
    def __init__(self, *args):
        super().__init__()

    def __getitem__(self, slice_):
        print(vars(slice_))


o = zip_([1,2,3], [4, 5, 6])
