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

1. Login ``https://suite.seasalt.ai/stt/signin`` to get ``APIKEY``.

2. Client sends STT API request with ``language`` and ``APIKEY`` to API server: ``https://suite.seasalt.ai/api/v1/speech/stt_server_url?language=xxxxx``, put ``language`` in query string and ``APIKEY`` in headers. ``language`` currently supports ``en-US`` and ``zh-TW``.

    - CLI example:

    .. code-block:: bash

        curl -H "speech_token: <APIKEY>" https://suite.seasalt.ai/api/v1/speech/stt_server_url?language=zh-TW

    - Python example:

    .. code-block:: Python

        import requests
        headers = {'speech_token': 'ae988bc0-8b70-11ec-a0c3-be6fdf6e6b7e'}
        params = (('language', 'zh-TW'))
        response = requests.get('https://suite.seasalt.ai/api/v1/speech/stt_server_url',
                                headers=headers,
                                params=params)

3. API server returns HTTP 200 with json string including the available STT server's url to the client, like,

.. code-block:: JSON

    {
        "server_url": "wss://<host>:<port>/client/ws/speech"
    }

If something is wrong, API server may return HTTP 404 with a json string including an error message.

4. Client connects to the available STT server by websocket with ``APIKEY``, ``language`` and ``punctuation`` settings, e.g. ``wss://stt-servers.seasalt.ai:5019/client/ws/speech?token=<APIKEY>&language=zh-tw&punctuation=True``

5. STT server verifies ``APIKEY`` on API server, if something wrong, STT server will reply error message and close websocket connection:

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

1. Client sends https POST request to API: ``https://suite.seasalt.ai/api/v1/user/login`` to login and get ``api_token``.

.. code-block:: JSON

    {
        "account_id": <username>,
        "password": <password>
    }

- CLI example:

    .. code-block:: bash

        curl -X 'POST' -d '{"account_id": <username>, "password": <password>}' 'https://suite.seasalt.ai/api/v1/user/login'
        # return example: {"user_id":<username>,"timestamp":"2022-03-17T16:43:40","token":<api_token>,"role_id":2}

[OPTIONAL] Find available voices by sending a GET request to API: https://suite.seasalt.ai/api/v1/speech/tts_options.
Find the voice you want and use, and get the value of ``model`` and ``language`` to insert as ``voice`` and ``language`` respectively in step 2.

- CLI example:

    .. code-block:: bash

        curl -X GET "https://suite.seasalt.ai/api/v1/speech/tts_options" -H "token: <api_token>"
        # return example: [{"model_name":"彤彤","language_name":"國語  (台灣)","service_type":"Text-to-Speech","description":null,"model":"Tongtong","language":"zh-TW","id":2}

2. Client sends https POST request to API: ``https://suite.seasalt.ai/api/v1/speech/text_to_speech`` with ``language``, ``voice`` and ``api_token``.

.. code-block:: JSON

    {
        "language": "zh-TW",
        "voice": "Tongtong"
    }

- CLI example:

    .. code-block:: bash

        curl -X POST "https://suite.seasalt.ai/api/v1/speech/text_to_speech" -H "token: <api_token>" -d '{"language": "zh-TW", "voice": "Tongtong"}'
        # return example: {"token":<speech_service_token>,"server_url":"wss://<host>:<port>","account_id":<username>}

please put ``api_token`` in the Headers and put ``language`` and ``voice`` in the request body.

3. API server returns HTTP 200 with json string including the available TTS server's url and ``speech_service_token`` to Client, like

.. code-block:: JSON

    {
        "account_id": <username>,
        "server_url": "wss://<host>:<port>",
        "token": <speech_service_token>
    }

If something is wrong, API server may return HTTP 404 with a json string including an error message.

4. Using the returned TTS ``server_url`` and ``speech_service_token`` from step 3, Client connects to TTS server as a websocket client.

5. If successfully connected, Client sends json string to TTS server, for example,

.. code-block:: JSON

    {
        "business":
        {
            "language": "zh-TW",
            "voice": "Tongtong",
            "token": <speech_service_token>
        },
        "settings":
        {
            "pitch": 0.0,
            "speed": 1.0,
            "sample_rate": 22050
        },
        "data":
        {
            "text": "text to be synthesized" (must be in utf-8 encoding and base64 encoded),
            "ssml": "False"
        }
    }

.. NOTE::

 - Note 1, “language” could be “zh-TW” or “en-US”.
 - Note 2, “voice” for “zh-TW” can be Tongtong or “Vivian”; “voice” for “en-US” could be “TomHanks”, “ReeseWitherspoon” or “AnneHathaway”.
 - Note 3, ["data"]["ssml"] should be True if ["data"]["text"] is a SSML string, i.e. using SSML tab.
 - Note 4, ["data"]["text"] should be in utf-8 encoding and base64 encoded.
 - Note 5, “pitch” could be a value between -12.0 to 12.0, 0.0 is normal pitch,  needs to convert pitch from a percentage number like `100%` to a decimal like `12.0`. It's a linear conversion, `0%` corresponds to `0.0`, `100%` corresponds to `12.0`, `-100%` corresponds to `-12.0`.
 - Note 6, “speed” could be a value from 0.5 to 2.0, 1.0 is normal speed.

6. After sending the TEXT/SSML string, Client calls ws.recv() to wait for TTS server to send the streaming audio data.

7. TTS server performs synthesis and keeps sending streaming audio data to Client. The format is,

.. code-block:: JSON

    {
        "status": "ok",
        "sid": "seq_id",
        "progress": 5,
        "data":
        {
            "audio": "<base64 encoded raw pcm data>",
            "status": 2
        }
    }

.. NOTE::

 - Note 1, if "status" isn't "ok", then there will be some error messages.
 - Note 2, if ["data"]["status"] is 1, means synthesis is in progress; if ["data"]["status"] is 2, means synthesis is completed.
 - Note 3, "progress" means currently which character it's synthesizing.

8. Client receives audio data frames.

9. After finishing processing all TEXT or SSML string, TTS server closes the websocket connection.