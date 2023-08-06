
# Used these instructions:
# http://peterdowns.com/posts/first-time-with-pypi.html
# http://the-hitchhikers-guide-to-packaging.readthedocs.io/en/latest/quickstart.html

from distutils.core import setup

setup( 
    name = 'SVGdatashapes',
    version = '0.3.6',
    author = 'Stephen Grubb',
    author_email = 'stevegrubb@gmail.com',
    packages = ['svgdatashapes', 'svgdatashapes_dt'],
    url = 'https://pepprseed.github.io/svgdatashapes/',
    license = 'MIT License',
    description = 'Simple procedural library to create many types of plots and data displays in SVG for dynamic web pages. General purpose: biomedical, scientific, business.',

    keywords = [ 'plot', 'graph', 'data display', 'SVG', 'bar', 'curve', 'band', 'scatterplot', 'pie graph', 
                'heatmap', 'date', 'time', 'legend', 'tooltip', 'color', 'transparent' ],

    long_description = """SVGdatashapes is a compact set of python functions  
for creating many types of plots and data displays in SVG for use in web pages.   

For full info and examples see: https://pepprseed.github.io/svgdatashapes  

General purpose, useful in areas such as biomedical, scientific, business, process monitoring, report generation. 
Plenty of control over legends, tooltips, colors, transparency, and many other appearance details.  
It has no package dependencies, and can work nicely in frameworks such as Flask and Bootstrap.  
No javascript, CSS, DOM, or SVG knowledge is required.  

Produce many types of bargraphs, lineplots, curves, bands, scatterplots, pie graphs, heatmaps, boxplots, 
histograms, multipanel displays, 
and other data displays like windbarbs and Secchi depth graphs.  Plot from your numeric, categorical, or date/time data. 

SVGdatashapes produces attractive results for many typical straightforward graphing / data display needs, as can be seen 
in the examples. The approach is procedural and the code is relatively simple and agile (click on examples to see code). 
It supports some basic "reactive" things: tooltips, clickthru, hyperlinks, element hide/show with js. It does some basic 
stat / computational things: data ranges, frequency distributions, mean and SD, quartiles for boxplots. 
For a given project, developers should judge whether SVGdatashapes is sufficient, or if more involved approaches 
(such as D3, Plotly, Numpy, R ggplot) are necessary. 

SVGdatashapes renders its results in SVG. All modern web browsers support viewing and printing of SVG graphics. 
SVG is a good format for web-based data displays and line art because it is vector-based and has full support for 
good fonts, text in any direction, transparency, as well as tooltip and hyperlink support. SVG can share CSS styling  
from the host web page and can use the full range of html special characters to get Greek letters, etc. 
(SVGdatashapes also supports <sup> and <sub> for superscripts and subscripts). 

You can include a chunk of SVG code directly into your html (referred to as an "inline SVG"). Or, you can put the SVG in  \
a separate file and reference it using an <img> tag. (We do it both ways on our web site.) """,

    classifiers = [ 'Development Status :: 4 - Beta', 
'Environment :: Web Environment', 
'Intended Audience :: Developers', 
'Intended Audience :: Education',
'Intended Audience :: Financial and Insurance Industry',
'Intended Audience :: Healthcare Industry',
'Intended Audience :: Information Technology',
'Intended Audience :: Legal Industry',
'Intended Audience :: Manufacturing',
'Intended Audience :: Other Audience',
'Intended Audience :: Science/Research',
'Intended Audience :: System Administrators',
'Intended Audience :: Telecommunications Industry',
'License :: OSI Approved :: MIT License',
'Programming Language :: Python :: 2.7',
'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
'Topic :: Multimedia :: Graphics',
'Topic :: Multimedia :: Graphics :: Presentation',
'Topic :: Scientific/Engineering :: Visualization',
'Topic :: Scientific/Engineering :: Information Analysis',
'Topic :: Scientific/Engineering :: Medical Science Apps.',
'Topic :: Software Development :: Libraries :: Python Modules',
'Topic :: Utilities' ],

  )


