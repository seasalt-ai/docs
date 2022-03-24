.. _seavoice_sdk_python_tutorial:

SeaVoice Python SDK
===================

This is the tutorial about how to use SeaVoice Python SDK to try Seasalt.ai Speech-To-Text (STT) and Text-To-Speech (TTS) services.

Please contact info@seasalt.ai if you have any questions.

.. contents:: Table of Contents
    :local:
    :depth: 3

Speech-to-Text Example:
-----------------------

Prerequisites
~~~~~~~~~~~~~

You will need a SeaVoice speech service account to run this example. Please contact info@seasalt.ai and apply for it.

Install and import
~~~~~~~~~~~~~~~~~~

To install SeaVoice SDK:

``pip install seavoice-sdk``

To import SeaVoice SDK:

``import seavoice_sdk.speech as speechsdk``

Recognition
~~~~~~~~~~~

In the example below, we show how to recognize speech from an audio file. You can also apply recognition to an audio stream.

Speech Configuration
^^^^^^^^^^^^^^^^^^^^

Use the following code to create ``SpeechConfig`` (contact info@seasalt.ai for the speech service APIKEY):

::

        speech_config = speechsdk.SpeechConfig(
            apikey=SEASALT_APIKEY,
            speech_recognition_language="zh-TW",
            speech_recognition_punctuation=True
        )

``speech_recognition_language`` could be ``zh-TW`` or ``en-US``.

``speech_recognition_punctuation`` is used to set whether recognition results will have punctuations.

Audio Configuration
^^^^^^^^^^^^^^^^^^^

Use the following code to create ``AudioConfig``.

::

        audio_format = speechsdk.audio.AudioStreamFormat(samples_per_second=16000, bits_per_sample=16, channels=1)
        audio_stream = speechsdk.audio.PushAudioInputStream(audio_format)
        audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

Recognizer initialization
^^^^^^^^^^^^^^^^^^^^^^^^^

SpeechRecognizer can be initialzed as follows:

::

        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_config
        )

Callbacks connection
^^^^^^^^^^^^^^^^^^^^

SpeechRecognizer has 5 kinds of callbacks:

-  Recognizing - called when recognition is in progress.
-  Recognized - called when a single utterance is recognized.
-  Canceled - called when a continuous recognition is interrupted.
-  Session\_started - called when a recognition session is started.
-  Session\_stopped - called when a recognition session is stopped.

To connect the callbacks:

::

        speech_recognizer.recognizing.connect(
            lambda evt: print(f"Recognizing: {evt.result.text}"))
        speech_recognizer.recognized.connect(
            lambda evt: print(f'Recognized: {evt.result.text}'))
        speech_recognizer.canceled.connect(
            lambda evt: print(f'Canceled: {evt}'))
        speech_recognizer.session_started.connect(
            lambda evt: print(f'Session_started: {evt}'))
        speech_recognizer.session_stopped.connect(
            lambda evt: print(f'Session_stopped: {evt}'))

Recognizing speech
^^^^^^^^^^^^^^^^^^

Now it is ready to run SpeechRecognizer. SpeechRecognizer has two ways
for speech recognition:

-  Single-shot recognition - Performs recognition once. This is to
   recognize a single audio file. It stops recognition after a single
   utterance is recognized.
-  Continuous recognition (async) - Asynchronously initiates continuous
   recognition on an audio stream. Recognition results are available
   through callback functions. To stop the continuous recognition, call
   ``stop_continuous_recognition_async()``.

::

        speech_recognizer.start_continuous_recognition_async()
        # Code commented out is for Single-shot recognition.
        # speech_recognizer.recognize_once()

Putting everything together
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now, put everything together and run the example:

