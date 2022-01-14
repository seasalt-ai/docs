.. _action_tutorial:

=====================================
Action Extraction API Tutorial
=====================================

This tutorial will walk through how to use the Action Extraction API for meeting analytics.

.. contents:: Table of Contents
    :local:
    :depth: 3


Introduction
============

The purpose of the Action Extraction system is to create short summaries of action items from meeting transcriptions.
The result of running the Action Extraction over a meeting transcription is a list of commands, suggestions, statements of intent, and other actionable segments that can be presented as to-dos or follow-ups for the meeting participants.

The endpoint for the Action Extraction API is ``https://seaword.seasalt.ai/actions``.


Multilingual Support
====================

The Action Extraction API currently supports three languages, English, Traditional Chinese, and Simplified Chinese. All API calls for each language include a language code in the URL.

The language codes for supported languages are the following:

====================  =====
Language              Code
====================  =====
English               en-XX
Traditional Chinese   zh-TW
Simplified Chinese    zh-CN
====================  =====


Callback URLs
=============

The Action Extraction API uses callback URLs in some of its endpoints. These endpoints can take longer to execute, and the callback URL allows the process to run in the background and return the answer to you when it is finished.

For testing these endpoints, two resources that are available to provide testing URLs as your callback URL are `webhook.site <https://webhook.site/>`_ and `ngrok <https://ngrok.com/>`_.

In this tutorial, we will use a webhook.site URL in the examples.


API Usage
==========

The Action Extraction API supports action extraction with and without a callback link. The method with a callback link is intended for very long input that will take longer to complete. The method without is intended for short input where timeout is not a concern. 

POST /extract_no_callback
--------------------------
The no-callback process is called with the following POST request:

.. code-block:: bash

    POST https://seaword.seasalt.ai/actions/{lang-code}/extract_no_callback??access_code={api-key}

The required request body for no-callback action extraction is in the following format:

.. code-block:: JSON

    {
        "data":[
            {
                "speaker":[
                    "Speaker1"
                ],
                "transcription":"and so I have a plan for today."
            },
            {
                "speaker":[
                    "Speaker2"
                ],
                "transcription":"Resident."
            },
            {
                "speaker":[
                    "Speaker1"
                ],
                "transcription":"We are going to start with LSA at LDA since they started very similarly with the document term matrix"
            },
            {
                "speaker":[
                    "Speaker2"
                ],
                "transcription":"And then I am going to spend the remainder of my time by continued to studying, continuing to study Docker and 1st API."
            }
        ]
    }

A successful response will have the following output:

.. code-block:: JSON

    {
        "action_items":[
            {
                "actionable_segment":"Speaker1: and so I have a plan for today.",
                "transcription_id":0,
                "classification_result":"statement",
                "classification_confidence":0.9999922513961792,
                "summarization_context":"\n\nSpeaker1: and so I have a plan for today.",
                "summary":"Speaker1 has a plan for today.",
                "assigner":null,
                "assignee":null,
                "due_date":null
            },
            {
                "actionable_segment":"Speaker1: We are going to start with LSA at LDA since they started very similarly with the document term matrix",
                "transcription_id":2,
                "classification_result":"statement",
                "classification_confidence":0.999990701675415,
                "summarization_context":"Speaker1: and so I have a plan for today.\nSpeaker2: Resident.\nSpeaker1: We are going to start with LSA at LDA since they started very similarly with the document term matrix",
                "summary":"Speaker1 says the team will start with LSA at LDA.",
                "assigner":null,
                "assignee":null,
                "due_date":null
            },
            {
                "actionable_segment":"Speaker2: And then I am going to spend the remainder of my time by continued to studying, continuing to study Docker and 1st API.",
                "transcription_id":3,
                "classification_result":"statement",
                "classification_confidence":1.0,
                "summarization_context":"Speaker2: Resident.\nSpeaker1: We are going to start with LSA at LDA since they started very similarly with the document term matrix\nSpeaker2: And then I am going to spend the remainder of my time by continued to studying, continuing to study Docker and 1st API.",
                "summary":"Speaker2 will continue to study Docker and 1st API.",
                "assigner":null,
                "assignee":null,
                "due_date":null
            }
        ]
    }


The final action extraction result is the ``summary`` field. The resulting three action items from the example are:
    * "Speaker1 has a plan for today."
    * "Speaker1 says the team will start with LSA at LDA."
    * "Speaker1 will continue to study Docker and 1st API."

In addition to action summary, the action extraction result returns:

* ``actionable_segment``: original transcription that was classified as 'actionable'
* ``transcription_id``: assigned transcript ID
* ``classification_result``: segment label
* ``classification_confidence``: confidence score for segment label
* ``summarization_context``: text used for summarization
* ``assigner``, ``assignee``, and ``due_date``: context info for extracted actions

