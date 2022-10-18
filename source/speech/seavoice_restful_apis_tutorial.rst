.. _seavoice_restful_apis_tutorial:

SeaVoice RESTful APIs
=====================

This is the tutorial about how to use SeaVoice RESTful APIs to try Seasalt Speech-To-Text (STT) and Text-To-Speech (TTS) services.

Please contact info@seasalt.ai if you have any questions.

.. contents:: Table of Contents
    :local:
    :depth: 3

STT protocols
-------------

1. Get ``speech_service_token``: send POST request to API: ``https://suite.seasalt.ai/api/v1/user/login``

    .. code-block:: JSON

        {
            "account_id": "<username>",
            "password": "<password>"
        }

    - CLI example:

        .. code-block:: bash

            curl -X 'POST' -d '{"account_id": <username>, "password": <password>}' 'https://suite.seasalt.ai/api/v1/user/login'
            # return example: {"user_id": <username>, "timestamp":"2022-03-17T16:43:40", "token": <speech_service_token>, "role_id":2}

    - Python example:

        .. code-block:: python

            import requests
            data = {
                "account_id": <username>,
                "password": <password>,
                "entry": "not_userboard",
            }
            url = 'https://suite.seasalt.ai/api/v1/user/login'
            res = requests.post(url, json=data)
            assert res.status_code == 200, res.status_code
            print(res.json()["token"]) # this is the speech_service_token

2. Get ``api_key`` and STT ``server_url``: send POST request with ``language`` and ``speech_service_token`` to API server: ``https://suite.seasalt.ai/api/v1/speech/speech_to_text``. ``language`` currently supports ``en-US`` and ``zh-TW``.

    - Python example:

        .. code-block:: python
            import requests
            headers = {'token': speech_service_token}
            data = {"language": "zh-TW"}
            response = requests.post("https://suite.seasalt.ai/api/v1/speech/speech_to_text",
                                    headers=headers, json=data)
            print(response.json()) # return example: {'token': <api_key>, 'server_url': 'wss://<host>:<port>/client/ws/speech', 'account_id': <username>}

3. API server returns HTTP 200 with json string including the available TTS server's url and ``api_key`` to Client, like

.. code-block:: JSON

    {
        "account_id": "<username>",
        "server_url": "wss://<host>:<port>/client/ws/speech",
        "token": "<api_key>"
    }

If something is wrong, API server may return HTTP 404 with a json string including an error message.

4. Client connects to the available STT server by websocket with ``api_key``, ``language`` and ``punctuation`` settings, e.g. ``wss://<host>:<port>/client/ws/speech?token=<api_key>&language=zh-tw&punctuation=True``

5. STT server verifies ``api_key`` on API server, and if something is wrong, STT server will reply error message and close websocket connection:

.. code-block:: JSON

    {
        "status": 10,
        "result": "Token invalid"
    }

6. After connecting, Client starts to record the microphone and stream audio data to STT server (See below for data format).

7. STT server receives audio data and does recognition, then send recognizing/recognized results to Client, the format is,

.. code-block:: JSON

    {
        "status": 0,
	"result":
	{
	    "final": true,
	    "hypotheses":
	    [
	        {
		    "transcript": "你 好",
		    "likelihood": 377.78
		}
	    ]
	},
	"segment-start": 0.0,
	"segment-length": 2.8,
	"total-length": 3.75
    }

.. NOTE::

 - Note 1, if "status" is 0, it means no error happened.
 - Note 2, if "final" is `True`, it means this is a final recognized result; `False` means it's a recognizing result.

8. Client receives recognizing/recognized results.

9. Client closes websocket connection when finished recognizing.

Audio data format to send to STT server:
 - If the data is in wav format, which has wav head indicating audio format, then STT server will know the audio format by the wav head. Please just have wav head at the first package, wav head in other packages will be taken as audio data.
 - If the data is in raw format, then when connecting to STT server, Client needs to include Content-Type in wss url. The format looks like
   ``&content-type=audio/x-raw, layout=(string)interleaved, rate=(int)16000, format=(string)S16LE, channels=(int)1``
 - but Client needs to do urlencode and then connects to STT server, for example, the url with Content-Type looks like ``wss://speech.seasalt.ai:5019/client/ws/speech?token=67e44248-b473-11eb-95f1-ba52214202a6&punctuation=True&content-type=audio%2Fx-raw%2C+layout%3D%28string%29interleaved%2C+rate%3D%28int%2916000%2C+format%3D%28string%29S16LE%2C+channels%3D%28int%291``