::

    import seavoice_sdk.speech as speechsdk
    import time

    SEASALT_APIKEY = "xxxxxxxxx"
    speech_config = speechsdk.SpeechConfig(
        apikey=SEASALT_APIKEY,
        speech_recognition_language="zh-TW",
        speech_recognition_punctuation=True
    )
    audio_format = speechsdk.audio.AudioStreamFormat(samples_per_second=16000, bits_per_sample=16, channels=1)
    audio_stream = speechsdk.audio.PushAudioInputStream(audio_format)
    audio_config = speechsdk.audio.AudioConfig(stream=audio_stream)

    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_config
    )

    done = False
    def stopped_handler(evt):
        global done
        print(f'Session_stopped: {evt}')
        done = True

    speech_recognizer.recognizing.connect(
        lambda evt: print(f"Recognizing: {evt.result.text}"))
    speech_recognizer.recognized.connect(
        lambda evt: print(f'Recognized: {evt.result.text}'))
    speech_recognizer.canceled.connect(
        lambda evt: print(f'Canceled: {evt}'))
    speech_recognizer.session_started.connect(
        lambda evt: print(f'Session_started: {evt}'))
    speech_recognizer.session_stopped.connect(stopped_handler)

    speech_recognizer.start_continuous_recognition_async()
    with open("test.wav", "rb") as audio_bytes:
        audio_stream.write(audio_bytes.read())
        audio_stream.write("EOS".encode('utf-8'))
    while not done:
        time.sleep(3)
    speech_recognizer.stop_continuous_recognition()
    print("Finished recognizing")


Text-to-Speech Example:
-----------------------

Prerequisites
~~~~~~~~~~~~~

You will need a SeaVoice speech service account to run this example. Please contact info@seasalt.ai and apply for it.

Install and import
~~~~~~~~~~~~~~~~~~

To install SeaVoice SDK:

``pip install seavoice-sdk``

To import SeaVoice SDK:

``import seavoice_sdk.speech as speechsdk``

Synthesis
~~~~~~~~~

In the example below, we show how to synthesize text to generate an
audio file. You can also receive synthesis results from an audio stream.

Speech Configuration
^^^^^^^^^^^^^^^^^^^^

Use the following code to create ``SpeechConfig`` (contact info@seasalt.ai for the speech service account):

::

        speech_config = speechsdk.SpeechConfig(
            account_id=SEASALT_ACCOUNT,
            password=PASSWORD,
            speech_synthesis_language="en-US",
            speech_synthesis_voice_name="TomHanks",
            speech_synthesis_output_format_id="riff-22khz-16bit-mono-pcm",
            speech_synthesis_output_pitch=0.0,
            speech_synthesis_output_speed=1.0
        )

Options for ``speech_synthesis_language`` could be ``zh-TW``, ``en-US`` or ``en-GB``.

For ``zh-TW``, ``speech_synthesis_voice_name`` could be ``Tongtong`` or ``Vivian``.

For ``en-US``, ``speech_synthesis_voice_name`` could be ``TomHanks``, ``ReeseWitherspoon`` or ``AnneHathaway``.
For ``en-GB``, ``speech_synthesis_voice_name`` could be ``DavidAttenborough``.

Options for ``speech_synthesis_output_format_id`` could be ``riff-22khz-16bit-mono-pcm``, ``riff-16khz-16bit-mono-pcm`` or ``riff-8khz-16bit-mono-pcm``.

``speech_synthesis_output_pitch`` could be a value between ``-12.0`` and ``12.0``, where ``0.0`` is the default/normal value.

``speech_synthesis_output_speed`` could be a value between ``0.5`` and ``2.0``, where ``1.0`` is the default/normal value.

Audio Configuration
^^^^^^^^^^^^^^^^^^^

Use the following code to create ``AudioOutputConfig``.

::

        import seavoice_sdk.audio as audio
        # Code commented out is an example for receiving synthesis results from an audio stream.
        # audio_stream = audio.AudioOutputStream()
        # audio_config = audio.AudioOutputConfig(stream=audio_stream)
        audio_config = audio.AudioOutputConfig(filename="output.wav")

Synthesizer initialization
^^^^^^^^^^^^^^^^^^^^^^^^^^

