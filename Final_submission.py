# Import libraries
import speech_recognition as sr  # recognises speech from audio
import pyttsx3  # text to speech conversion (Robot voice)
import sounddevice as sd  # records audio from the microphone
import numpy as np  # maths operations for audio data processing
import wave  # save audio in WAV format
import re  # for regular expression operations (not used explicitly in this code, but useful for pattern matching)

# initialize the text-to-speech engine to make the robot speak
engine = pyttsx3.init()


# function to record the audio using sounddevice library
def record_audio(duration=4, fs=44100):
    """
    Record audio for a given duration and save it as a WAV file.
    """
    print("Start speaking...")  # notify user to speak

    # record audio for a 4s duration at a sample rate of 44100 Hz (standard rate for good audio quality)
    audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')  # record audio as an array of integers
    sd.wait()  # wait for recording to finish

    print("Recording finished.")  # notify user that the recording is done

    # Save the recorded audio to a WAV file
    with wave.open('user_input.wav', 'wb') as wf:  # Open a file in write-binary mode
        wf.setnchannels(1)  # Set the number of audio channels = 1 for mono sound
        wf.setsampwidth(2)  # Set the sample width in this instance 2 = 16 bits per sample
        wf.setframerate(fs)  # Set the sample rate (44100kHz samples per second)
        wf.writeframes(audio_data.tobytes())  # write the recorded audio data as bytes into the file

    return 'user_input.wav'  # return file name for the recorded audio


# function to convert speech to text using the Speech recognition API
def speech_to_text(audio_file):
    """
    Convert the speech in an audio file to text using Google's Speech Recognition API.
    """
    recognizer = sr.Recognizer()  # recognizer object to recognize speech

    # Open the audio file and recognize the speech in it
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)  # Read the audio file

    try:
        print("Recognizing...")  # notify the user that the recognition process is in progress
        text = recognizer.recognize_google(audio)  # Use Google's STT API to convert speech to text
        return text.lower()  # Return the text in lowercase for easier comparison
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio.")  # error if the audio is unclear
        return None  # return nothing if speech wasnt recognised
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")  # Error if API request fails
        return None  # return nothing if there is a request error


# Function to make the robot speak
def speak(text):
    """
    Speak the given text using text-to-speech engine.
    """
    engine.say(text)  # Convert text to speech
    engine.runAndWait()  # Wait until the speech finishes


# Function to check for specific commands in the user's speech (using keyword matching) and return appropriate responses
def match_command(user_command):
    """
    Match keywords in user speech and return an appropriate response.
    """
    user_command = user_command.lower()  # Convert the user command to lowercase for easier matching

    # Check if the user is asking about the weather
    if 'weather' in user_command:
        if 'today' in user_command or 'now' in user_command or 'current' in user_command:
            return "The sun is shining with highs of 18°C."  # Respond with today's weather
        elif 'tomorrow' in user_command or 'next day' in user_command:
            return "It looks like it will be rainy and windy tomorrow."  # Respond with tomorrow's weather
        elif 'weekend' in user_command:  # Check if the user is asking about the weekend
            return "Saturday will be hot with no wind, and Sunday will be cooler with passing showers."  # Respond with weekend weather
        else:
            return "Which day are you asking about? Today, tomorrow, or the weekend?"  # Ask the user for clarification

        # Handle both sunrise and sunset together
    elif 'sunrise' in user_command and 'sunset' in user_command:
        return "The sun is set to rise at 7:20 AM tomorrow and set at 4:45 PM tomorrow."  # Respond with both sunrise and sunset times

    # Handle sunrise queries
    elif 'sunrise' in user_command:
        if 'time' in user_command:
            return "The sunrise will be at 7:20 AM tomorrow."  # Respond with sunrise time
        else:
            return "What time is the sunrise?"

    # Handle sunset queries
    elif 'sunset' in user_command:
        if 'time' in user_command:
            return "The sunset will be at 4:45 PM tomorrow."  # Respond with sunset time
        else:
            return "What time is the sunset?"

    # Handle greeting commands accepting Hello, Hey or Hi
    elif 'hello' in user_command or 'hey' in user_command or 'hi' in user_command:
        return "Hello! How can I help you today, I can help you with the weather today, tomorrow or the weekend. Or I can tell you when the sunrise and sunset will be tomorrow?"  # Greet the user

    # Handle goodbye or thank you commands accepting Goodbye and Thank you
    elif 'goodbye' in user_command or 'thank you' in user_command:
        return "Goodbye, have a nice day!"  # Say goodbye to the user

    # Catch-all for unrecognized commands
    else:
        return "I'm sorry, I didn't understand that. Could you say it again?"  # Respond if the command was not recognized


# Main function to handle the conversation loop
def main():
    """
    Main function to handle the interaction between the user and the robot.
    """
    first_interaction = True  # Flag to check if it's the first interaction with the user
    weather_timeframe_asked = False  # Flag to track if the robot asked about the timeframe of the weather
    mis_understood = False  # Flag to track if the robot didn't understand the user's command

    while True:  # Infinite loop to keep the conversation going
        # Record user's audio input
        audio_file = record_audio()

        # Convert the recorded audio into text using speech recognition
        user_command = speech_to_text(audio_file)

        if user_command:
            print(f'User says: "{user_command}"')  # Display what the user said

            # Get a response from the robot based on the user's command using the match_command function
            robot_response = match_command(user_command)

            # Speak the robot's response
            print(f'Robot responds: "{robot_response}"')
            speak(robot_response)

            # Check if the user said goodbye or thank you and end the conversation if so
            if "goodbye" in user_command or "thank you" in user_command:
                print("Ending conversation.")  # End the conversation
                break  # Exit the loop and stop the program

            # Skip asking "Anything else?" after the first interaction to avoid redundancy
            if first_interaction:
                first_interaction = False  # Update the flag after the first interaction
                continue  # Skip asking for more input right after greeting

            # Track if the robot has already asked for the weather timeframe (today or tomorrow)
            if "Which day are you asking about? Today, tomorrow, or the weekend?" in robot_response:
                weather_timeframe_asked = True  # Set flag if timeframe was asked
            elif "I'm sorry, I didn't understand that. Could you say it again?" in robot_response:
                mis_understood = True  # Set flag if the robot didn't understand

            # Skips asking "Anything else?" if the system is already addressing a misunderstanding or timeframe question, this is why the flags are used to avoid redundancy
            if weather_timeframe_asked or mis_understood:
                weather_timeframe_asked = False  # Reset flags after skipping
                mis_understood = False
                continue  # Skip asking anything else

            # After the first interaction, ask if the user needs further assistance
            print("Robot: Anything else?")
            speak("Anything else?")

            # If the user says "no" or "nothing", end the conversation
            if user_command and ('no' in user_command or 'nothing' in user_command):
                print("Robot says: Goodbye.")  # Goodbye message
                speak("Goodbye, have a nice day!")
                break  # End the conversation


# Run the main function when the script is executed
if __name__ == "__main__":
    main()  # Call the main function to start the program