TTS protocols
-------------

1. Log into SeaAuth: ``https://seaauth.seasalt.ai/api/v1/users/login``

.. code-block:: JSON

    {
        "username": "test",
        "password": "test",
        "scope": "seavoice"
    }


2. Obtain access token in the response

.. code-block:: JSON
    
    {
        "account": "test",
        "access_token": "eyJ0eXAiOi*****",
        "token_type": "Bearer",
        "refresh_token": "71bbffd5368*****"
    }

3. Connect to SeaVoice TTS websocket server: ``wss://seavoice.seasalt.ai/api/v1/tts/ws``

If successfully connected, Client sends json package to TTS server, for example (settings and data are shown with default values),

.. code-block:: JSON

    {
        "business":
        {
            "language": "zh_tw,
            "voice": "Tongtong",
        },
        "settings":
        {
            "pitch": 0.0,
            "speed": 1.0,
            "volume": 50.0,
            "sample_rate": 22050
            "rules": ""
        },
        "data":
        {
            "text": "this is a test"
            "ssml": True
        }
    }

.. NOTE::

  - <language> / <voice>: Choose from the following options
      - zh-TW
          - Tongtong
          - Vivian
      - en-US
          - MikeNorgaard
          - MoxieLabouche
          - LisaHenige
      
  - <pitch>
      - default: 0.0
      - range: [-5.0, 5.0] 
      - description: adjust the pitch of the synthesized voice, where positive values raise the pitch and negative values lower the pitch.
  - <speed>
      - default = 1.0
      - range: [0.0, 3.0]
      - description: adjust the speed of the synthesized voice, where values > 1.0 speed up the speech and values < 1.0 slows down the speech.
  - <volume>
      - default: 50.0
      - range: [0.0, 100.0]
      - description: adjust the volume of the synthesized voice, where values > 50.0 increases the volume and values < 50.0 decreases the volume.
  - <sample_rate>
      - default: 22050
      - range: [8000, 48000]
      - description: set the output audio sample rate
  - <rules>
      - default: (empty string)
      - description: pronunciation rules as a string in the following format "<WORD1> | <PRONUNCIATION1>\n<WORD2> | <PRONUNCIATION2>"
      - for "zh-TW", pronunciation can be specified in zhuyin, pinyin, or Chinese characters, e.g. "TSMC | 台積電\n你好 | ㄋㄧˇ ㄏㄠˇ\n為了 | wei4 le5"
      - for "en-US", pronunciation can be specified with English words, e.g. "XÆA12 | ex ash ay twelve\nSideræl|psydeereal"
  - <ssml>
      - default: false
      - description: should be True if <text> is an SSML string, i.e. using SSML tags. See :ref:`Supported SSML Tags` for more info.


6. After sending the package, Client calls ws.recv() to wait for TTS server to send the streaming audio data.

7. TTS server performs synthesis and keeps sending streaming audio data to Client. The audio package format is as follows:

.. code-block:: JSON

    {
        "status": <SEQ_STATUS>,
        "message": <MESSAGE>,
        "sid": <SEQ_ID>,
        "data":
        {
            "audio": <AUDIO_DATA>,
            "status": <STATUS>
        }
    }

.. NOTE::

    - <SEQ_STATUS>: Either "ok" or an error message
    - <MESSAGE>: Additional information based on the status
    - <SEQ_ID>: audio sequence id
    - <STATUS>: if status is 1 it means streaming synthesis is still in progress; if status is 2, it means synthesis is complete.


8. Client receives audio data frames.

9. After finishing processing all TEXT or SSML string, TTS server closes the websocket connection.


Sample Client Script
**********

1. Setup

.. code-block:: bash

    # Python venv setup (recommends using Python 3.8.10)
    python3 -m venv venv/seavoice
    source venv/seavoice/bin/activate
    pip install --upgrade pip
    pip install websockets==10.3
    pip install aiohttp==3.8.1

2. Run client script

