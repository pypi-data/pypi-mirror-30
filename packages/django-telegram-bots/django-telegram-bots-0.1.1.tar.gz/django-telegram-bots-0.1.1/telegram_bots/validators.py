message_schema = {
	'bot': {
		'type': 'int',
		'coerce': int,
		'required': True,
		'empty': False
	},
	'type': {
		'type': 'list',
		'allowed': ['HTML', 'Markdown', 'Text'],
		'required': True,
		'empty': False
	},
	'message': {
		'type': 'string',
		'minlength': 1,
		'required': True,
		'empty': False
	},
	'chat_ids': {
		'type': 'list',
		'required': True,
		'empty': False
	}
}
