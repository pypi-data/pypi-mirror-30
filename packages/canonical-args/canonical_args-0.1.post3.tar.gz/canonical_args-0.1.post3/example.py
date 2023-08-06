from __future__ import absolute_import

from canonical_args import arg_spec, check_args, register_spec
import json


class Obj(object):
	pass

@arg_spec(
	{
		"args": [
			{
				"name": "arg1",
				"type": str,
				"values": [
					"SAMME",
					"SAMME.R"
				]
			},
			{
				"name": "arg2",
				"type": "testfunction.Obj",
				"values": None
			}
		],
	}
)
def test(arg1, arg2):
	print arg1, arg2


@arg_spec(
	{
		"args": [
			{
				"name": "arg1",
				"type": int,
				"values": ">0"
			},
			{
				"name": "arg2",
				"type": dict({
					"arg2.1": {
						"type": int,
						"values": None
					},
					"arg2.2": {
						"type": float,
						"values": ">=0"
					}
				}),
				"values": None
			}
		],
		"kwargs": {
			"kwarg1": {
				"type": dict({
					"thing1": {
						"type": int,
						"values": None
					},
					"thing2": {
						"type": int,
						"values": None
					}
				}),
				"values": None
			}
		}
	}
)
def test2(arg1, arg2, kwarg1=None):
	print arg1, arg2, kwarg1

def test3(*args, **kwargs):
	with open("example.json") as f:
		spec = json.load(f)
	check_args(spec, args, kwargs)

	print args, kwargs
