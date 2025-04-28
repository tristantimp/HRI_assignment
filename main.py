from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
import openai
from alpha_mini_rug.speech_to_text import SpeechToText 

audio_processor = SpeechToText() # create an instance of the class  # changing these values might not be necessary 
audio_processor.silence_time = 0.5 # parameter set to indicate when to stop recording 
audio_processor.silence_threshold2 = 120 # any sound recorded below this value is considered silence   
audio_processor.logging = False # set to true if you want to see all the output 


openai.api_key = OPENAI_API_KEY

def request_to_chatgpt(prompt, history):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[
            {"role": "system", "content": "You're an AI agent responsible for social conversations with an elderly person through an Alpha Mini robot. "
            "Firstly, conduct a getting-to-know conversation. Use B1 level English language and simulate a normal getting-to-know conversation. "
            "In the first conversation that follows this prompt, the goal is to personalize yourself to fit the person you are talking to for future conversations. "
            "You also want to use the answers to the questions you ask in this introductory conversation to measure the cognitive skills of the person. "
            "Specific instructions are as follows. First off, introduce yourself by saying 'Hi, my name is Alpha and today I'll be getting to know you! What's your name?' "
            "After an answer has been received, move on to the next question: 'How do you feel about having a conversation with me, a robot?' "
            "Provide an appropriate response to the answer, then move on to the next question 'How old are you and where do you live?' "
            "At this point, try to respond to their answer with a self chosen follow-up question (max two follow-up questions per main question) so that it feels more like a dynamic conversation and less like a static interview. "
            "Do the same for the questions 'What did you study when you were younger?', 'What line of work were you in?', 'Do you have any hobbies?' "
            "and 'Is there anything else you're passionate about?' Make sure to provide a response to each answer before asking the next question, as well as asking one or two "
            "follow up questions for each answer before moving on to the next question. Ask at most one question per output." + 
            "The following is the conversation history " + history},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

@inlineCallbacks
def main(session, details):
    history = "None"

    yield session.call("rom.optional.behavior.play", name="BlocklyStand")
    yield session.call("rie.dialogue.say_animated", text="Hello there!")
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
    
            if word_array[-1][0] != "stop":
                question = word_array[-1][0] 
                answer = request_to_chatgpt(question, history)
                yield session.call("rie.dialogue.say_animated", text=answer)
                yield sleep(2)
                history += "Elderly response:" + word_array[-1][0] + " " + "GPT answer:" + answer


            if word_array[-1][0] == "stop":
                yield sleep(2)
                yield session.call("rie.dialogue.say_animated", text="Bye bye, see you next time")
                yield session.call("rom.optional.behavior.play", name="BlocklyWaveRightArm")
                cog_answer = request_to_chatgpt("The conversation has ended, evaluate the person you spoke to based on the following criteria: 1 Inattention"
                    "Does the patient have difficulty in focusing attention (for example, is he or she easily distracted) or in keeping track of what is being said?"
                    "2 Disorganised thinking Is the patient’s speech disorganised or incoherent, such as rambling or irrelevant conversation, unclear or illogical flow of ideas, or unpredictable switching from subject to subject?"
                    "3 Altered level of consciousness Overall, how would you rate this patient’s level of consciousness? Alert (normal), vigilant (hyperalert), lethargic (drowsy, easily aroused), stupor (difficult to arouse), "
                    "coma (unarousable). Any rating other than “alert” is scored as abnormal.", history)
                yield session.call("rie.dialogue.say_animated", text=cog_answer)

                x=False

        audio_processor.loop()  

    session.leave() 

wamp = Component(
    transports=[{
        "url": "ws://wamp.robotsindeklas.nl",
        "serializers": ["msgpack"],
        "max_retries": 0
    }],
    realm="rie.680f4ddd29c04006ecc069ba",
)

wamp.on_join(main)

if __name__ == "__main__":
    run([wamp])
