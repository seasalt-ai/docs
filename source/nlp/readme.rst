.. _nlp_readme:

====================
SeaWord NLP Overview
====================

.. contents:: Table of Contents
    :local:
    :depth: 3

The purpose of this tutorial is to demonstrate how the SeaWord APIs can be used to extract information from text. In this tutorial we will walk-through:
    - How to use the Summarization API to generate short and long summaries from a meeting transcript
    - How to use the Topic Prediction API to predict topics from a meeting transcript
    - How to use the Action Extraction API to extract and summarize actionable items from a meeting transcript
    - How to use the Cross Lingual NER API to extract entities from a given sentence
    - How to use the Machine Reading API to answer questions from a given text

The endpoints of the SeaWord API call for an API key. For these endpoints, please use ``6kx8koGGsGJXfarD``.

Summarization API
=================

The Summarization API uses mBART-50 based summarization models to generate summaries of single turn utterances and full transcripts in multiple languages.

:ref:`Summarization Tutorial ---> <sum_tutorial>`

Topic Prediction API
====================

The Topic Prediction API uses a combination of abstractive and extractive techniques to return a list of relevant topics and keywords from a document.

:ref:`Topic Prediction Tutorial ---> <topic_tutorial>`

Action Extraction API
=====================

The Action Extraction API extracts and summarizes action items from a document. 

:ref:`Action Extraction Tutorial ---> <action_tutorial>`

Cross Lingual NER API
=====================

The Cross Lingual NER API uses one model to extract 30+ common entities from over 100 languages.

:ref:`Cross Lingual NER Tutorial ---> <xlingualNER_tutorial>`

Machine Reading API
===================

The Machine Reading API performs extractive machine reading to answer questions given a context text.

:ref:`Machine Reading Tutorial ---> <mr_tutorial>`