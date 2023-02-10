.. _nlp_readme:

=======================
SeaWord NLP V1 Overview
=======================

.. toctree::
   :maxdepth: 2
   :glob:
   :titlesonly:
   :caption: SeaWord v1

   mr_tutorial
   xlingualNER_tutorial

.. meta::
    :keywords: tutorial, documentation, NLP, Natural Language Processing
    :description lang=en: Overview of Seasalt.ai's V1 Natural Language Processing APIs.
    :description lang=zh: Seasalt.ai 自然語言處理 API v1 文檔

The purpose of this tutorial is to demonstrate how the SeaWord APIs can be used to extract information from text. In this tutorial we will walk-through:
    - How to use the Summarization API to generate short and long summaries from a meeting transcript
    - How to use the Topic Prediction API to predict topics from a meeting transcript
    - How to use the Action Extraction API to extract and summarize actionable items from a meeting transcript
    - How to use the Cross Lingual NER API to extract entities from a given sentence
    - How to use the Machine Reading API to answer questions from a given text

| These APIs are protected by an access token. Please send an email to info@seasalt.ai to get yours!
| For these endpoints, please use ``access_token={token}`` either in the request webhook or the request header.

Summarization / Topic Prediction / Action Extraction APIs
==========================================================

These APIs have had a big overhaul! Check out the v2 documentation.

:ref:`NLP V2 Documentation ---> <nlp_readme_v2>`

Cross Lingual NER API
=====================

The Cross Lingual NER API uses one model to extract 30+ common entities from over 100 languages.

:ref:`Cross Lingual NER Tutorial ---> <xlingualNER_tutorial>`

Machine Reading API
===================

The Machine Reading API performs extractive machine reading to answer questions given a context text.

:ref:`Machine Reading Tutorial ---> <mr_tutorial>`