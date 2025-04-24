from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
import openai
from alpha_mini_rug.speech_to_text import SpeechToText 

audio_processor = SpeechToText() # create an instance of the class  # changing these values might not be necessary 
audio_processor.silence_time = 0.5 # parameter set to indicate when to stop recording 
audio_processor.silence_threshold2 = 100 # any sound recorded below this value is considered silence   
audio_processor.logging = False # set to true if you want to see all the output 


openai.api_key = "api key" 

def request_to_chatgpt(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[
            {"role": "system", "content": "You are a smart friendly robot helping elderly people. Answer in short sentences."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

@inlineCallbacks
def main(session, details):
    yield session.call("rom.optional.behavior.play", name="BlocklyStand")
    yield session.call("rie.dialogue.say_animated", text="Hey there! How are you doing?")
    yield sleep(2)

    yield session.call("rom.sensor.hearing.sensitivity", 1650)   
    yield session.call("rie.dialogue.config.language", lang="en")  
    print("listening to audio")  
    yield session.subscribe(audio_processor.listen_continues, "rom.sensor.hearing.stream")  
    yield session.call("rom.sensor.hearing.stream") 

    x=True
    while x:      
        if not audio_processor.new_words:          
            yield sleep(0.5)  # VERY IMPORTANT, OTHERWISE THE CONNECTION TO THE SERVER MIGHT CRASH          
            print("I am recording")      
        else:          
            word_array = audio_processor.give_me_words()          
            print("I'm processing the words")          
            print(word_array[-3:])  # print last 3 sentences 
            x=False

        audio_processor.loop()  
    
    question = word_array[0][0]
    answer = request_to_chatgpt(question)
    yield session.call("rie.dialogue.say_animated", text=answer)

    yield sleep(2)
    yield session.call("rom.optional.behavior.play", name="BlocklyWaveRightArm")
    session.leave() 

wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"],
        "max_retries": 0
    }],
    realm="rie.6808d8fc29c04006ecc04b78",
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
