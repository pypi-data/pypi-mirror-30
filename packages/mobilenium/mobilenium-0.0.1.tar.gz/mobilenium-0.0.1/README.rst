Mobilenium: Selenium with steroids
==================================

Mobilenium uses `BrowserMob Proxy <https://github.com/AutomatedTester/browsermob-proxy-py>`_ to give superpowers to Selenium.

Usage
------------

.. code-block:: python

    >>> from mobilenium import mobidriver
    >>> 
    >>> browsermob_path = 'path/to/browsermob-proxy'
    >>> mob = mobidriver.Firefox(browsermob_binary=browsermob_path)
    >>> mob.get('http://python-requests.org')
    301
    >>> mob.response['redirectURL']
    'http://docs.python-requests.org'
    >>> mob.headers['Content-Type']
    'application/json; charset=utf8'
    >>> mob.title
    'Requests: HTTP for Humans \u2014 Requests 2.13.0 documentation'
    >>> mob.find_elements_by_tag_name('strong')[1].text
    'Behold, the power of Requests'

Mobilenium allows you to use Selenium and manipulate HTTP requests and responses, capture HTTP content, and export performance data, without the need for manual labor. It is powered by BrowserMob Proxy.

Installation
------------
 
* First download the latest BrowserMob Proxy release from the releases `page <https://github.com/lightbody/browsermob-proxy/releases>`_.
* git clone https://github.com/rafpyprog/Mobilenium.git
* pip install -r requirements.txt

Contribute
------------
Contributions are welcome! Not familiar with the codebase yet? No problem! There are many ways to contribute to open source projects: reporting bugs, helping with the documentation, spreading the word and of course, adding new features and patches.
