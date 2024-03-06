.. _seavoice_sdk_python_tutorial:

SeaVoice Python SDK
===================

.. meta::
    :keywords: text to speech, speech to text, python, sdk, documentation, tutorial, customization
    :description lang=en: python sdk tutorial for seavoice cutting edge text to speech and speech to text services
    :description lang=zh: seavoice最先進的語音轉文字以及文字轉語音服務的python軟件開發套件的教學文檔


This is the tutorial about how to use SeaVoice Python SDK to try Seasalt.ai Speech-To-Text (STT) and Text-To-Speech (TTS) services.

Please contact info@seasalt.ai if you have any questions.

.. contents:: Table of Contents
    :local:
    :depth: 3


Prerequisites
-------------

You will need a SeaVoice speech service account to run the following examples. Please contact info@seasalt.ai to apply for the SEAVOICE_TOKEN.


Speech-to-Text Example:
-----------------------

Install and import
~~~~~~~~~~~~~~~~~~

To install SeaVoice SDK:

``pip install seavoice-sdk-test``

To import SeaVoice SDK:

``import seavoice_sdk_beta.speech as speechsdk``

Recognition
~~~~~~~~~~~

In the example below, we show how to recognize speech from an audio file. You can also apply recognition to an audio stream.

Speech Configuration
^^^^^^^^^^^^^^^^^^^^

Use the following code to create ``SpeechConfig``:

::

        recognizer = SpeechRecognizer(
            token=SEAVOICE_TOKEN,
            language=LanguageCode.EN_US,
            sample_rate=16000,
            sample_width=2,
            enable_itn=True,
            contexts={},
            context_score=0
        )


.. NOTE::
    - ``language``: Input audio language, choose from ``LanguageCode.ZH_TW``, ``LanguageCode.EN_US``
    - ``enable_itn``: Whether to run Inverse Text Normalisation (ITN) to add punctuation and output written form instead of spoken form, i.e. output words like ``Mr.`` instead of ``mister``
    - ``contexts``: A json dict to boost certain hotwords and/or phrases for recognition, and optionally rewrite certain spoken forms to a specific written form. Each key is a word/phrase for context biasing; each corresponding value is an optional dict containing a key 'rewrite' which maps to a list of possible spoken forms that will be rewritten to the written form (the key). In the above example, the word "seasalt" will be boosted and all occurences of "sea salt" and "c salt" will be rewritten to the capitalised "Seasalt". Also, if a certain sentence is expected, you can also boost the whole sentence, e.g. "Seasalt is an AI company"

        ::

                contexts =  {
                    "Seasalt": {
                        "rewrite": ["sea salt", "c salt"]
                    },
                    "SeaVoice": {
                        "rewrite": ["c voice"]
                    }
                }
                
    - ``context_score``: The strength of the above provided ``contexts``. We recommend starting with a score of 2.0 and try it out.

Recognizing speech
^^^^^^^^^^^^^^^^^^

Now we use the recognizer to send audio at ``audio_path`` for recognition. 

::

            async with recognizer:
                async def _send():
                    with wave.open(audio_path, mode="rb") as audio_file:
                        frames = audio_file.readframes(frames_sent_per_command)
                        while frames:
                            await recognizer.send(frames)
                            frames = audio_file.readframes(frames_sent_per_command)
                    await recognizer.finish()

                asyncio.create_task(_send())
                async for event in recognizer.stream():
                    print(event)

.. Note::
    ``frames_sent_per_command``: you can add ``asyncio.sleep()`` depending on the number of frames sent for each chunk to mimic a streaming setting with local audio file testing.

    There are three types of events from the recognizer:

    - ``InfoEvent`` : contains the recognition status of one of the following ``SpeechStatus.BEGIN``, ``SpeechStatus.END``, ``SpeechStatus.ERROR``
    - ``RecognizingEvent`` : contains the following information

        - ``text``: this is the partial transcription that might change in the ``RecognizedEvent``
        - ``segment_id``: 0-based index of this recognizing segment.
        - ``voice_start_time``: timestamp in seconds of the start of this segment relative to the start of the audio.
        - ``word_alignments``: a list of ``WordAlignment`` objects containing the start timestamp of each word relative to the start of the audio.
    - ``RecognizedEvent`` : similar to the ``RecognizingEvent`` with an additional ``duration`` in seconds for this recognized segment.

    Here are some examples of the events:
    ::
        
            InfoEvent(payload=InfoEventPayload(status='begin'))
            RecognizingEvent(payload=RecognizingEventPayload(segment_id=4, text=' how much', voice_start_time=29.17, word_alignments=[WordAlignment(word='how', start=29.169998919963838, length=1), WordAlignment(word='much', start=29.32999891638756, length=1)]))
            RecognizedEvent(payload=RecognizedEventPayload(segment_id=4, text=' How much it was? ', voice_start_time=29.17, word_alignments=[WordAlignment(word='How', start=29.169998919963838, length=1), WordAlignment(word='much', start=29.32999891638756, length=1), WordAlignment(word='it', start=29.609998917579652, length=1), WordAlignment(word='was?', start=29.68999890089035, length=1)], duration=0.67))