.. code-block:: python

    #!/usr/bin/env python3
    # -*- coding: utf-8 -*-

    # Copyright 2022  Seasalt AI, Inc

    """TTS client script

    Usage:
    python tts_client.py \
      --account test \
      --password test \
      --lang en-US \
      --voice MikeNorgaard \
      --text "hello this is a test"

    `--account`: seavoice account
    `--password`: seavoice password
    `--text`: input text to synthesize, supports SSML format
    `--rules`: optional, globally applied pronunciation rules in the format of `<word> | <pronunciation>\n`
    `--pitch`: optional, adjust pitch of synthesized speech, [-5, 5] default 0.0
    `--speed`: optional, adjust speed of synthesized speech, [0, 2] default 1.0
    `--volume`: optional, adjust volume of synthesize speech, [0, 100] default 50.0
    `--sample-rate`: optional, set the sample rate of synthesized speech, default 22050
    """

    import argparse
    import asyncio
    import base64
    import json
    import wave
    from urllib.parse import urljoin

    import aiohttp
    import websockets

    SEAAUTH_SCOPE_NAME: str = "seavoice"

    VOICE_CHANNELS: int = 1
    VOICE_SAMPLE_WIDTH: int = 2

    VOICES = {
        "zh-TW": {"Tongtong", "Vivian"},
        "en-US": {"MikeNorgaard", "MoxieLabouche", "LissaHenige"}
    }


    async def main(args: argparse.Namespace):
        auth_result = await _login_seaauth(args)
        await _do_tts(args, auth_result)


    async def _login_seaauth(args: argparse.Namespace) -> dict:
        """Login with SeaAuth.
        Example of response:
            {
            "account": "test",
            "access_token": "eyJ0eXAiOi*****",
            "token_type": "Bearer",
            "refresh_token": "71bbffd5368*****"
            }
        """
        payload = {"username": args.account, "password": args.password, "scope": SEAAUTH_SCOPE_NAME}
        data = aiohttp.FormData()
        data.add_fields(*payload.items())
        async with aiohttp.ClientSession() as session:
            async with session.post(urljoin(args.seaauth_url, "/api/v1/users/login"), data=data) as response:
                if response.status >= 400:
                    raise Exception(await response.text())
                data = await response.json()
                return data


    async def _do_tts(args: argparse.Namespace, auth_result: dict):
        tts_endpoint_url = urljoin(args.seavoice_ws_url, "/api/v1/tts/ws")
        async with websockets.connect(tts_endpoint_url) as websocket:
            is_begin = asyncio.Event()
            is_sythesized = asyncio.Event()
            asyncio.create_task(_receive_events(websocket, is_begin, is_sythesized))
            await _send_authentication_command(websocket, auth_result)
            # wait until received the begin event from server
            await is_begin.wait()
            await _send_synthesis_commands(websocket, args)

            # wait for audio synthsized
            await is_sythesized.wait()
            print("tts finished")


    async def _receive_events(websocket, is_begin: asyncio.Event, is_sythesized: asyncio.Event):
        with wave.open(args.output, "w") as f:
            f.setnchannels(VOICE_CHANNELS)
            f.setsampwidth(VOICE_SAMPLE_WIDTH)
            f.setframerate(args.sample_rate)

            async for message in websocket:
                event = json.loads(message)
                event_name = event.get("event", "")
                event_payload = event.get("payload", {})
                if event_name == "info":
                    if event_payload.get("status") == "begin":
                        print(f"received an info event: {event_payload}")
                        is_begin.set()
                    elif event_payload.get("status") == "error":
                        print(f"received an error event: {event_payload}")
                elif event_name == "audio_data":
                    synthesis_status = event_payload["status"]
                    print(f"received an audio_data event, staus:{synthesis_status}")
                    # warning: it's a IO blocking operation.
                    f.writeframes(base64.b64decode(event_payload["audio"]))
                    if synthesis_status == "synthesized":
                        is_sythesized.set()
                else:
                    print(f"received an unknown event: {event}")


    async def _send_authentication_command(websocket, auth_result: dict):
        authentication_command = {
            "command": "authentication",
            "payload": {
                "token": auth_result["access_token"],
                "settings": {
                    "language": args.lang,
                    "voice": args.voice,
                },
            },
        }
        command_str = json.dumps(authentication_command)
        await websocket.send(command_str)


    async def _send_synthesis_commands(websocket, args: argparse.Namespace):
        synthesis_command = {
            "command": "synthesis",
            "payload": {
                "settings": {
                    "pitch": args.pitch,
                    "speed": args.speed,
                    "volume": args.volume,
                    "rules": args.rules,
                    "sample_rate": args.sample_rate,
                },
                "data": {"text": args.text, "ssml": True},
            },
        }
        command_str = json.dumps(synthesis_command)
        await websocket.send(command_str)


    def _determine_voice(args: argparse.Namespace):
        if args.voice:
            if args.voice not in VOICES[args.lang]:
                raise Exception("Voice selected doesn't match the language. Check supported list of lang/voices.")
            return

        if args.lang == "zh-TW":
            args.voice = "Tongtong"
        elif args.lang == "en-US":
            args.voice = "MikeNorgaard"
        else:
            raise Exception("Only supports 'zh-TW' or 'en-US' for the '--lang' option.")


    if __name__ == "__main__":
        parser = argparse.ArgumentParser()
        parser.add_argument("--account", type=str, required=True, help="account of a SeaAuth account.")
        parser.add_argument("--password", type=str, required=True, help="password of a SeaAuth account.")
        parser.add_argument(
            "--lang",
            type=str,
            required=True,
            help='Language of TTS server, must in ["zh-TW", "en-US"]')
        parser.add_argument(
            "--voice",
            type=str,
            default="",
            help="Voice of the synthesized speech.",
        )
        parser.add_argument(
            "--text",
            type=str,
            required=True,
            help="Text to synthesize. Supports SSML text.",
        )
        parser.add_argument(
            "--seaauth_url",
            type=str,
            required=False,
            default="https://seaauth.seasalt.ai",
            help="Url of SeaAuth.",
        )
        parser.add_argument(
            "--seavoice_ws_url",
            type=str,
            required=False,
            default="wss://seavoice.seasalt.ai",
            help="Url of SeaVoice.",
        )
        parser.add_argument(
            "--rules",
            type=str,
            required=False,
            default="",
            help="Global pronunciation rules.",
        )
        parser.add_argument(
            "--output",
            type=str,
            default="test_audio.wav",
            help="Path to output audio file.",
        )
        parser.add_argument(
            "--sample-rate",
            type=int,
            default=22050,
            help="Optional, set the sample rate of synthesized speech, default 22050.",
        )
        parser.add_argument(
            "--pitch",
            type=float,
            default=0.0,
            help="Optional, adjust pitch of synthesized speech, [-5, 5] default is 0.0",
        )
        parser.add_argument(
            "--speed",
            type=float,
            default=1.0,
            help="Optional, adjust speed of synthesized speech, [0.0, 2.0] default is 1.0",
        )
        parser.add_argument(
            "--volume",
            type=float,
            default=50.0,
            help="Optional, adjust volume of synthesize speech, [0.0, 100.0] default is 50.0",
        )

        args = parser.parse_args()
        _determine_voice(args)
        asyncio.run(main(args))



