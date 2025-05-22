from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep

@inlineCallbacks
def main(session, details):
	yield session.call("rom.optional.behavior.play", name="BlocklyStand")
	yield sleep(2)
	yield session.call("rom.optional.behavior.play", name="BlocklyMacarena")
	yield sleep(2)
	yield session.call("rie.dialogue.say", text="bombardillo crocodillo")
	session.leave() 

wamp = Component(
	transports=[{
		"url": "ws://wamp.robotsindeklas.nl",
		"serializers": ["msgpack"],
		"max_retries": 0
	}],
	realm="rie.68245ea644932a6a6ce018bd",
)

wamp.on_join(main)

if __name__ == "__main__":
	run([wamp])