Putting everything together
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now, put everything together and run the example:

::

        #!/usr/bin/env python3
        # -*- coding: utf-8 -*-

        import os
        import asyncio
        import wave
        import argparse

        from seavoice_sdk_beta import LanguageCode, SpeechRecognizer
        from seavoice_sdk_beta.events import InfoEvent

        async def recognize(
            audio_path: str,
            language: LanguageCode,
            sample_rate: int,
            sample_width: int = 2,
            frames_sent_per_command: int = 150,
        ):
            seavoice_token = os.getenv("SEAVOICE_TOKEN", None)
            assert seavoice_token, "SEAVOICE_TOKEN is not set."
            recognizer = SpeechRecognizer(
                token=seavoice_token,
                language=language,
                sample_rate=sample_rate,
                sample_width=sample_width,
                enable_itn=True,
                contexts={},
                context_score=0
            )

            async with recognizer:
                async def _send():
                    with wave.open(audio_path, mode="rb") as audio_file:
                        frames = audio_file.readframes(frames_sent_per_command)
                        while frames:
                            await recognizer.send(frames)
                            frames = audio_file.readframes(frames_sent_per_command)

                    await recognizer.finish()

                asyncio.create_task(_send())
                async for event in recognizer.stream():
                    if type(event) is InfoEvent:
                        print(f"{type(event).__name__}: status {event.payload.status}")
                    else:
                        print(f"{type(event).__name__}: {event.payload.text}")

        if __name__ == "__main__":
            parser = argparse.ArgumentParser()
            parser.add_argument("--audio", type=str, required=True,
                                help="path to the audio file to be recognized")
            parser.add_argument("--sample-rate", type=int, required=True,
                                help="sample rate of the audio")
            parser.add_argument("--language", type=str, required=True,
                                help="language of the provided audio, choose from 'en' and 'zh'")
            args = parser.parse_args()
            if args.language == "en":
                lang = LanguageCode.EN_US
            elif args.language == "zh":
                lang = LanguageCode.ZH_TW
            else:
                raise Exception("for 'language', choose from 'en', 'zh'")
            
            asyncio.run(recognize(args.audio, language=lang, sample_rate=args.sample_rate))


Text-to-Speech Example:
-----------------------

Install and import
~~~~~~~~~~~~~~~~~~

To install SeaVoice SDK:

``pip install seavoice-sdk-test``

To import SeaVoice SDK:

``import seavoice_sdk_beta as speechsdk``

Synthesis
~~~~~~~~~

In the example below, we show how to synthesize text to generate an
audio file. You can also receive synthesis results from an audio stream.

Voice Configuration
^^^^^^^^^^^^^^^^^^^^

Use the following code to create ``SpeechSynthesizer`` and ``SynthesisSettings`` (contact info@seasalt.ai for the SEAVOICE_TOKEN):

::

        from seavoice_sdk_beta import SpeechSynthesizer, LanguageCode, Voice
        from seavoice_sdk_beta.commands import SynthesisSettings

        synthesizer = SpeechSynthesizer(
            token=SEAVOICE_TOKEN,
            language=LanguageCode.EN_US,
            sample_rate=22050,
            voice=Voice.TOMHANKS,
        )

        settings = SynthesisSettings(
            pitch=0.0,
            speed=1.0,
            volume=50.0,
            rules="Elon | eelon\nX Æ A12 | x ash ay twelve",
            sample_rate=22050,
        )

