from abc import ABCMeta, abstractmethod

class Style(object):
    def __init__(self, **options):
        self._bgColour = options.pop('backgroundColour')
        self._fgColour = options.pop('foregroundColour')
        self._fontColour = options.pop('fontColour')
        self._fontFamily = options.pop('fontFamily', 'Roboto, sans-serif')


    def getBackgroundColour(self):
        return self._bgColour

    def getForegroundColour(self):
        return self._fgColour

    def getFontColour(self):
        return self._fontColour

    def getFontFamily(self):
        return self._fontFamily


class DarkStyle(Style):
    def __init__(self):
        super(DarkStyle, self).__init__(backgroundColour='#242424', foregroundColour='#3E3E3E', fontColour='white')

class LightStyle(Style):
    def __init__(self):
        super(LightStyle, self).__init__(backgroundColour='#F3F3F5', foregroundColour='white', fontColour='#676a6c')

class DarkBlueStyle(Style):
    def __init__(self):
        super(DarkStyle, self).__init__(backgroundColour='#252830', foregroundColour='#252830', fontColour='white')

	