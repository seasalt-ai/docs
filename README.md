
# Seasalt.ai Documentation

Seasalt.ai documentation is written with [Sphinx](http://www.sphinx-doc.org/en/stable/), in RestructuredText syntax.

It is hosted at https://docs.seasalt.ai

## Quick start

1. install Python and [pip](https://pip.pypa.io/en/stable/installing/)
2. install `sphinx`:

        pip install Sphinx

3. install `sphinx_rtd_theme`:

        pip install sphinx_rtd_theme

    Follow the [docs](https://pypi.org/project/sphinx-rtd-theme/) to change your `conf.py`

4. If you start a new project:

        sphinx-quickstart

    When asked "> Separate source and build directories (y/n) [n]: y" Please answer "y" to separate `source` and `build` directories.

    Add `build` to your `.gitignore` file.

5. make static HTML:

        make html

    if using VSCode you can use an extention like Live Server to view the page by right clicking on build/html/index.html and selecting 'Open with Live Server'


6. or if you prefer an auto-refreshing server:

        pip install sphinx-autobuild
        make livehtml

    then the document will be hosted at http://localhost:4002

## Publish

To publish your changes, make a PR to merge changes to `master` branch as usual. When your code is merged to `master` branch, Github Actions for deployment (see `.github/workflows/deploy-github.yml`) will be triggered to rebuild and publish static files to `gh-pages` branch. The webpage, [docs.seasalt.ai](https://docs.seasalt.ai), serves the static files that are pushed to `gh-pages` directly.

## Writing protocols


* Use lots of examples, pictures, and videos
* **images**: use PNG format and center align
* **videos**:
    - if video is long and large, host it on YouTube (ask Xuchen to add you to the Chatflow channel on YouTube; you should already have an invitation in your inbox)
    - if video is short and small (file size < 1MB), you can use the `<video>` tag and host it statically in this repository
    - static video please use `.mp4` format. I used [Handbrake](https://handbrake.fr/) to convert original recorded video to `.mp4` format, with a click on the checkbox "Web Optimized" before converting
* **YouTube videos**:
    - we prefer YouTube videos than vemo because it enables 1.5x/2x play
    - make sure it has good quality: when you first upload the video, it might only show 480p, but *after a while* it'll show 1080p. If it doesn't show 1080p no matter what, it's probably that the screensize isn't a standard format

## Restructured Text Tutorials


http://thomas-cokelaer.info/tutorials/sphinx/rest_syntax.html

http://docutils.sourceforge.net/docs/user/rst/quickref.html
