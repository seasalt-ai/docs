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

3. Connect to SeaVoice STT websocket server: ``wss://seavoice.seasalt.ai/api/v1/stt/ws``

If successfully connected, Client sends json packages to stt server, for example:

- authentication command

.. code-block:: JSON
    
    {
        "command": "authentication",
        "payload": {
            "token": "<ACCESS_TOKEN>",
            "settings": {
                "language": "zh-TW",
                "sample_rate": 16000,
                "itn": false,
                "punctuation": false,
            },
        }
    }

accept language: `zh-TW`, `en-US`

- start recognition command: sending audio data for recognition

.. code-block:: JSON
    
    {
        "command": "audio_data",
        "payload": {
            "audio": "<BASE64_ENCODED_AUDIO_DATA>"
        }
    }


- stop recognition command

.. code-block:: JSON

    {
        "command": "stop"
    }

4. STT server receives audio data, performs recognition, and sends recognizing/recognized events to Client

- info event (begin)

.. code-block:: JSON

    {
        "event": "info",
        "payload": {
            "status": "begin"
        }
    }

- info event (error)

.. code-block:: JSON

    {
        "event": "info",
        "payload": {
            "status": "error",
            "error": {
                "message": "<ERROR_MESSAGE>",
                "code": "<ERROR_CODE>"
            }
        }
    }

- recognizing event: intermediate streaming ASR results

.. code-block:: JSON

    {
        "event": "recognizing"
        "payload": {
            "segment_id": "<SEG_ID>",
            "text": "<PARTIAL_RESULTS>",
            "voice_start_time": 0.1
        }
    }

- recognized event: final ASR results

.. code-block:: JSON

    {
        "event": "recognized"
        "payload": {
            "segment_id": "<SEG_ID>",
            "text": "<FINAL_RESULTS>",
            "voice_start_time": 0.1,
            "duration": 2.5
        }
    }


