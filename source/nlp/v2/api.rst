.. _nlp_api_v2:

==================================
SeaWord NLP v2 API Tutorial
==================================

.. meta::
    :keywords: tutorial, documentation, NLP, Natural Language Processing, API
    :description lang=en: Documentation on how to use Seasalt.ai's natural language processing APIs.
    :description lang=zh: Seasalt.ai 自然語言處理 API 文檔

This tutorial will walk through how to use the Natural Language Processing API for meeting analytics.

.. contents:: Table of Contents
    :local:
    :depth: 3


Introduction
============

In the SeaWord v1 API, each NLP service had its own API server.
That means if you wanted to get the actions, topics, and summary for a meeting, you'd have to submit 3 separate API requests and handle 3 separate callbacks.
In our new version of the API, we have combined all of our meeting analytics services into a single easy-to-use API endpoint.

The new API is hosted at ``https://seaword.seasalt.ai/nlp``, and provides access to the following NLP services:

Action Extraction
-----------------
The purpose of the Action Extraction system is to create a short list of action items from meeting transcriptions.
The result of running the Action Extraction over a meeting transcription is a list of commands, suggestions, statements of intent, and other actionable segments that can be presented as to-dos or follow-ups for the meeting participants.

Topic Extraction
----------------
The Topic Extraction system finds the most salient topics in a body of text and returns those as a list of words or short phrases.

Summarization
-------------
The summarization system accepts both short segments and long bodies of text and returns a summarized version.
Summarization of short segments is useful to normalize and consolidate output from speech-to-text systems.
Long summary can capture the broad strokes of long meetings and consolidate the main points of the conversation to a few short paragraphs.

Emotion
-------
The emotion system analyzes audio data and predicts what emotion (such as happy, angry, sad, etc.) the speaker is expressing.

Sentiment
---------
The sentiment analysis system performs a similar role to the emotion system, but focuses on the text data instead of audio.
It predicts whether each utterance has positive, negative, or neutral sentiment.

Multilingual Support
====================

Each NLP service has support for different languages.
See the table below for information about which languages are supported by each service.
If a request is submitted to a service that does not support the requested language, a warning will be returned with the callback result along with any successful results from other services.

=================== =====   ======= ======  =============   ======= =========
Language            Code    Actions Topics  Summarization   Emotion Sentiment
=================== =====   ======= ======  =============   ======= =========
English             en-XX   ✔️      ✔️      ✔️              ✔️      ✔️
Traditional Chinese zh-TW   ✔️      ✔️      ✔️              ✔️      ❌
Simplified Chinese  zh-CN   ✔️      ✔️      ✔️              ✔️      ❌
Indonesian          id-XX   ❌      ❌      ✔️              ✔️      ❌
=================== =====   ======= ======  =============   ======= =========

NOTE: The emotion service is language independent, and can therefore be used with audio containing any spoken language.


Callback URLs
=============

The SeaWord API uses callback URLs in some of its endpoints.
These endpoints can take longer to execute, and the callback URL allows the process to run in the background and return the answer to you when it is finished.

For testing these endpoints, two resources that are available to provide testing URLs as your callback URL are `webhook.site <https://webhook.site/>`_ and `ngrok <https://ngrok.com/>`_.

In this tutorial, we will use a webhook.site URL in the examples.


API Usage
==========

POST /v2/process/meeting
--------------------------

.. code-block:: bash

    POST https://seaword.seasalt.ai/nlp/v2/process/meeting?access_token={api_key}&is_live={bool}

The required request body for processing a meeting transcription is in the following format:

.. code-block:: JSON

    {
        "meeting_id": "unique-meeting-id-1289342938",
        "language": "en-XX",
        "nlp_processes": [
            "ACTIONS",
            "TOPICS",
            "SHORT_SUMMARY",
            "LONG_SUMMARY",
            "EMOTION",
            "SENTIMENT"
        ]
        "segments":[
            {
                "transcription_id": "unique-transcription-id-1234",
                "transcription":"I had a great time this weekend camping in Yellowstone and I'm going to process the photos and share them on Friday!",
                "speaker":[
                    "Speaker1"
                ],
                "audio": "base64-encoded-string-or-filepath"
            }
        ],
        "callback_url": "https://your-domain.com/callback/endpoint"
    }


If the meeting is in progress, and you want live results for each transcription, set the query parameter `is_live` to `True`.
Some of the NLP services perform significantly better when they have more context, so it's important to let the endpoint know that a meeting is live.
For example, topic extraction will not return salient topics for the entire meeting if it is asked to predict topics for one segment at a time.
To solve this, we cache some of the meeting segments as they come in and then do the processing for certain NLP services in batches.

The endpoint will only perform processing for the services specified in the `nlp_processes` field.
Once the processing is complete for *all* the tasks, the API will send a callback POST request to the URL specified in the `callback_url` field.

Each NLP service may or may not require different fields from the meeting transcription.
The following table shows which NLP processes require which fields:

=================   ======= ======  =============   ======= =========
NLP Process         Actions Topics  Summarization   Emotion Sentiment
=================   ======= ======  =============   ======= =========
meeting_id          ✔️      ✔️      ✔️              ✔️      ✔️
language            ✔️      ✔️      ✔️              ❌      ✔️
transcription_id    ✔️      ❌      ✔️️              ✔️      ✔️
transcription       ✔️      ✔️      ✔️              ❌      ✔️
speaker             ✔️      ❌      ✔️              ❌      ❌
audio               ❌      ❌      ❌              ✔️      ❌
callback_url        ✔️      ✔️      ✔️              ✔️      ✔️
=================   ======= ======  =============   ======= =========

When in doubt, it is best to include all the information available.

Upon submitting the POST request to the API, you should immediately receive the following response with a `202 SUBMITTED` response code:

.. code-block:: JSON

    {"message": f"NLP processing started on meeting {meeting_id}."}

Once the NLP processing is completed (this make take several minutes depending on the size of the transcription), your callback endpoint will recieve a POST request with the following message body:

.. code-block:: JSON

    {
        "meeting_id": "unique-meeting-id-1289342938",
        "language": "en-XX",
        "nlp_processes": [
            "ACTIONS",
            "TOPICS",
            "SHORT_SUMMARY",
            "LONG_SUMMARY",
            "EMOTION",
            "SENTIMENT"
        ]
        "segments":[
            {
                "transcription_id": "unique-transcription-id-1234",
                "transcription":"I had a great time this weekend camping in Yellowstone and I'm going to process the photos and share them on Friday!",
                "speaker":[
                    "Speaker1"
                ],
                "action_items": [
                    {
                        "actionable_segment": "I had a great time this weekend camping in Yellowstone and I'm going to process the photos and share them on Friday!",
                        "action_item": "I'm going to process the photos and share them on Friday!"
                    }
                ],
                "short_summary": "Speaker1 is planning on processing her photos from Yellowstone this weekend.",
                "emotion": "happy",
                "sentiment": "positive"
            }
        ],
        "topics": [
            "camping",
            "Yellowstone",
            "this weekend"
        ],
        "long_summary": "The team shares what they did over the weekend and Speaker1 went to Yellowstone.",
        "errors": []
    }

Each service will append its results to each individual segment and/or the top-level meeting.
For example, the summarization service performs a short summary on each individual utterance as well as a long summary on the entire meeting transcription.
If any errors occur during the processing, the error message will be appended to the `errors` field, but any successful results will still try to be returned as normal.

