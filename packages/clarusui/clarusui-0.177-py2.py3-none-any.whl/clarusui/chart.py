import plotly.graph_objs as graphs
import plotly.offline as py
import plotly.figure_factory as ff
from clarusui.layout import Element
from abc import ABCMeta, abstractmethod
from clarus.models import ApiResponse, ParsedCsvResult
import numpy as np

class Chart(Element):

    __metaclass__ = ABCMeta
    
    def __init__(self, response, **options):
        self.layout     = dict()
        
        if isinstance(response, ApiResponse):
            super(Chart, self).__init__(response._parsed(), **options)
        else:
            super(Chart, self).__init__(response, **options)            
            
        #self.set_height(self.options.pop('height', None))
        #self.layout['height'] = 'auto'
        #self.options    = dict(options)
        self.colFilter  = self.options.pop('colFilter', None)
        if self.colFilter is not None:
            self.colFilter  = self.colFilter.split(',')

    @classmethod
    def from_apiresponse(cls, apiResponse, **options):
        apiResponse.stats['IsGrid'] = 'Yes' #force this as otherwise non grids causes problems in charts
        return cls(apiResponse, **options)

    @classmethod
    def from_csv(cls, csvText, delimiter=',', **options):
        parsed = ParsedCsvResult(csvText, delimiter)
        if not parsed.get_col_headers(True):
            parsed = ParsedCsvResult(csvText, delimiter, hasrowheaders=False)
        return cls(parsed, **options)
       
    @classmethod
    def from_dataframe(cls, dataFrame, **options):
        csvText = dataFrame.to_csv(index=False)
        return cls.from_csv(csvText, **options)
    
    def set_height(self, height):
        if height is None:
            self.layout['height'] = 'auto'
        else:
            self.layout.update({'height' : height, 'autosize' : True})  
        
    def set_font(self, style):
        font = dict()
        axis = dict()
        if style is not None:
            font['color'] = style.getFontColour()
            font['family'] = style.getFontFamily()
            self.layout['font'] = font
            
            #axis['linecolor'] = style.getFontColour()
            #axis['zerolinecolor'] = style.getFontColour()
            #self.layout['xaxis'] = axis
            #self.layout['yaxis'] = axis
    
    def _get_layout(self):
        return self.layout
    
    def set_layout(self, layout):
        self.layout = layout
        
    def set_title(self, title):
        self.layout.update({'title' : title})
        
    def set_xaxis(self, title, type):
        xoptions = dict()
        #xoptions['automargin'] = True
        #if reverse == True:
        #    xoptions['autorange'] = 'reversed'
        if type is not None and type != 'auto':
            xoptions['type'] = type
            xoptions['nticks'] = 10
        if title is not None:
            xoptions['title'] = title
        self.layout.update({'xaxis' : xoptions})   
        
    def set_yaxis(self, axis):
        yoptions = dict()
        #yoptions['automargin'] = True
        #if reverse == True:
        #    yoptions['autorange'] = 'reversed'
        if axis is not None:
            yoptions['title'] = axis
        self.layout.update({'yaxis' : yoptions})   
    
    def set_legend_options(self, legendOptions):
        if legendOptions is None:
            legendOptions = dict(orientation='h')
        self.layout.update({'legend' : legendOptions})

    def set_bgcolour(self, colour):
        self.layout.update({'paper_bgcolor' : colour})
        self.layout.update({'plot_bgcolor' : colour})

    def toDiv(self):
        return self._plot('div')

#    def toFile(self):
#        return self._plot('file')

    def _plot(self, output_type):
        figure = graphs.Figure(data=self._get_plot_data(), layout=self._get_layout())
        includeJS = True if output_type=='file' else False
        return py.offline.plot(figure_or_data=figure, show_link=False, output_type=output_type, include_plotlyjs=includeJS, config={'displayModeBar':False})
    
    def _get_xaxis(self, col):
        return self.response.get(col, True) if self.isHorizontal() else self.response.get_row_headers(True)

    def _get_yaxis(self, col):
        return self.response.get_row_headers(True) if self.isHorizontal() else self.response.get(col, True)

    def isHorizontal(self):
        return self.options.get('orientation')=='h'
    
    def _get_options(self):
        chart_options = dict(self.options)
        self.set_title(chart_options.pop('title', None))
        self.set_xaxis(chart_options.pop('xlabel', None), chart_options.pop('xtype', None))
        self.set_yaxis(chart_options.pop('ylabel', None))
        self.set_legend_options(chart_options.pop('legend', None))
        bgcolour = chart_options.pop('bgcolour', None)
        if (bgcolour is not None):
            self.set_bgcolour(bgcolour)
        #self.add_custom_css({"background-color":bgcolour})
        return chart_options
               
    @abstractmethod        
    def _get_plot_data(self):
        pass

class PieChart(Chart):

    def __init__(self, response, **options):
        super(PieChart, self).__init__(response, **options)
        
    def _get_plot_data(self):
        data = []
        for colHeader in self.response.get_col_headers(True):
            if (self.colFilter==None or colHeader in self.colFilter):
                data.append(graphs.Pie(labels=self._get_xaxis(colHeader), values=self._get_yaxis(colHeader), name=colHeader, **self._get_options()))                    
        return data
        
class DonutChart(PieChart):
        
    def __init__(self, response, **options):
        super(DonutChart, self).__init__(response, **options)
        
    def _get_options(self):
        options = super(PieChart, self)._get_options()     
        options['hole'] = options.pop('hole', .5)
        return options
            
    def _get_layout(self):
        layout =  super(DonutChart, self)._get_layout()        
        layout['annotations'] = [dict(text=layout.pop('title', None), showarrow=False, font={'size':15})]
        return layout
   
