from autobahn.twisted.component import Component, run 
from twisted.internet.defer import inlineCallbacks 
from autobahn.twisted.util import sleep 
from time import time  
import cv2 as cv 
import numpy as np 
import wave 
import os  
from alpha_mini_rug.speech_to_text import SpeechToText  

audio_processor = SpeechToText() # create an instance of the class  # changing these values might not be necessary 
audio_processor.silence_time = 0.5 # parameter set to indicate when to stop recording 
audio_processor.silence_threshold2 = 100 # any sound recorded below this value is considered silence   
audio_processor.logging = False # set to true if you want to see all the output 

@inlineCallbacks 
def STT_continuous(session):  
    info = yield session.call("rom.sensor.hearing.info")  
    print(info)      
    yield session.call("rom.sensor.hearing.sensitivity", 1650)   
    yield session.call("rie.dialogue.config.language", lang="en")  
    yield session.call("rie.dialogue.say", text="Say something")       
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
            print(word_array[0][0])  # print last 3 sentences 
            x=False

        audio_processor.loop()   
        
@inlineCallbacks 
def main(session, details):    
    yield STT_continuous(session)   
    session.leave()    
    
    
wamp = Component(  
    transports=[      
        {          
            "url": "ws://wamp.robotsindeklas.nl",          
            "serializers": ["msgpack"],          
            "max_retries": 0, 
        } ], 
            realm="rie.6808d8fc29c04006ecc04b78", ) 

wamp.on_join(main) 

if __name__ == "__main__": run([wamp]) 