POST /extract
--------------

Use this API endpoint to extract a list of action items from a long transcription, because analysis may take longer for long transcripts. The callback URL must be specified in the input json body.


The callback process is called with the following POST request:

.. code-block:: bash

    POST https://seaword.seasalt.ai/actions/{lang_code}/extract?access_code={api-key}


The required request body for action extraction with callback is in the following format:

.. code-block:: JSON

    {
        "url":"https://webhook.site/3c95b604-4243-4d15-b5ce-a79e18dec3e7",
        "data":[
            {
                "speaker":[
                    "Speaker1"
                ],
                "transcription":"and so I have a plan for today."
            },
            {
                "speaker":[
                    "Speaker2"
                ],
                "transcription":"Resident."
            },
            {
                "speaker":[
                    "Speaker1"
                ],
                "transcription":"We are going to start with LSA at LDA since they started very similarly with the document term matrix"
            },
            {
                "speaker":[
                    "Speaker2"
                ],
                "transcription":"And then I am going to spend the remainder of my time by continued to studying, continuing to study Docker and 1st API."
            }
        ]
    }

A successful response will return the following message immediately:

.. code-block:: JSON

    {"message": "Action Extraction process started."}

Once the Action Extraction has been performed on the full transcript, a POST request will be sent to the callback URL provided in the json body.
The format of the final result is as follows:

.. code-block:: JSON

    {
        "action_items":[
            {
                "actionable_segment":"Speaker1: and so I have a plan for today.",
                "transcription_id":0,
                "classification_result":"statement",
                "classification_confidence":0.9999922513961792,
                "summarization_context":"\n\nSpeaker1: and so I have a plan for today.",
                "summary":"Speaker1 has a plan for today.",
                "assigner":null,
                "assignee":null,
                "due_date":null
            },
            {
                "actionable_segment":"Speaker1: We are going to start with LSA at LDA since they started very similarly with the document term matrix",
                "transcription_id":2,
                "classification_result":"statement",
                "classification_confidence":0.999990701675415,
                "summarization_context":"Speaker1: and so I have a plan for today.\nSpeaker2: Resident.\nSpeaker1: We are going to start with LSA at LDA since they started very similarly with the document term matrix",
                "summary":"Speaker1 says the team will start with LSA at LDA.",
                "assigner":null,
                "assignee":null,
                "due_date":null
            },
            {
                "actionable_segment":"Speaker2: And then I am going to spend the remainder of my time by continued to studying, continuing to study Docker and 1st API.",
                "transcription_id":3,
                "classification_result":"statement",
                "classification_confidence":1.0,
                "summarization_context":"Speaker2: Resident.\nSpeaker1: We are going to start with LSA at LDA since they started very similarly with the document term matrix\nSpeaker2: And then I am going to spend the remainder of my time by continued to studying, continuing to study Docker and 1st API.",
                "summary":"Speaker2 will continue to study Docker and 1st API.",
                "assigner":null,
                "assignee":null,
                "due_date":null
            }
        ]
    }

The final action extraction result is the ``summary`` field. The resulting three action items from the example are:
    * "Speaker1 has a plan for today."
    * "Speaker1 says the team will start with LSA at LDA."
    * "Speaker1 will continue to study Docker and 1st API."


In addition to action summary, the action extraction result returns:

* ``actionable_segment``: original transcription that was classified as 'actionable'
* ``transcription_id``: assigned transcript ID
* ``classification_result``: segment label
* ``classification_confidence``: confidence score for segment label
* ``summarization_context``: text used for summarization
* ``assigner``, ``assignee``, and ``due_date``: context info for extracted actions


POST /extract_live
-------------------------

In cases where we want to get live results and process a transcript piece by piece, we can use the ``/extract_live`` endpoint.
Instead of an entire meeting transcript, this endpoint accepts a single transcription segment in the following format:

.. code-block:: JSON

    {
        "command": Text,
        "meeting_id": Text,
        "sequence": int,
        "account_id": Text,
        "timestamp": Text,
        "speaker": Text,
        "transcription": Text,
        "voice_start_time": float,
        "voice_duration": float,
        "type": Text,
        "callback_url": HttpUrl
    }

The action extraction process will be performed on the segment. Because the action extraction system uses the previous two segments as context for the
action summarization, the system will automatically cache previous segments from each meeting to assist with summarization.
If the action extraction system predicts an action item for the incoming segment, the API will send a callback containing the new actions in the following format:

.. code-block:: JSON

    {
        "meeting_id": Text,
        "sequence": int,
        "account_id": Text,
        "action_items": List[ActionItem]
    }