class BarChart(Chart):

    def __init__(self, response, **options):
        super(BarChart, self).__init__(response, **options)
        
    def _get_options(self):
        bar_options =  super(BarChart, self)._get_options()
        colour = self._get_rgbcolour(bar_options.pop('colour', None))
        lineColour = self._get_rgbcolour(bar_options.pop('lineColour', colour))
        lineWidth = bar_options.pop('lineWidth', '1')
        if (colour is not None):
            bar_options['marker'] = dict(color=colour, line=dict(color=lineColour, width=lineWidth))
        return bar_options
        
    def _get_plot_data(self):
        data = []
        for colHeader in self.response.get_col_headers(True):
            if (self.colFilter==None or colHeader in self.colFilter):
                data.append(graphs.Bar(x=self._get_xaxis(colHeader), y=self._get_yaxis(colHeader), name=colHeader, **self._get_options()))                 
        return data
        
class StackedBarChart(BarChart):

    def __init__(self, response, **options):
        super(StackedBarChart, self).__init__(response, **options)
        
    def _get_layout(self):
        bar_layout =  super(StackedBarChart, self)._get_layout()
        bar_layout['barmode'] = 'stack'
        return bar_layout
    
class LineChart(Chart):

    def __init__(self, response, **options):
        super(LineChart, self).__init__(response, **options)

    def _get_options(self):
        line_options = super(LineChart, self)._get_options()
        lineColour = self._get_rgbcolour(line_options.pop('lineColour', None))
        lineWidth = line_options.pop('lineWidth', '1')
        interpolate = line_options.pop('interpolate', 'linear')
        line = line_options.pop('line', 'solid')
        if (line!='solid') or (lineColour is not None) or (lineWidth!='1') or (interpolate!='linear'):
            line_options['line'] = dict(color=lineColour, width=lineWidth, dash=line, shape=interpolate);
        return line_options        

    def _get_plot_data(self):
        data = []
        for colHeader in self.response.get_col_headers(True):
            if (self.colFilter==None or colHeader in self.colFilter):
                data.append(graphs.Scatter(x=self._get_xaxis(colHeader), y=self._get_yaxis(colHeader), name=colHeader, **self._get_options()))                 
        return data
    
class AreaChart(LineChart):

    def __init__(self, response, **options):
        super(AreaChart, self).__init__(response, **options)
    
    def _get_options(self):
        line_options =  super(AreaChart, self)._get_options()
        line_options['fill'] = 'tonexty'
        colour = self._get_rgbcolour(line_options.pop('colour', None))
        if colour is not None:
            line_options['fillcolor'] = colour
        return line_options

class Histogram(Chart):
    
    def __init__(self, response, **options):
        super(Histogram, self).__init__(response, **options)
        
    def _get_options(self):
        hist_options =  super(Histogram, self)._get_options()
        binSize = hist_options.pop('binSize', None)
        binNumber = hist_options.pop('binNumber', None)
        
        if binSize is not None and binNumber is not None:
            raise ValueError("Cannot specify both binSize and binNumber for Histogram")
        
        if binNumber is not None:
            binSize = self._get_calculated_bin_size(binNumber)
        
        if binSize is not None:
            hist_options['xbins'] = dict(size=binSize, start=self._rangeStart, end=self._rangeEnd)
        return hist_options
    
    def set_xaxis(self, title, type):
        xoptions = dict()
        if title is not None:
            xoptions['title'] = title
        self.layout.update({'xaxis' : xoptions}) 
        
    def _get_xaxis(self, col):
        x = self.response.get(col, True)
        self._calculate_range(x)
        return x
    
    def _get_calculated_bin_size(self, binNumber):
        range = self._rangeEnd - self._rangeStart
        return range/binNumber
    
    def _calculate_range(self, array):
        try:
            x = np.array(array).astype(np.float)
            self._rangeStart = min(x)
            self._rangeEnd = max(x)
        except ValueError:
            self._rangeStart = None
            self._rangeEnd = None
           
    def _get_plot_data(self):
        data = []
        
        for colHeader in self.response.get_col_headers(True):
            if (self.colFilter==None or colHeader in self.colFilter):
                data.append(graphs.Histogram(x=self._get_xaxis(colHeader), name=colHeader, **self._get_options()))                 
        return data
    
class DistChart(Chart):
    def __init__(self, response, **options):
        self._binSize = options.pop('binSize', 1.)
        super(DistChart, self).__init__(response, **options)
        
    def _get_options(self):
        hist_options =  super(DistChart, self)._get_options()
        return hist_options

    def _get_xaxis(self, col):
        x = np.array(self.response.get(col, True)).astype(np.float)
        #x = np.array(array).astype(np.float)
        return x
    
    def _get_plot_data(self):
        data = []
        groupLabels = []
     
        for colHeader in self.response.get_col_headers(True):
            print(colHeader)
            if (self.colFilter==None or colHeader in self.colFilter):
                data.append(self._get_xaxis(colHeader))
                groupLabels.append(colHeader)
                
        return ff.create_distplot(data, groupLabels, bin_size=self._binSize)                 

    
    def _plot(self, output_type):
        data=self._get_plot_data()
        data['layout'].update(self._get_layout())
        includeJS = True if output_type=='file' else False
        return py.offline.plot(data, show_link=False, output_type=output_type, include_plotlyjs=includeJS, config={'displayModeBar':False})
    
    
class ComboChart(Chart):
    def __init__(self, *charts, **options):
        super(ComboChart, self).__init__(None, **options)
        self._charts = charts
        
    def _get_plot_data(self):
        self._get_options()
        data = []
        for chart in self._charts:
            for d in chart._get_plot_data():
                data.append(d)
        return data
    
        