.. NOTE::
    - ``language``: choose from ``LanguageCode.ZH_TW``, ``LanguageCode.EN_US``, ``LanguageCode.EN_GB``
    - ``voice``: voice options of the synthesized audio

        - ``ZH_TW`` : choose from ``Voice.TONGTONG``, ``Voice.VIVIAN``
        - ``EN_US`` : choose from ``Voice.ROBERT``, ``Voice.TOM``, ``Voice.MIKE``, ``Voice.ANNE``, ``Voice.LISSA``, ``Voice.MOXIE``, ``Voice.REESE``
        - ``EN_GB`` : choose from ``Voice.DAVID``
    
    - ``pitch`` : to adjust the pitch of the synthesized voice, choose a value between ``-12.0`` and ``12.0``, where ``0.0`` is the default/normal value, where positive values raise the pitch and negative values lower the pitch.
    - ``speed`` : to adjust the speed of the synthesized voice, choose a value between ``0.5`` and ``2.0``, where ``1.0`` is the default/normal value, where values > 1.0 speed up the speech and values < 1.0 slows down the speech.
    - ``volume`` : to adjust the volume of the synthesized voice, choose a value between ``0.0`` and ``100.0``, where ``50.0`` is the default/normal value, where values > 50.0 increases the volume and values < 50.0 decreases the volume.
    - ``rules`` : to specify pronunciation rules for special word representations, input string in the following format ``<WORD1> | <PRONUNCIATION1>\n<WORD2> | <PRONUNCIATION2>`` where ``\n`` is the delimiter. 
        
        - ``ZH_TW`` : pronunciation can be specified in zhuyin, pinyin, or Chinese characters, e.g. “TSMC | 台積電n你好 | ㄋㄧˇ ㄏㄠˇn為了 | wei4 le5”
        - ``EN_US`` and ``EN_GB`` : pronunciation can be specified with English words, e.g. “XÆA12 | ex ash ay twelvenSideræl|psydeereal”

    - ``sample_rate``: make sure the sample rate matches the sample rate setting for the output audio file.


Text Configuration
^^^^^^^^^^^^^^^^^^^

Use the following code to create ``SynthesisData``.

::

        from seavoice_sdk_beta.commands import SynthesisData
        
        data = SynthesisData(
            text="Good morning, today's date is<say-as interpret-as='date' format='m/d/Y'>10/11/2022</say-as>",
            ssml=True,
        )

.. NOTE::
    ``text`` is the text to be synthesized. 
    ``ssml`` should be True if ``text`` is an SSML string, i.e. using SSML tags. See :ref:`Supported SSML Tags` Tags for more info.


Output File Configuration
^^^^^^^^^^^^^^^^^^^

Synthesized audio 

::

    import wave

    f = wave.open("output.wav", "w")
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(22050)



Synthesis Command
^^^^^^^^^^^^^^^^^^^

Use the following code to create ``SynthesisCommand`` using the ``SynthesisData`` and ``SynthesisSettings`` from previous steps.

::

    from seavoice_sdk_beta.commands import SynthesisCommand

    command = SynthesisCommand(
        payload=SynthesisPayload(
            data=data,
            settings=settings,
        )
    )


Putting everything together
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Now, put everything together and run the example:

::

        #!/usr/bin/env python3
        # -*- coding: utf-8 -*-

        import os
        import asyncio
        import wave

        from seavoice_sdk_beta import LanguageCode, SpeechSynthesizer, Voice
        from seavoice_sdk_beta.commands import SynthesisCommand, SynthesisData, SynthesisPayload, SynthesisSettings
        from seavoice_sdk_beta.events import AudioDataEvent

        SAMPLE_RATE: int = 8000

        async def synthesize():
            seavoice_token = os.getenv("SEAVOICE_TOKEN", None)
            assert seavoice_token, "SEAVOICE_TOKEN is not set."
            synthesizer = SpeechSynthesizer(
                token=seavoice_token,
                language=LanguageCode.ZH_TW,
                sample_rate=SAMPLE_RATE,
                voice=Voice.TONGTONG,
            )
            
            data = SynthesisData(
                text="Good morning, today's date is<say-as interpret-as='date' format='m/d/Y'>10/11/2022</say-as>",
                ssml=True,
            )
            
            settings = SynthesisSettings(
                pitch=0.0,
                speed=0.9,
                volume=100.0,
                rules="SeaX | sea x",
                sample_rate=SAMPLE_RATE,
            )
            
            command = SynthesisCommand(
                payload=SynthesisPayload(
                    data=data,
                    settings=settings,
                )
            )

            f = wave.open("output.wav", "w")
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(SAMPLE_RATE)
            
            async with synthesizer:
                async def _send():
                    await synthesizer.send(command)

                asyncio.create_task(_send())
                async for message in synthesizer.stream():
                    print(message)
                    if isinstance(message, AudioDataEvent):
                        f.writeframes(message.payload.audio)


        if __name__ == "__main__":
            asyncio.run(synthesize())


Change Log
----------

[0.2.3] - 2022-9-23

``Improvements``

- Add reconnection mechanism

[0.2.2] - 2021-8-16

``Bugfixes``

-  Some callbacks were never called

[0.2.1] - 2021-7-25

``changed sdk name to seavoice``

[0.1.14] - 2021-4-9

``Improvements``

-  Added output of post-processing result

[0.1.13] - 2021-4-1

``Improvements``

-  Added output of segment and word alignment information

[0.1.12] - 2020-12-10

``Bugfixes``

-  Remove unused variable

``Improvements``

-  Added websocket packages in requirements.txt file
