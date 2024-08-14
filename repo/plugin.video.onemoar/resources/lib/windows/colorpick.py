# -*- coding: utf-8 -*-
"""
	OneMoar Add-on
"""

from resources.lib.modules import colors
from resources.lib.modules.control import dialog, setting as getSetting
from resources.lib.windows.base import BaseDialog

button_ids = (10, 11)
palettes = {'rainbow': colors.rainbow}
palette_list = list(palettes.keys())

class ColorPick(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, *args)
		self.window_id = 2000
		self.selected = None
		self.current_palette = palette_list[0]
		self.current_setting = kwargs.get('current_setting')
		self.current_value = kwargs.get('current_value')
		self.customBackgroundColor = getSetting('dialogs.customcolor')
		self.customButtonColor = getSetting('dialogs.button.color')
		self.customTitleColor = getSetting('dialogs.titlebar.color')
		self.useCustomTitleColor = getSetting('dialogs.usecolortitle') == 'true'
		self.mode = getSetting('dialogs.lightordarkmode')
		self.lightcolor = 'FFF5F5F5'
		self.darkcolor = 'FF302F2F'
		self.set_properties()
		self.make_menu()

	def onInit(self):
		win = self.getControl(self.window_id)
		win.addItems(self.item_list)
		self.setFocusId(self.window_id)
		self.getControl(self.window_id).selectItem(0)

	def run(self):
		self.doModal()
		self.clearProperties()
		return self.selected

	def onAction(self, action):
		if action in self.closing_actions: self.setFocusId(11)
		elif action in self.selection_actions:
			focus_id = self.getFocusId()
			if focus_id == 2000:
				chosen_listitem = self.item_list[self.get_position(self.window_id)]
				self.current_setting = chosen_listitem.getProperty('label')
				self.selected = self.current_setting
				self.setFocusId(10)
			elif focus_id == 10: self.close()
			elif focus_id == 11:
				self.selected = None
				self.close()
			elif focus_id == 12:
				color_value = dialog.input('Enter Color Value', defaultt=self.current_value)
				if not color_value: return
				if len(color_value) == 6:
					color_value = "FF"+color_value
				self.current_setting = color_value
				self.selected = self.current_setting
				self.close()
			else: self.palette_switcher()

	def make_menu(self):
		def builder():
			for count, item in enumerate(current_palette):
				try:
					listitem = self.make_listitem()
					listitem.setProperty('label', item)
					yield listitem
				except: pass
		current_palette = palettes[self.current_palette]
		self.item_list = list(builder())

	def set_properties(self):
		background = {'0': self.darkcolor, '1': self.lightcolor, '2': self.customBackgroundColor}[self.mode]
		titlebar = self.customTitleColor if self.useCustomTitleColor else background
		if self.mode not in ('0', '1'): self.mode = '0' if colors.isDarkColor(background) else '1'
		text = self.lightcolor if self.mode == '0' else self.darkcolor
		buttontext = self.darkcolor if self.mode == '0' else self.lightcolor
		buttontextns = self.lightcolor if self.mode == '0' else self.darkcolor
		buttonnf = '33F5F5F5' if self.mode == '0' else '33302F2F'
		if self.mode == '0' and background == titlebar: titletext = self.lightcolor
		else: titletext = self.darkcolor

		self.setProperty('onemoar.backgroundColor', background)
		self.setProperty('onemoar.titleBarColor', titlebar)
		self.setProperty('onemoar.titleTextColor', titletext)
		self.setProperty('onemoar.buttonColor', self.customButtonColor)
		self.setProperty('onemoar.buttonColorNF', buttonnf)
		self.setProperty('onemoar.buttonTextColor', buttontext)
		self.setProperty('onemoar.buttonTextColorNS', buttontextns)
		self.setProperty('onemoar.textColor', text)
		self.setProperty('current_palette', self.current_palette)

	def palette_switcher(self):
		try: self.current_palette = palette_list[palette_list.index(self.current_palette) + 1]
		except: self.current_palette = palette_list[0]
		self.reset_window(self.window_id)
		self.set_properties()
		self.make_menu()
		self.add_items(self.window_id, self.item_list)
