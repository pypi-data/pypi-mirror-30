from .svgdatashapes import svgbegin, svgresult, xspace, yspace, settext, setline, findrange, uniqcats, columninfo
from .svgdatashapes import plotdeco, xaxis, yaxis, bar, errorbar, datapoint, setclustering, label, rectangle, curvebegin, curvenext, line, arrow
from .svgdatashapes import pieslice, legenditem, legendrender, tooltip, groupbegin, groupend
from .svgdatashapes import lin, txt, rect, circle, polygon, comment, nx, ny, nu, ndist, inspace, nmin, nmax, dmin, dmax, vec2d
from .svgdatashapes import p_dtformat, _getdfindex

# this allows us to support "from svgdatashapes import *" ....
__all__ = [
    "svgbegin", "svgresult", "xspace", "yspace", "settext", "setline", "findrange", "uniqcats", "columninfo", 
     "plotdeco", "xaxis", "yaxis", "bar", "errorbar", "datapoint", "setclustering", "label", "rectangle", "curvebegin", "curvenext", "line", "arrow",
    "pieslice", "legenditem", "legendrender", "tooltip", "groupbegin", "groupend", 
    "lin", "txt", "rect", "circle", "polygon", "comment", "nx", "ny", "nu", "ndist", "inspace", "nmin", "nmax", "dmin", "dmax", "vec2d" ]