.. NOTE::

    - ``"voice_start_time"``: timestamp in seconds of that segment relative to the start of the audio.
    - ``"duration"``: duration of that segment.


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

    """Client script for stt endpoint

    prerequisite:
    python 3.8
    python package:
    - aiohttp==3.8.1
    - websockets==10.3

    Usage:

    python stt_client.py \
        --account test \
        --password test \
        --lang zh-TW \
        --enable-itn false \
        --enable-punctuation false \
        --audio-path test_audio.wav \
        --sample-rate 8000

    `--lang`: supports `zh-tw`, `en-us`
    `--enable-itn`: true to enable inverse text normalisation
    `--enable-punctuation`: true to enable punctuation
    `--sample-rate`: optional, set the sample rate of synthesized speech
    """

    import argparse
    import asyncio
    import base64
    import json
    from enum import Enum
    from pathlib import Path
    from urllib.parse import urljoin

    import aiohttp
    import websockets

    SEAAUTH_SCOPE_NAME: str = "seavoice"
    CHUNK_SIZE: int = 5000


    class Language(str, Enum):
        EN_US = "en-US"
        ZH_TW = "zh-TW"


    async def main(args: argparse.Namespace):
        auth_result = await _login_seaauth(args.account, args.password)
        await _do_stt(args, auth_result)


    async def _login_seaauth(account: str, password: str) -> dict:
        """Login with SeaAuth.
        Example of response:
            {
                "account": "test",
                "access_token": "eyJ0eXAiOi*****",
                "token_type": "Bearer",
                "refresh_token": "71bbffd5368*****"
            }
        """
        payload = {"username": account, "password": password, "scope": SEAAUTH_SCOPE_NAME}
        data = aiohttp.FormData()
        data.add_fields(*payload.items())
        async with aiohttp.ClientSession() as session:
            async with session.post(urljoin(args.seaauth_url, "/api/v1/users/login"), data=data) as response:
                if response.status >= 400:
                    raise Exception(await response.text())
                data = await response.json()
                return data


    async def _do_stt(args: argparse.Namespace, auth_result: dict):
        stt_endpoint_url = urljoin(args.seavoice_ws_url, "/api/v1/stt/ws")
        async with websockets.connect(stt_endpoint_url) as websocket:
            is_begin, is_end = asyncio.Event(), asyncio.Event()

            await asyncio.gather(
                _receive_events(websocket, is_begin, is_end),
                _send_commands(args, auth_result, websocket, is_begin, is_end),
            )

            # wait for audio synthesized
            print("stt finished")


    async def _send_commands(
        args: argparse.Namespace,
        auth_result: dict,
        websocket,
        is_begin: asyncio.Event,
        is_end: asyncio.Event,
    ):
        await _send_authentication_command(args, websocket, auth_result)

        # wait until received the begin event from server
        await is_begin.wait()
        await _send_audio_data_chunkily(websocket, args.audio_path)
        await _send_stop_command(websocket)
        await is_end.wait()


    async def _receive_events(websocket, is_begin: asyncio.Event, is_end: asyncio.Event):
        async for message in websocket:
            event = json.loads(message)
            event_name = event.get("event", "")
            event_payload = event.get("payload", {})

            if event_name == "info":
                if event_payload.get("status") == "begin":
                    print(f"received an info begin event: {event_payload}")
                    is_begin.set()
                elif event_payload.get("status") == "error":
                    print(f"received an info error event: {event_payload}")
                    raise Exception(f"received an info error event: {event_payload}")
                elif event_payload.get("status") == "end":
                    print("received an info end event")
                    is_end.set()
                else:
                    print(f"received an unknown info event: {event}")

            elif event_name == "recognizing" or event_name == "recognized":
                print(f"received an {event_name} event: {event_payload}")

            else:
                print(f"received an unknown event: {event}")


    async def _send_stop_command(websocket):
        command_str = json.dumps({"command": "stop"})
        await websocket.send(command_str)


    async def _send_authentication_command(args: argparse.Namespace, websocket, auth_result: dict):
        authentication_command = {
            "command": "authentication",
            "payload": {
                "token": auth_result["access_token"],
                "settings": {
                    "language": args.lang,
                    "sample_rate": args.sample_rate,
                    "itn": args.enable_itn,
                    "punctuation": args.enable_punctuation,
                },
            },
        }
        command_str = json.dumps(authentication_command)
        await websocket.send(command_str)


    async def _send_audio_data_chunkily(websocket, audio_path: str):
        with open(audio_path, "rb") as f:
            while True:
                audio = f.read(CHUNK_SIZE)
                if audio == b"":
                    break
                await _send_one_audio_data_command(websocket, audio)


    async def _send_one_audio_data_command(websocket, audio: bytes):
        audio_data_command = {"command": "audio_data", "payload": base64.b64encode(audio).decode()}
        await websocket.send(json.dumps(audio_data_command))


    def _check_file_path_exists(audio_path: str):
        if not Path(audio_path).exists():
            raise Exception(f"No file exists at {audio_path}.")


    def _convert_argument_str_to_bool(args: argparse.Namespace) -> argparse.Namespace:
        args.enable_itn = args.enable_itn.lower() == "true"
        args.enable_punctuation = args.enable_punctuation.lower() == "true"
        return args


    if __name__ == "__main__":
        parser = argparse.ArgumentParser()
        parser.add_argument("--account", type=str, required=True, help="account of a SeaAuth account.")
        parser.add_argument("--password", type=str, required=True, help="password of a SeaAuth account.")
        parser.add_argument(
            "--lang",
            type=str,
            required=True,
            choices=[lang for lang in Language],
            help='Language of TTS server, must in ["zh-TW", "en-US"]',
        )
        parser.add_argument(
            "--sample-rate",
            dest="sample_rate",
            type=int,
            required=True,
            help="Set the sample rate of speech.",
        )
        parser.add_argument(
            "--audio-path",
            dest="audio_path",
            type=str,
            required=True,
            help="The path of wav file for speech to text.",
        )
        parser.add_argument(
            "--seaauth-url",
            dest="seaauth_url",
            type=str,
            required=False,
            default="https://seaauth.seasalt.ai",
            help="Url of SeaAuth.",
        )
        parser.add_argument(
            "--seavoice-ws-url",
            dest="seavoice_ws_url",
            type=str,
            required=False,
            default="wss://seavoice.seasalt.ai",
            help="Url of SeaVoice.",
        )
        parser.add_argument(
            "--enable-itn",
            dest="enable_itn",
            type=str,
            required=False,
            default="true",
            help="Enable the ITN feature(true or false), default is true.",
        )
        parser.add_argument(
            "--enable-punctuation",
            dest="enable_punctuation",
            type=str,
            required=False,
            default="true",
            help="Enable the punctuation feature(true or false), default is true.",
        )
        args = parser.parse_args()
        _check_file_path_exists(args.audio_path)
        args = _convert_argument_str_to_bool(args)
        asyncio.run(main(args))


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

If successfully connected, Client sends json packages to TTS server, for example (settings and data are shown with default values),

- authentication command

.. code-block:: JSON
    
    {
        "command": "authentication",
        "payload": {
            "token": "{access_token}",
            "settings": {
                "language": "en-US",
                "voice": "LissaHenige",
            },
        }
    }


- synthesis command

