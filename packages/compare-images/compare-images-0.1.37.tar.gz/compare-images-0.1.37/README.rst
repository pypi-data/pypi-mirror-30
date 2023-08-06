.. image:: https://img.shields.io/badge/language-PHP-.svg
    :target: none
.. image:: https://img.shields.io/pypi/pyversions/compare-images.svg
    :target: https://pypi.org/pypi/compare-images/
.. image:: https://img.shields.io/pypi/v/compare-images.svg
    :target: https://pypi.org/pypi/compare-images

|

Install
```````


.. code:: bash

    `[sudo] pip install compare-images`

Usage
`````


.. code:: bash

    usage: compare-images.php image1 image2


Examples
````````


.. code:: bash

    $ compare-images.php image1.jpg image2.jpg # $? != 0 if not equal
    
    $ compare-images.php image1.jpg image1.jpg # $? == 0, equal 100% :)
