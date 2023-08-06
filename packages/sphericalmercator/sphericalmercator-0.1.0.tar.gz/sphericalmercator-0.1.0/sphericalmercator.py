import math


class WrongZoomException(Exception):
    pass


class SphericalMercator(object):
    """
    Python class defining Spherical Mercator Projection.

    Originally from:
      http://svn.openstreetmap.org/applications/rendering/mapnik/generate_tiles.py
    """

    def __init__(self, levels=18, size=256):
        self.Bc = []
        self.Cc = []
        self.zc = []
        self.Ac = []
        self.levels = levels
        self.DEG_TO_RAD = math.pi / 180
        self.RAD_TO_DEG = 180 / math.pi
        self.size = size
        for d in range(0, levels):
            e = size / 2.0
            self.Bc.append(size / 360.0)
            self.Cc.append(size / (2.0 * math.pi))
            self.zc.append((e, e))
            self.Ac.append(size)
            size *= 2.0

    @staticmethod
    def minmax(a, b, c):
        a = max(a, b)
        a = min(a, c)
        return a

    def check_zoom(self, zoom):
        if zoom < 0 or zoom >= self.levels:
            raise WrongZoomException('zoom must be between %s and %s' % (0, self.levels - 1))

    def ll_to_px(self, ll, zoom):
        self.check_zoom(zoom)
        d = self.zc[zoom]
        e = round(d[0] + ll[0] * self.Bc[zoom])
        f = self.minmax(math.sin(self.DEG_TO_RAD * ll[1]), -0.9999, 0.9999)
        g = round(d[1] + 0.5 * math.log((1 + f) / (1 - f)) * -self.Cc[zoom])
        return e, g

    def px_to_ll(self, px, zoom):
        """ Convert pixel postion to LatLong (EPSG:4326) """
        # TODO - more graceful handling of indexing error
        self.check_zoom(zoom)
        e = self.zc[zoom]
        f = (px[0] - e[0]) / self.Bc[zoom]
        g = (px[1] - e[1]) / -self.Cc[zoom]
        h = self.RAD_TO_DEG * (2 * math.atan(math.exp(g)) - 0.5 * math.pi)
        return f, h

    def xyz_to_envelope(self, x, y, zoom, tms_style=False):
        """ Convert XYZ to mapnik.Envelope """
        # flip y to match TMS spec
        if tms_style:
            y = (2 ** zoom - 1) - y
        ll = (x * self.size, (y + 1) * self.size)
        ur = ((x + 1) * self.size, y * self.size)
        minx, miny = self.px_to_ll(ll, zoom)
        maxx, maxy = self.px_to_ll(ur, zoom)
        return minx, miny, maxx, maxy

    def bbox_to_tiles(self, minx, miny, maxx, maxy, zoom):
        """Get the tiles for bbox"""
        self.check_zoom(zoom)

        minx = max(-180.0, minx)
        miny = max(-85.051129, miny)
        maxx = min(180.0, maxx)
        maxy = min(85.051129, maxy)

        if minx > maxx:
            bboxes = [
                (-180.0, miny, maxx, maxy),
                (minx, miny, 180.0, maxy)
            ]
        else:
            bboxes = [(minx, miny, maxx, maxy)]

        for minx, miny, maxx, maxy in bboxes:

            ll = self.ll_to_px((minx, miny), zoom)
            ur = self.ll_to_px((maxx, maxy), zoom)

            tile_x_min = int(max(ll[0] / self.size, 0))
            tile_x_max = int(min(ur[0] / self.size + 1, 2 ** zoom))
            tile_y_min = int(max(ur[1] / self.size, 0))
            tile_y_max = int(min(ll[1] / self.size + 1, 2 ** zoom))

            for x in range(tile_x_min, tile_x_max):
                for y in range(tile_y_min, tile_y_max):
                    yield x, y
