from __future__ import with_statement
import Live
from _Framework.ControlSurface import ControlSurface
from _Framework.DeviceComponent import DeviceComponent
from _Framework.MixerComponent import MixerComponent # Class encompassing several channel strips to form a mixer
from _Framework.SliderElement import SliderElement
from _Framework.TransportComponent import TransportComponent
from _Framework.InputControlElement import *
from _Framework.ButtonElement import ButtonElement
from _Framework.ButtonMatrixElement import ButtonMatrixElement
from _Framework.SessionComponent import SessionComponent

class midi_twister_110(ControlSurface):

	def __init__(self, c_instance):
		super(midi_twister_110, self).__init__(c_instance)
		with self.component_guard():
			global active_mode
			active_mode = "_mode1"
			self._set_active_mode()
			self.show_message("Modified by XXPW")

	def _mode1(self):
		self.show_message("_mode1 is active")
		# mixer
		global mixer
		num_tracks = 32
		num_returns = 7
		self.mixer = MixerComponent(num_tracks, num_returns)
		self.mixer.set_track_offset(0)
		self.song().view.selected_track = self.mixer.channel_strip(0)._track
		# sends
		send0_controls = (
			SliderElement(MIDI_CC_TYPE, 0, 32),
			SliderElement(MIDI_CC_TYPE, 0, 36),
			SliderElement(MIDI_CC_TYPE, 0, 40),
			None,
			None,
			None,
			None,
			None,
		);
		self.mixer.channel_strip(0).set_send_controls(tuple(send0_controls))
		self.mixer.channel_strip(0).set_volume_control(SliderElement(MIDI_CC_TYPE, 0, 44))
		send1_controls = (
			SliderElement(MIDI_CC_TYPE, 0, 33),
			SliderElement(MIDI_CC_TYPE, 0, 37),
			SliderElement(MIDI_CC_TYPE, 0, 41),
			None,
			None,
			None,
			None,
			None,
		);
		self.mixer.channel_strip(1).set_send_controls(tuple(send1_controls))
		self.mixer.channel_strip(1).set_volume_control(SliderElement(MIDI_CC_TYPE, 0, 45))

		send2_controls = (
			SliderElement(MIDI_CC_TYPE, 0, 34),
			SliderElement(MIDI_CC_TYPE, 0, 38),
			SliderElement(MIDI_CC_TYPE, 0, 42),
			None,
			None,			
			None,
			None,
			None,
		);
		self.mixer.channel_strip(2).set_send_controls(tuple(send2_controls))
		self.mixer.channel_strip(2).set_volume_control(SliderElement(MIDI_CC_TYPE, 0, 46))
		send3_controls = (
			SliderElement(MIDI_CC_TYPE, 0, 35),
			SliderElement(MIDI_CC_TYPE, 0, 39),
			SliderElement(MIDI_CC_TYPE, 0, 43),
			None,
			None,
			None,
			None,
			None,
		);
		self.mixer.channel_strip(3).set_send_controls(tuple(send3_controls))
		self.mixer.channel_strip(3).set_volume_control(SliderElement(MIDI_CC_TYPE, 0, 47))
		# session
		global _session
		num_tracks = 4
		num_scenes = 3
		session_buttons = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
		self._pads = [ButtonElement(1, MIDI_CC_TYPE, 1, session_buttons[index]) for index in range(num_tracks*num_scenes)]
		self._grid = ButtonMatrixElement(rows=[self._pads[(index*num_tracks):(index*num_tracks)+num_tracks] for index in range(num_scenes)])
		self._session = SessionComponent(num_tracks, num_scenes)
		self._session.set_clip_launch_buttons(self._grid)
		self.set_highlighting_session_component(self._session)
		# session track stop
		stop_track_buttons = [12, 13, 14, 15]
		self._track_stop_buttons = [ButtonElement(1, MIDI_CC_TYPE, 1, stop_track_buttons[index]) for index in range(num_tracks)]
		self._session.set_stop_track_clip_buttons(tuple(self._track_stop_buttons))
		# session navigation
		self.session_left= ButtonElement(1, MIDI_CC_TYPE, 3, 8)
		self._session.set_page_left_button(self.session_left)
		self.session_left.add_value_listener(self._reload_active_devices, identify_sender=False)
		self.session_right= ButtonElement(1, MIDI_CC_TYPE, 3, 11)
		self._session.set_page_right_button(self.session_right)
		self.session_right.add_value_listener(self._reload_active_devices, identify_sender=False)
		self.session_up= ButtonElement(1, MIDI_CC_TYPE, 3, 10)
		self._session.set_page_up_button(self.session_up)
		self.session_up.add_value_listener(self._reload_active_devices, identify_sender=False)
		self.session_down= ButtonElement(1, MIDI_CC_TYPE, 3, 13)
		self._session.set_page_down_button(self.session_down)
		self.session_down.add_value_listener(self._reload_active_devices, identify_sender=False)
		self._session._link()
		self._session.set_mixer(self.mixer)
		#self._session.set_mixer(self.mixer)
		self._mode1_devices()
		self.add_device_listeners()
		# button: next device
		self.next_device = ButtonElement(0, MIDI_CC_TYPE, 1, 25)
		self.next_device.add_value_listener(self._next_device_value, identify_sender=False)
		# button: prev device
		self.previous_device = ButtonElement(1, MIDI_CC_TYPE, 1, 24)
		self.previous_device.add_value_listener(self._prev_device_value, identify_sender=False)
		# transport
		global transport
		self.transport = TransportComponent()
		self.transport.name = 'Transport'
		loop_button = ButtonElement(1, MIDI_CC_TYPE, 1, 50)
		loop_button.name = 'loop_button'
		self.transport.set_loop_button(loop_button)
		stop_button = ButtonElement(1, MIDI_CC_TYPE, 1, 49)
		stop_button.name = 'stop_button'
		self.transport.set_stop_button(stop_button)
		play_button = ButtonElement(1, MIDI_CC_TYPE, 1, 48)
		play_button.name = 'play_button'
		self.transport.set_play_button(play_button)
		# button: track navigation right
		self.track_navigation_right = ButtonElement(1, MIDI_CC_TYPE, 3, 17)
		self.track_navigation_right.add_value_listener(self._track_navigation_right_track_nav, identify_sender=False)
		# button: track navigation left
		self.track_navigation_left = ButtonElement(1, MIDI_CC_TYPE, 3, 14)
		self.track_navigation_left.add_value_listener(self._track_navigation_left_track_nav, identify_sender=False)

	def _remove_mode1(self):
		# mixer
		global mixer
		self._remove_mode1_devices()
		self.remove_device_listeners()
		send0_controls = (
			None,
			None,
			None,
			None,
			None,
			None,
			None,
			None,
		);
		self.mixer.channel_strip(0).set_send_controls(tuple(send0_controls))
		send1_controls = (
			None,
			None,
			None,
			None,
			None,
			None,
			None,
			None,
		);
		self.mixer.channel_strip(1).set_send_controls(tuple(send1_controls))
		send2_controls = (
			None,
			None,
			None,
			None,
			None,
			None,
			None,
			None,
		);
		self.mixer.channel_strip(2).set_send_controls(tuple(send2_controls))
		send3_controls = (
			None,
			None,
			None,
			None,
			None,
			None,
			None,
			None,
		);
		self.mixer.channel_strip(3).set_send_controls(tuple(send3_controls))
		# session
		global _session
		self._session.set_clip_launch_buttons(None)
		self.set_highlighting_session_component(None)
		self._session.set_mixer(None)
		self._session.set_stop_all_clips_button(None)
		# session track stop
		self._track_stop_buttons = None
		self._session.set_stop_track_clip_buttons(None)
		# session scene launch
		self._scene_launch_buttons = None
		self._session.set_scene_launch_buttons(None)
		# session navigation
		self.session_left.remove_value_listener(self._reload_active_devices)
		self._session.set_page_left_button(None)
		self.session_right.remove_value_listener(self._reload_active_devices)
		self._session.set_page_right_button(None)
		self.session_up.remove_value_listener(self._reload_active_devices)
		self._session.set_page_up_button(None)
		self.session_down.remove_value_listener(self._reload_active_devices)
		self._session.set_page_down_button(None)
		self._session = None
		self.next_device.remove_value_listener(self._next_device_value)
		self.next_device = None
		self.previous_device.remove_value_listener(self._prev_device_value)
		self.previous_device = None
		# transport
		global transport
		self.transport.set_loop_button(None)
		self.transport.set_stop_button(None)
		self.transport.set_play_button(None)
		self.transport = None
		self.track_navigation_right.remove_value_listener(self._track_navigation_right_track_nav)
		self.track_navigation_right = None
		self.track_navigation_left.remove_value_listener(self._track_navigation_left_track_nav)
		self.track_navigation_left = None

	def _mode1_devices(self):
		global mixer
		global _session
		# device
		self.mixer.selected_strip().set_volume_control(SliderElement(MIDI_CC_TYPE, 0, 28))
		self.mixer.selected_strip().set_pan_control(SliderElement(MIDI_CC_TYPE, 0, 29))
		self.mixer.selected_strip().set_mute_button(ButtonElement(1, MIDI_CC_TYPE, 1 , 28))
		self.mixer.selected_strip().set_solo_button(ButtonElement(1, MIDI_CC_TYPE, 1 , 29))

		if (len(self.mixer.selected_strip()._track.devices) > 0):
			global device_tracktype_selected__chain_number_selected
			self.device_tracktype_selected__chain_number_selected = DeviceComponent()
			device_controls = (
				SliderElement(MIDI_CC_TYPE, 0, 16),
				SliderElement(MIDI_CC_TYPE, 0, 17),
				SliderElement(MIDI_CC_TYPE, 0, 18),
				SliderElement(MIDI_CC_TYPE, 0, 19),
				SliderElement(MIDI_CC_TYPE, 0, 20),
				SliderElement(MIDI_CC_TYPE, 0, 21),
				SliderElement(MIDI_CC_TYPE, 0, 22),
				SliderElement(MIDI_CC_TYPE, 0, 23),
			)
			self.device_tracktype_selected__chain_number_selected.set_parameter_controls(tuple(device_controls))
			self.set_device_component(self.device_tracktype_selected__chain_number_selected)
			self.device_tracktype_selected__chain_number_selected.set_on_off_button(ButtonElement(1, MIDI_CC_TYPE, 1, 26))
			self.device_tracktype_selected__chain_number_selected.set_bank_nav_buttons(ButtonElement(0, MIDI_CC_TYPE, 1, 31), ButtonElement(1, MIDI_CC_TYPE, 1, 33))



	def _remove_mode1_devices(self):
		global mixer
		global _session
		# device
		if (hasattr(self, 'device_tracktype_selected__chain_number_selected')):
			global device_tracktype_selected__chain_number_selected
			device_controls = (
				None,
				None,
				None,
				None,
				None,
				None,
				None,
				None,
			)
			self.device_tracktype_selected__chain_number_selected.set_parameter_controls(tuple(device_controls))
			self.device_tracktype_selected__chain_number_selected.set_on_off_button(None)
			self.device_tracktype_selected__chain_number_selected.set_bank_nav_buttons(None, None)
			self.set_device_component(self.device_tracktype_selected__chain_number_selected)

	def add_device_listeners(self):
		global mixer
		num_of_tracks = len(self.song().tracks)
		value = "add device listener"
		for index in range(num_of_tracks):
			self.song().tracks[index].add_devices_listener(self._reload_active_devices)

	def remove_device_listeners(self):
		global mixer
		num_of_tracks = len(self.song().tracks)
		value = "remove device listener"
		for index in range(num_of_tracks):
			self.song().tracks[index].remove_devices_listener(self._reload_active_devices)

	def _on_selected_track_changed(self):
		ControlSurface._on_selected_track_changed(self)
		self._display_reset_delay = 0
		value = "selected track changed"
		self._reload_active_devices(value)

	def _reload_active_devices(self, value = None):
		self._remove_active_devices()
		self._set_active_devices()

	def _set_active_devices(self):
		global active_mode
		# activate mode
		if (active_mode == "_mode1") and (hasattr(self, '_mode1_devices')):
			self._mode1_devices()

	def _remove_active_devices(self):
		global active_mode
		# remove activate mode
		if (active_mode == "_mode1") and (hasattr(self, '_mode1_devices')):
			self._remove_mode1_devices()

	def _next_device_value(self, value):
		if value > 0:
			self._device = self.song().view.selected_track.view.selected_device
			if self._device is not None:
				self.song().view.select_device(self.song().view.selected_track.devices[self.selected_device_idx() + 1])


	def _prev_device_value(self, value):
		if value > 0:
			self._device = self.song().view.selected_track.view.selected_device
			if self._device is not None:
				self.song().view.select_device(self.song().view.selected_track.devices[self.selected_device_idx() - 1])

	def selected_device_idx(self):
		self._device = self.song().view.selected_track.view.selected_device
		return self.tuple_index(self.song().view.selected_track.devices, self._device)

	def _track_navigation_right_track_nav(self, value):
		if value > 0:
			self.song().view.selected_track = self.song().tracks[self.selected_track_idx() + 1]


	def _track_navigation_left_track_nav(self, value):
		if value > 0:
			self.song().view.selected_track = self.song().tracks[self.selected_track_idx() - 1]


	def selected_track_idx(self):
		return self.tuple_index(self.song().tracks, self.song().view.selected_track)


	def _set_active_mode(self):
		global active_mode
		# activate mode
		if active_mode == "_mode1":
			self._mode1()

	def _remove_active_mode(self):
		global active_mode
		# remove activate mode
		if active_mode == "_mode1":
			self._remove_mode1()

	def _activate_mode1(self,value):
		global active_mode
		if value > 0:
			self._remove_active_mode()
			active_mode = "_mode1"
			self._set_active_mode()

	def _activate_shift_mode1(self,value):
		global active_mode
		if value > 0:
			self._remove_active_mode()
			self._mode1()
		else:
			self._remove_mode1()
			self._set_active_mode()

	def tuple_index(self, tuple, obj):
		for i in xrange(0, len(tuple)):
			if (tuple[i] == obj):
				return i
		return(False)

	def disconnect(self):
		super(midi_twister_110, self).disconnect()
