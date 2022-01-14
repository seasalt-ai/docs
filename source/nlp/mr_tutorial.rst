.. _mr_tutorial:

==================================
Machine Reading API Tutorial
==================================

This tutorial will walk through how to use the Machine Reading API for question answering.

.. contents:: Table of Contents
    :local:
    :depth: 3

Introduction
============
The purpose of the Machine Reading system is to perform extractive question answering given a query and a list of context segments. The result of running the Machine Reader is text span containing the most likely answer and a confidence score.

The endpoint for the Machine Reading API is ``https://seaword.seasalt.ai/machine-reading``.

Multilingual Support
====================

The Machine Reading API currently only supports English.

API Usage
=========

POST /marco-answer
------------
To extract an answer to a given question from a context paragraph, send a POST request to the ``/marco-answer`` endpoint.

.. code-block:: bash

    POST https://seaword.seasalt.ai/machine-reading/marco-answer?access_code={api-key}

The required request body contains a ``question`` and a list of ``context`` segments.

.. code-block:: JSON

    {
        "question": "Where is Seasalt.ai located?",
        "context": 
            [
                "Seasalt.ai is an AI communication solutions start-up located in Seattle, WA.", 
                "Their products include SeaChat, SeaVoice, SeaMeet, and SeaX."
            ]
    }

.. IMPORTANT:: The model used in the Machine Reading system is a cased model trained on case-sensitive data. Therefore it is not necessary to lowercase input text.

.. NOTE:: A context segment cannot exceed 512 characters.

A sucessful response will return an answer, which includes a ``score``, the full ``review`` or context segement that the answer span came from, and the extracted ``answer``:

.. code-block:: JSON

    {
        "answer": "Seattle, WA",
        "review": "Seasalt.ai is an AI communication solutions start-up located in Seattle, WA.",
        "score": 0.9610805511474609
    }