.. code-block:: JSON
    
    {
        "command": "synthesis",
        "payload": {
            "settings": {
                "pitch": 0,
                "speed": 0,
                "volume": 50,
                "rules": "",
                "sample_rate": 8000,
            },
            "data": {
                "text": "test",
                "ssml": true
            }
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
          - LissaHenige
      
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
      --lang zh-TW \
      --voice Tongtong \
      --text "你好這裡是nxcloud，今天的日期是<say-as interpret-as='date' format='m/d/Y'>10/11/2022</say-as>" \
      --rules "nxcloud | 牛信雲\n"

    `--lang`: supports `zh-tw`, `en-us`, `en-gb`
    `--text`: input text to synthesize, supports SSML format
    `--rules`: optional, globally applied pronunciation rules in the format of `<word> | <pronunciation>\n`
    `--pitch`: optional, adjust pitch of synthesized speech, must be > 0.01 or < -0.01
    `--speed`: optional, adjust speed of synthesized speech, must be > 1.01 or < 0.99
    `--sample-rate`: optional, set the sample rate of synthesized speech
    """

    import argparse
    import asyncio
    import base64
    import json
    import wave
    from enum import Enum
    from urllib.parse import urljoin

    import aiohttp
    import websockets

    SEAAUTH_SCOPE_NAME: str = "seavoice"

    VOICE_CHANNELS: int = 1
    VOICE_SAMPLE_WIDTH: int = 2


    class Voices(str, Enum):
        TONGTONG = "Tongtong"
        VIVIAN = "Vivian"
        MIKE_NORGAARD = "MikeNorgaard"
        MOXIE_LABOUCHE = "MoxieLabouche"
        LISSA_HENIGE = "LissaHenige"


    class Language(str, Enum):
        EN_US = "en-US"
        ZH_TW = "zh-TW"


    VOICES_LANGUAGES_MAPPING = {
        Voices.TONGTONG: [Language.ZH_TW],
        Voices.VIVIAN: [Language.ZH_TW],
        Voices.MIKE_NORGAARD: [Language.EN_US],
        Voices.MOXIE_LABOUCHE: [Language.EN_US],
        Voices.LISSA_HENIGE: [Language.EN_US],
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
            await asyncio.gather(
                _receive_events(websocket, is_begin, is_sythesized),
                _send_commands(args, auth_result, websocket, is_begin, is_sythesized),
            )
            print("tts finished")


    async def _send_commands(
        args: argparse.Namespace,
        auth_result: dict,
        websocket,
        is_begin: asyncio.Event,
        is_sythesized: asyncio.Event,
    ):
        await _send_authentication_command(websocket, auth_result)
        # wait until received the begin event from server
        await is_begin.wait()
        await _send_synthesis_commands(websocket, args)

        # wait for audio synthsized
        await is_sythesized.wait()
        await websocket.close()


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
                        raise Exception(f"received an error event: {event_payload}")
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


    def _check_voice(args: argparse.Namespace):
        if args.lang not in VOICES_LANGUAGES_MAPPING[args.voice]:
            raise Exception(
                f"{args.voice} only support {','.join(VOICES_LANGUAGES_MAPPING[args.voice])}, the input is {args.lang}."
            )


    if __name__ == "__main__":
        parser = argparse.ArgumentParser()
        parser.add_argument("--account", type=str, required=True, help="account of a SeaAuth account.")
        parser.add_argument("--password", type=str, required=True, help="password of a SeaAuth account.")
        parser.add_argument(
            "--lang",
            type=str,
            required=True,
            choices=[lang for lang in Language],
            help='Language of TTS server, must in ["zh-TW", "en-US"]',
        )
        parser.add_argument(
            "--voice",
            type=str,
            required=True,
            choices=[voice for voice in Voices],
            help="Voice of the synthesized.",
        )
        parser.add_argument(
            "--text",
            type=str,
            required=True,
            help="Text to synthesize. Supports SSML text.",
        )
        parser.add_argument(
            "--seaauth-url",
            dest="seaauth_url",
            type=str,
            required=False,
            default="https://seaauth.seasalt.ai",
            help="Url of SeaAuth.",
        )
        parser.add_argument(
            "--seavoice-ws-url",
            dest="seavoice_ws_url",
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
            help="Optional, adjust pitch of synthesized speech, [-5, 5] default is 0.",
        )
        parser.add_argument(
            "--speed",
            type=float,
            default=1.0,
            help="Optional, adjust speed of synthesized speech, [0, 2] default is 1.",
        )
        parser.add_argument(
            "--volume",
            type=float,
            default=50.0,
            help="Optional, adjust volume of synthesize speech, [0, 100] default is 50.",
        )

        args = parser.parse_args()
        _check_voice(args)
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
