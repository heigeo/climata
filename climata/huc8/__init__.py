from wq.io import NetLoader, TupleMapper, BaseIO
from climata.parsers import RdbParser


class HucIO(NetLoader, RdbParser, TupleMapper, BaseIO):
    url = "http://water.usgs.gov/GIS/new_huc_rdb.txt"

    def parse(self):
        super(HucIO, self).parse()

        # FIXME: new_huc_rdb.txt isn't a valid RDB file; remove non-digit text
        # at end of file.
        for i in range(0, 100):
            val = self.data[-i - 1].get('huc', None) or ''
            if val.isdigit():
                break
        self.data = self.data[:-i]


hucs = list(HucIO())


def get_huc8(prefix):
    """
    Return all HUC8s matching the given prefix (e.g. 1801) or basin name
    (e.g. Klamath)
    """
    if not prefix.isdigit():
        # Look up hucs by name
        name = prefix
        prefix = None
        for row in hucs:
            if row.basin.lower() == name.lower():
                # Use most general huc if two have the same name
                if prefix is None or len(row.huc) < len(prefix):
                    prefix = row.huc

    if prefix is None:
        return []

    huc8s = []
    for row in hucs:
        # Return all 8-digit hucs with given prefix
        if len(row.huc) == 8 and row.huc.startswith(prefix):
            huc8s.append(row.huc)
    return huc8s