Supported SSML Tags
**********

1. Break

Description: Add pauses to the synthesized speech, measured in milliseconds.

Format: ``<break time="100ms"/>``

Examples:

- ``今天<break time="100ms"/>的日期是3/22/2022``
- ``Today <break time="100ms"/> the date is 3/22/2022``

2. Alias
Description: Specify pronunciation.

Format:  ``<alias alphabet=”{sub|arpabet|zhuyin|pinyin}” ph='...'>...</alias>``

Examples:

- ``<alias alphabet='sub' ph='see salt dot ay eye'>Seasalt.ai</alias>``
- ``代碼<alias alphabet='sub' ph='維'>為</sub>``
- ``<alias alphabet='arpabet' ph='HH AH0 L OW1'>hello</alias>``
- ``代碼<alias alphabet='zhuyin' ph='ㄨㄟˊ'>為</alias>``
- ``代碼<alias alphabet='pinyin' ph='wei2'>為</alias>``

3. Say-as

Description: Specify how to interpret ambiguous text like numbers and dates.

Format: ``<say-as interpret-as='{digits|cardinal|spell-out|date}' format='{phone|social|m/d/Y|...}'>...</say-as>``

Examples:

- ``Today is <say-as interpret-as='date' format='m/d/Y'>2/11/2022</say-as>``
- ``my phone number is <say-as interpret-as='digits' format='phone'>7145262155</say-as>``
- ``the word diarization is spelled <say-as interpret-as='spell-out'>diarization</say-as>``
- ``今天的日期是<say-as interpret-as='date' format='m/d/Y'>3/15/2022</say-as>``
- ``我的電話號碼是<say-as interpret-as='digits' format='mobile'>1234567890</say-as>``
- ``訂位代碼為<say-as interpret-as='spell-out'>5VOPXT</say-as>``
- ``訂位代碼為<say-as interpret-as='spell-out' time='600ms'=>5VOPXT</say-as>``
