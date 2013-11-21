from wq.io import CsvNetIO


class HucIO(CsvNetIO):
    # FIXME: some HUCs have changed, but new_huc_rdb.txt isn't a valid TSV file
    url = "http://water.usgs.gov/GIS/huc_rdb.txt"
    delimiter = "\t"

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
