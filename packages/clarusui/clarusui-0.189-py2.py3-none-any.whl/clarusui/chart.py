import plotly.graph_objs as graphs
import plotly.offline as py
import plotly.figure_factory as ff
from clarusui.layout import Element
from abc import ABCMeta, abstractmethod
from clarus.models import ApiResponse, ParsedCsvResult
import numpy as np

COLOURS = {
        'Reds' : ['#F44336','#FFCDD2','#EF9A9A','#E57373','#EF5350','#E53935','#D32F2F','#C62828','#B71C1C','#FF8A80','#FF5252','#FF1744','#D50000'],
        'LightBlues' : ['#03A9F4','#B3E5FC','#81D4FA','#4FC3F7','#29B6F6','#039BE5','#0288D1','#0277BD','#01579B','#80D8FF','#40C4FF','#00B0FF','#0091EA'],
        'Pinks':['#E91E63','#F8BBD0','#F48FB1','#F06292','#EC407A','#D81B60','#C2185B','#AD1457','#880E4F','#FF80AB','#FF4081','#F50057','#C51162'],
        'Purples' : ['#9C27B0','#E1BEE7','#CE93D8','#BA68C8','#AB47BC','#8E24AA','#7B1FA2','#6A1B9A','#4A148C','#EA80FC','#E040FB','#D500F9','#AA00FF'],
        'Blues':['#2196F3','#BBDEFB','#90CAF9','#64B5F6','#42A5F5','#1E88E5','#1976D2','#1565C0','#0D47A1','#82B1FF','#448AFF','#2979FF','#2962FF'],
        'Greens':['#4CAF50','#C8E6C9','#A5D6A7','#81C784','#66BB6A','#43A047','#388E3C','#2E7D32','#1B5E20','#B9F6CA','#69F0AE','#00E676','#00C853']
        }

class Chart(Element):

    __metaclass__ = ABCMeta
    
    def __init__(self, response, **options):
        self.layout     = dict()
        self.xoptions = dict()
        self.yoptions = dict()
        self.yoptions2 = dict()
        super(Chart, self).__init__(response, **options)
        
        if isinstance(response, ApiResponse):
            self._parsedResponse = response._parsed()
        else:
            self._parsedResponse = response            
            
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
    
    def _get_xoptions(self):
        return self.xoptions
    
    def _get_yoptions(self):
        return self.yoptions
    
    def set_layout(self, layout):
        self.layout = layout
        
    def set_xoptions(self, options):
        self.xoptions = options
    
    def set_yoptions(self, options):
        self.yoptions = options
    
    def add_xoptions(self, options):
        self._get_xoptions().update(options)
    
    def add_yoptions(self, options):
        self._get_yoptions().update(options)
        
    def set_title(self, title):
        self.layout.update({'title' : title})
        
    def set_xtitle(self, title):
        if title is not None:
            self.xoptions['title'] = title

    def set_ytitle(self, title):
        if title is not None:
            self.yoptions['title'] = title

    def set_ytitle2(self, title):
        if title is not None:
            self.yoptions2['title'] = title

    
    def set_xaxistype(self, type):
        if type is not None and type != 'auto':
            self.xoptions['type'] = type
            self.xoptions['nticks'] = 10
        
    def set_xreversed(self, reverse):
        if reverse == True:
            self.xoptions['autorange'] = 'reversed'

    def set_yreversed(self, reverse):
        if reverse == True:
            self.yoptions['autorange'] = 'reversed'
            
    def set_auto_margining(self, autoMargin):
        if autoMargin == True:
            self.add_xoptions({'automargin': True})
            self.add_yoptions({'automargin': True})
            
    def set_xaxis(self):
        #xoptions = dict()
        #xoptions['automargin'] = True
        #if reverse == True:
        #    xoptions['autorange'] = 'reversed'
        #if type is not None and type != 'auto':
        #    xoptions['type'] = type
        #    xoptions['nticks'] = 10
        #if title is not None:
        #    xoptions['title'] = title
        self.layout.update({'xaxis' : self.xoptions})   
        
    def set_yaxis(self):
        #yoptions = dict()
        #yoptions['automargin'] = True
        #if reverse == True:
        #    yoptions['autorange'] = 'reversed'
        #if axis is not None:
        #    yoptions['title'] = axis
        self.layout.update({'yaxis' : self.yoptions})   

    def set_yaxis2(self):
        #yoptions = dict()
        #yoptions['automargin'] = True
        #if reverse == True:
        #    yoptions['autorange'] = 'reversed'
        #if axis is not None:
        #    yoptions['title'] = axis
        self.yoptions2['side'] = 'right'
        self.yoptions2['overlaying'] = 'y'
        self.layout.update({'yaxis2' : self.yoptions2})   
    
    def set_legend_options(self, legendOptions):
        if legendOptions is None:
            legendOptions = dict(orientation='h')
        self.layout.update({'legend' : legendOptions})

    def set_bgcolour(self, colour):
        self.layout.update({'paper_bgcolor' : colour})
        self.layout.update({'plot_bgcolor' : colour})

    def set_colours(self, colours):
        if colours is not None:
            if isinstance(colours, list):
                self.layout.update({'colorway':colours})
            else:
                colours = COLOURS.get(colours)
                if colours is None:
                    raise ValueError('Specify a list of colours or one of: '+ str(list(COLOURS)))
                self.layout.update({'colorway':colours})

    def toDiv(self):
        return self._plot('div')

