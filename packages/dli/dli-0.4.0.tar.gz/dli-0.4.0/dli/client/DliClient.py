from .Ctx import Ctx
from .DatasetFunctions import DatasetFunctions
from .PackageFunctions import PackageFunctions
from .PandasClient.PandasFunctions import PandasFunctions


class DliClient(PackageFunctions, DatasetFunctions, PandasFunctions):
    def __init__(self, api_key, api_root):
        self.ctx = Ctx(api_key, api_root)

    def get_root_siren(self):
        return self.ctx.get_root_siren()
