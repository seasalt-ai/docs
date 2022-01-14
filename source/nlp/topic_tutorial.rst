.. _topic_tutorial:

====================================
Topic Extraction API Tutorial
====================================

This tutorial will walk through how to use the Topic Extraction API for meeting analytics.

.. contents:: Table of Contents
    :local:
    :depth: 3

The endpoint for the Topic Extraction API is ``https://seaword.seasalt.ai/topics``.

Multilingual Support
====================

The Topic Extraction API currently supports the following languages: English, Traditional Chinese, Simplified Chinese, Indonesian, Javanese, Malay, Tagalog, and Vietnamese. By default, the Topic Extraction API will extract topics in English.

All API calls for each language include a language code in the URL.

The language codes for supported languages are the following:

====================  =====
Language              Code
====================  =====
English               en-XX
Traditional Chinese   zh-TW
Simplified Chinese    zh-CN
Indonesian            id-XX
Javanese              jv-XX
Malay                 ms-XX
Tagalog               tl-XX
Vietnamese            vi-XX
====================  =====

Callback URLs
=============

The Topic Extraction API uses callback URLs in some of its endpoints. These endpoints can take longer to execute, and the callback URL allows the process to run in the background and return the answer to you when it is finished.

For testing these endpoints, two resources that are available to provide testing URLs as your callback URL are `webhook.site <https://webhook.site/>`_ and `ngrok <https://ngrok.com/>`_.

In this tutorial, we will use a webhook.site URL in the examples.

API Usage
================

The Topic Extraction API supports topic extraction with and without a callback link. The method with a callback link is intended for very long input that will take longer to complete. The method without is intended for short input where timeout is not a concern. 

POST /extract_no_callback
--------------------------

The no-callback process is called with the following POST request:

.. code-block:: bash

    POST https://seaword.seasalt.ai/topics/{lang_code}/extract_no_callback?access_code={api-key}

The required request body for no-callback topic extraction is in the following format:

.. code-block:: JSON

    {
        "data": [
            {
            "transcription": "",
            "summarization": "The COVID-19 pandemic, also known as the coronavirus pandemic, is an ongoing global pandemic of coronavirus disease 2019 (COVID-19) caused by severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2)."
            }
        ]
    }

You can populate either the ``"summarization"`` field or the ``"transcription"`` field. If the ``"transcription"`` field is populated, the topic extraction will use that first.

The reason for using summarization is to ensure well-formedness. Speech-to-text may result in noisy input, so we strive to provide a sanitized input to the Topic Extraction API as much as possible.

To summarize transcriptions, the Summarization API may be used:

:ref:`Summarization Tutorial ---> <sum_tutorial>`

A successful response will have the following output:

.. code-block:: JSON
    
    {
        "topics": [
            {
                "tag_name": "coronavirus pandemic"
            },
            {
                "tag_name": "coronavirus disease 2019"
            },
            {
                "tag_name": "ongoing global pandemic"
            },
            {
                "tag_name": "coronavirus disease"
            }
        ]
    }

POST /extract
--------------

The callback process is called with the following POST request:

.. code-block:: bash

    POST https://seaword.seasalt.ai/topics/{lang_code}/extract?access_code={api-key}

The required request body for topic extraction with callback is in the following format:

.. code-block:: JSON

    {
        "data": [
            {
            "transcription": "",
            "summarization": "The COVID-19 pandemic, also known as the coronavirus pandemic, is an ongoing global pandemic of coronavirus disease 2019 (COVID-19) caused by severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2)."
            }
        ],
        "url": "https://webhook.site/3c95b604-4243-4d15-b5ce-a79e18dec3e7"
    }

The ``url`` field is where callback URL is specified. This URL is used when the API is ready to send its output to the person who submitted a topic extraction request.

A successful response will return the following message:

.. code-block:: bash
    
    {'message': 'Topic extraction process started.'}

The output of topic extraction is sent to the callback URL where you will be able to use it.

When using the ``extract`` endpoint, we do not have to wait for topic extraction results when we send a request. We let the API process the input without having to worry about the request timing out. Once all the data is processed, the API sends its own request to the callback URL that it was given in the original request.

POST /extract_live
-------------------

In cases where we want to get live results and process a transcript piece by piece, we can use the ``/extract_live`` endpoint.
Instead of an entire meeting transcript, this endpoint accepts a single transcription segment in the following format:

.. code-block:: JSON

    {
        "meeting_id": Text,
        "sequence": int,
        "account_id": Text,
        "transcription": Text,
        "callback_url": HttpUrl
    }

The ``"meeting_id"`` uniquely identifies the meeting, while the ``"sequence"`` identifies the segment. The ``"account_id"`` uniquely identifies the SeaMeet account.

The topic extraction process will be performed on the segment and the resulting topics for each segment will be cached.
If the topic extraction system predicts a unique topic for the transcript (ie. it predicts a topic for the first time on a specific meeting transcript),
the API will send a callback containing the new topics in the following format:

.. code-block:: JSON

    {
        "meeting_id": Text,
        "sequence": int,
        "account_id": Text,
        "topics": List[Keywords]
    }
