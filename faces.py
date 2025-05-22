from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks

# Callback function for handling detected cards in the stream
def on_card(frame):
    print(f"Card detected: {frame}")

@inlineCallbacks
def main(session, details):
    # Get information about the card detection module
    info = yield session.call("rie.vision.card.info")
    print("Card Detection Module Info:", info)

    # Wait for a single card detection frame
    yield session.call("rie.dialogue.say_animated", text="Hello there!")

    frames = yield session.call("rie.vision.card.read", time=0)  # Wait for a new card
    if frames:
        print("Single Card Frame Detected:", frames[0])

    # Start streaming card detection data
    print("Starting card detection stream...")
    yield session.subscribe(on_card, "rie.vision.card.stream")
    yield session.call("rie.vision.card.stream", time=5000)  # Stream for 5 seconds

    # Stop the stream after completion
    yield session.call("rie.vision.card.close")
    print("Card detection stream closed.")

    # End session
    session.leave()

# WAMP Component setup
wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"],
        "max_retries": 0
    }],
    realm="rie.68245ea644932a6a6ce018bd",
)

# Attach the `main` function to the WAMP component
wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