Synthesizer can be initialzed as follows:

::

        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )

Callbacks connection
^^^^^^^^^^^^^^^^^^^^

SpeechSynthesizer has 4 kinds of callbacks:

-  Synthesis\_started - called when synthesis is started.
-  Synthesizing - called when each time part of synthesis result is given.
-  Synthesis\_completed - called when all text was synthesized.
-  Synthesis\_canceled - called when synthesis is interrupted.

To connect the callbacks:

::

        speech_synthesizer.synthesis_started.connect(
            lambda : print("synthesis started"))
        speech_synthesizer.synthesizing.connect(
            lambda audio_data: print("synthesizing"))
        speech_synthesizer.synthesis_completed.connect(
            lambda audio_data: print("synthesis completed"))
        speech_synthesizer.synthesis_canceled.connect(
            lambda : print("synthesis canceled"))

Synthesizing text
^^^^^^^^^^^^^^^^^

Now it is ready to run SpeechSynthesizer. There are two ways to run
SpeechSynthesizer:

-  Synchronized - Perform synthesis until got all result.
-  Asynchronized - Start synthesis and return a
   ``speechsdk.ResultFuture``, which you could call its ``get()``
   function to wait and get synthesis result.

   ::

           # Code commented out is for synchronized synthesis
           # result = speech_synthesizer.speak_text("Input your text to synthesize here.")
           result = speech_synthesizer.speak_text_async("Input your text to synthesize here.").get()
           # Code commented out is an example for reading synthesis result from an audio stream.
           # audio_data = audio_stream.read()

Judge result reason --> Check result
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Both the synchronized and asynchronized methods return a
``speechsdk.SpeechSynthesisResult`` object, which indicates if synthesis
was completed successfully:

::

        if result.reason == speechsdk.ResultReason.ResultReason_SynthesizingAudioCompleted:
            print("finished speech synthesizing")

Putting everything together
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now, put everything together and run the example:

::

    from seavoice_sdk import speech as speechsdk
    from seavoice_sdk import audio as audio

    if __name__ == "__main__":
        SEASALT_ACCOUNT = "xxxxxxxxx"
        PASSWORD = "xxxxxxxx"
        speech_config = speechsdk.SpeechConfig(
            account_id=SEASALT_ACCOUNT,
            password=PASSWORD,
            speech_synthesis_language="en-US",
            speech_synthesis_voice_name="TomHanks",
            speech_synthesis_output_format_id="riff-22khz-16bit-mono-pcm",
            speech_synthesis_output_pitch=0.0,
            speech_synthesis_output_speed=1.0
        )
        audio_config = audio.AudioOutputConfig(filename="output.wav")
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )
        speech_synthesizer.synthesis_started.connect(
            lambda : print("synthesis started"))
        speech_synthesizer.synthesizing.connect(
            lambda audio_data: print("synthesizing"))
        speech_synthesizer.synthesis_completed.connect(
            lambda audio_data: print("synthesis completed"))
        speech_synthesizer.synthesis_canceled.connect(
            lambda : print("synthesis canceled"))

        # result = speech_synthesizer.speak_text("Seasalt.ai is a service company focusing on multi-modal AI solutions.")
        result = speech_synthesizer.speak_text_async("Seasalt.ai is a service company focusing on multi-modal AI solutions.").get()

        if result.reason == speechsdk.ResultReason.ResultReason_SynthesizingAudioCompleted:
            print("finished speech synthesizing")

Change Log
----------

[0.2.2] - 2021-8-16

``Bugfixes``

-  Some callbacks were never called

[0.2.1] - 2021-7-25

``changed sdk name to seavoice``

[0.1.14] - 2021-4-9

``Improments``

-  Added output of post-processing result

[0.1.13] - 2021-4-1

``Improments``

-  Added output of segment and word alignment information

[0.1.12] - 2020-12-10

``Bugfixes``

-  Remove unused variable

``Improvements``

-  Added websocket packages in requirements.txt file
