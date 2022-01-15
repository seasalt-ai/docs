.. _sum_tutorial:

==================================
Summarization API Tutorial
==================================

This tutorial will walk through how to use the Summarization API for meeting analytics.

.. contents:: Table of Contents
    :local:
    :depth: 3

The endpoint for the Summarization API is ``https://seaword.seasalt.ai/summarization``.

Multilingual Support
====================

The Summarization API currently supports four languages, English, Traditional Chinese, Simplified Chinese, and Indonesian. All API calls for each language include a language code in the URL.

The language codes for supported languages are the following:

====================  =====
Language              Code
====================  =====
English               en-XX
Traditional Chinese   zh-TW
Simplified Chinese    zh-CN
Indonesian            id-XX
====================  =====

Callback URLs
=============

The Summarization API uses callback URLs in some of its endpoints. These endpoints can take longer to execute, and the callback URL allows the process to run in the background and return the answer to you when it is finished.

For testing these endpoints, two resources that are available to provide testing URLs as your callback URL are `webhook.site <https://webhook.site/>`_ and `ngrok <https://ngrok.com/>`_.

In this tutorial, we will use a webhook.site URL in the examples.

API Usage
==========

The Summarization API supports two types of transcript summarization, short and long. The short summary method is intended to summarize a single utterance from a transcript, to provide fine-grained summarization of the transcript. The long summary method is intended to summarize the entire transcript in large chunks, to provide an overall summary of the transcript.

POST /short/summarize
---------------------

The short summary model produces a summary of a single turn of a transcript.

This process is called with the following POST request:

.. code-block:: bash

    POST https://seaword.seasalt.ai/summarization/{lang_code}/short/summarize?access_token={api_key}
    
The required request body for inference contains a single turn from a transcript in the following format:

.. code-block:: JSON

   {
        "transcription": "You know, in planning and all kinds of different meetings with the Taiwan team, and I get I got started on the MDA proposal."
    }

A successful response returns the summary of the transcription in the following JSON format.

.. code-block:: JSON

    {
        "summarization": "You know that there are many meetings with the Taiwan team and I get started on the MDA proposal."
    }

.. NOTE:: As summaries of extremely short utterances are not informative, if the utterances is shorter than 5 words, the summarizer will return an empty summary. To avoid going over the model's character limit, the summarizer will also truncate any utterance longer than 700 words.


POST /long/summarize
--------------------

The long summary model produces a summary of the largest possible segment of a transcript. 

This process is called with the following POST request:

.. code-block:: bash

    POST https://seaword.seasalt.ai/summarization/{lang_code}/long/summarize?access_token={api_key}

The required request body for inference contains the entire transcript in the following format, with speakers and utterances in the ``data`` list. The ``url`` element is the callback URL where the final summary will be returned.

.. code-block:: JSON
    
    {
        "url": "https://webhook.site/3c95b604-4243-4d15-b5ce-a79e18dec3e7",
        "data": [
            {
                "speaker": [
                    "Speaker"
                    ],
                "transcription": "Yesterday was pretty smooth day."
            },
            {
                "speaker": [
                    "Speaker"
                    ],
                "transcription": "Many spent the time in the."
            },
            {
                "speaker": [
                    "Speaker"
                    ],
                "transcription": "You know, in planning and all kinds of different meetings with the Taiwan team, and I get I got started on the MDA proposal."
            },
            {
                "speaker": [
                    "Speaker"
                    ],
                "transcription": "Then you chat about a proposal on the Air Force Recruitment Center and today I continue to work on the proposal."
            }
        ]
    }

.. IMPORTANT:: As it takes a comparatively long time to summarize a long segment, this is implemented as a callback. A successful response will return a success message of the process starting, not a summary directly.

The transcript will be automatically segmented into the largest chunks possible under 300 words. The callback function will then start producing summaries. When the summarization is complete, a PUT request will be sent with the generated summary to the callback url provided in the original request body.

The final summaries will appear in the following JSON format:

.. code-block:: JSON

    {
        "summarization": "Yesterday was a busy day for Speaker. He had many meetings with the Taiwan team and he worked on the MDA proposal. Today he continues to work on the proposal."
    }

The long summarization processing time will vary depending on the length of the transcript, as it depends on how many <300 word segments there are in the transcript.
