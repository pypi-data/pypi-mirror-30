from enum import Enum
from ast import literal_eval

class uint8(int): pass

class uint16(int): pass

class int8(int): pass

class int16(int): pass

class image(str): pass #file type!

class color(str): pass

class dimension(str):
	@staticmethod
	def parse(val):
		pass

class pad(str):
	@staticmethod
	def parse(val):
		return literal_eval(val)

class compound(Enum):
	none = 'none'
	top = 'top'
	bottom = 'bottom'
	left = 'left'
	right = 'right'

class justify(Enum):
	left = 'left'
	center = 'center'
	right = 'right'

class orient(Enum):
	horizontal = 'horizontal'
	vertical = 'vertical'

class anchor(Enum):
	nw = 'nw',
	n = 'n',
	ne = 'ne',
	w = 'w',
	center = 'center',
	e = 'e',
	sw = 'sw',
	s = 's',
	se = 'se'

class bitmap(Enum):
	error = 'error'
	gray75 = 'gray75'
	gray50 = 'gray50'
	gray25 = 'gray25'
	gray12 = 'gray12'
	hourglass = 'hourglass'
	info = 'info'
	questhead = 'questhead'
	question = 'question'
	warning = 'warning'

class progressmode(Enum):
	indeterminate = 'indeterminate'
	determinate = 'determinate'

class validate(Enum):
	focus = 'focus'
	focusin = 'focusin'
	focusout = 'focusout'
	key = 'key'
	all = 'all'
	none = 'none'

class activestyle(Enum):
	underline = 'underline'
	dotbox = 'dotbox'
	none = 'none'

class relief(Enum):
	flat = 'flat'
	raised = 'raised'
	sunken = 'sunken'
	groove = 'groove'
	ridge = 'ridge'

class state(Enum):
	normal = 'normal'
	disabled = 'disabled'

class selectmode(Enum):
	browse = 'browse'
	single = 'single'
	multiple = 'multiple'
	extended = 'extended'

class cursor(Enum):
	arrow = 'arrow'
	based_arrow_down = 'based_arrow_down'
	based_arrow_up = 'based_arrow_up'
	boat = 'boat'
	bogosity = 'bogosity'
	bottom_left_corner = 'bottom_left_corner'
	bottom_right_corner = 'bottom_right_corner'
	bottom_side = 'bottom_side'
	bottom_tee = 'bottom_tee'
	box_spiral = 'box_spiral'
	center_ptr = 'center_ptr'
	circle = 'circle'
	clock = 'clock'
	coffee_mug = 'coffee_mug'
	cross = 'cross'
	cross_reverse = 'cross_reverse'
	crosshair = 'crosshair'
	diamond_cross = 'diamond_cross'
	dot = 'dot'
	double_arrow = 'double_arrow'
	draft_large = 'draft_large'
	draft_small = 'draft_small'
	draped_box = 'draped_box'
	exchange = 'exchange'
	fleur = 'fleur'
	gobbler = 'gobbler'
	gumby = 'gumby'
	hand1 = 'hand1'
	hand2 = 'hand2'
	heart = 'heart'
	icon = 'icon'
	iron_cross = 'iron_cross'
	left_ptr = 'left_ptr'
	left_side = 'left_side'
	left_tee = 'left_tee'
	leftbutton = 'leftbutton'
	ll_angle = 'll_angle'
	lr_angle = 'lr_angle'
	man = 'man'
	middlebutton = 'middlebutton'
	mouse = 'mouse'
	pencil = 'pencil'
	pirate = 'pirate'
	plus = 'plus'
	question_arrow = 'question_arrow'
	right_ptr = 'right_ptr'
	right_side = 'right_side'
	right_tee = 'right_tee'
	rightbutton = 'rightbutton'
	rtl_logo = 'rtl_logo'
	sailboat = 'sailboat'
	sb_down_arrow = 'sb_down_arrow'
	sb_h_double_arrow = 'sb_h_double_arrow'
	sb_left_arrow = 'sb_left_arrow'
	sb_right_arrow = 'sb_right_arrow'
	sb_up_arrow = 'sb_up_arrow'
	sb_v_double_arrow = 'sb_v_double_arrow'
	shuttle = 'shuttle'
	sizing = 'sizing'
	spider = 'spider'
	spraycan = 'spraycan'
	star = 'star'
	target = 'target'
	tcross = 'tcross'
	top_left_arrow = 'top_left_arrow'
	top_left_corner = 'top_left_corner'
	top_right_corner = 'top_right_corner'
	top_side = 'top_side'
	top_tee = 'top_tee'
	trek = 'trek'
	ul_angle = 'ul_angle'
	umbrella = 'umbrella'
	ur_angle = 'ur_angle'
	watch = 'watch'
	xterm = 'xterm'
	X_cursor = 'X_cursor'

