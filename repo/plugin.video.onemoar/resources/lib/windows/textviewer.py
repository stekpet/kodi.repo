# -*- coding: utf-8 -*-

from resources.lib.windows.base import BaseDialog


class TextViewerXML(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, args)
		self.window_id = 2060
		self.heading = kwargs.get('heading', 'OneMoar')
		self.text = kwargs.get('text')
		self.background = 'FF302F2F'
		self.titlebar = 'FF37B6FF'
		self.titletext = 'FFE68B00'
		self.textcolor = 'FFF5F5F5'

	def onInit(self):
		self.set_properties()
		self.setFocusId(self.window_id)

	def run(self):
		self.doModal()
		self.clearProperties()

	def onAction(self, action):
		if action in self.closing_actions or action in self.selection_actions:
			self.close()

	def set_properties(self):
		self.setProperty('onemoar.text', self.text)
		self.setProperty('onemoar.heading', self.heading)
		self.setProperty('onemoar.background', self.background)
		self.setProperty('onemoar.titlebar', self.titlebar)
		self.setProperty('onemoar.titletext', self.titletext)
		self.setProperty('onemoar.textcolor', self.textcolor)