#    def toFile(self):
#        return self._plot('file')

    def _plot(self, output_type):
        figure = graphs.Figure(data=self._get_plot_data(), layout=self._get_layout())
        includeJS = True if output_type=='file' else False
        return py.offline.plot(figure_or_data=figure, show_link=False, output_type=output_type, include_plotlyjs=includeJS, config={'displayModeBar':False})
    
    def _get_xaxis(self, col):
        return self._parsedResponse.get(col, True) if self.isHorizontal() else self._parsedResponse.get_row_headers(True)

    def _get_yaxis(self, col):
        return self._parsedResponse.get_row_headers(True) if self.isHorizontal() else self._parsedResponse.get(col, True)

    def isHorizontal(self):
        return self.options.get('orientation')=='h'
    
    def _get_options(self):
        chart_options = self.options
        self.set_title(chart_options.pop('title', None))
        self.set_xtitle(chart_options.pop('xlabel', None))
        self.set_ytitle(chart_options.pop('ylabel', None))
        self.set_ytitle2(chart_options.pop('ylabel2', None))
        self.set_xaxistype(chart_options.pop('xtype', None))
        self.set_xreversed(chart_options.pop('xreverse', False))
        self.set_yreversed(chart_options.pop('yreverse', False))
        self.set_auto_margining(chart_options.pop('autoMargin', False))
        self.set_colours(chart_options.pop('colours', None))
        self.set_xaxis()
        self.set_yaxis()
        self.set_yaxis2()
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
        for colHeader in self._parsedResponse.get_col_headers(True):
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
        for colHeader in self._parsedResponse.get_col_headers(True):
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
        for colHeader in self._parsedResponse.get_col_headers(True):
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
    
    #def set_xaxis(self, title, type):
    #    xoptions = dict()
    #    if title is not None:
    #        xoptions['title'] = title
    #    self.layout.update({'xaxis' : xoptions}) 
        
    def _get_xaxis(self, col):
        x = self._parsedResponse.get(col, True)
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
        
        for colHeader in self._parsedResponse.get_col_headers(True):
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
        x = np.array(self._parsedResponse.get(col, True)).astype(np.float)
        #x = np.array(array).astype(np.float)
        return x
    
    def _get_plot_data(self):
        data = []
        groupLabels = []
     
        for colHeader in self._parsedResponse.get_col_headers(True):
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
    
        