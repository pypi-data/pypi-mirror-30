====
asjp
====

A library of three functions. ``ipa2asjp`` takes an IPA-encoded sequence and
converts it into an ASJP-encoded sequence. ``asjp2ipa`` tries to do the
opposite. ``tokenise`` takes an ASJP-encoded string and returns a list of
tokens.

>>> from asjp import ipa2asjp, asjp2ipa, tokenise
>>> ipa2asjp('zɛmʲa')
'zEmy~a'
>>> ipa2asjp(['z', 'ɛ', 'mʲ', 'a'])
['z', 'E', 'my~', 'a']
>>> asjp2ipa('zEmy~a')
'zɛmʲa'
>>> tokenise('zEmy~a')
['z', 'E', 'my~', 'a']
>>> ipa2asjp(asjp2ipa(tokenise('zEmy~a'))) == tokenise('zEmy~a')
True
>>> ipa2asjp(['z', 'ɛ', 'mʲ', 'a']) == tokenise(ipa2asjp('zɛmʲa'))
True


what is this?
=============

ASJPcode, more commonly referred to as the ASJP alphabet or simply as ASJP, is
a simplified transcription alphabet introduced in `Brown et al. (2008)`_ and
then slightly modified in `Brown et al. (2013)`_; the latter is considered the
alphabet's spec for the purposes of this package.

The ASJP alphabet is used for transcribing the `ASJP Database`_, an actively
developed database aiming to provide the translations of a set of 40 basic
concepts into all the world's languages. Both alphabet and database are
employed in the field of computational historical linguistics, e.g. in `Jäger
(2013)`_ or `Wichmann et al. (2011)`_.


api
===

``ipa2asjp(ipa_seq)`` takes an IPA string or sequence of string tokens and
converts it into an ASJP string or sequence of string tokens.

``asjp2ipa(asjp_seq)`` takes an ASJP string or sequence of string tokens and
converts it into an IPA string or sequence of string tokens. As ASJP encodes
much less information than IPA, something like
``asjp2ipa(ipa2asjp(ipa_seq)) == ipa_seq`` would rarely hold true.

``tokenise(asjp_string)`` takes an ASJP string and converts it into a list of
ASJP tokens.

``tokenize(asjp_string)`` is an alias for ``tokenise(asjp_string)``.


installation
============

This is a standard Python 3 package with a single dependency, `ipatok`_. It is
offered at the `Cheese Shop`_, so you can install it with pip::

    pip install ipatok

or, alternatively, you can clone this repo (safe to delete afterwards) and do::

    python setup.py test
    python setup.py install

Of course, all of this could, and probably should, be happening within a
virtual environment.


see also
========

- `lingpy`_ is an extensive library for computational historical linguistics
  that includes functions for converting IPA to ASJP.
- `ipatok`_ is a library for tokenising IPA strings used by the ``ipa2asjp``
  function for handling string input.


licence
=======

MIT. Do as you please and praise the snake gods.


.. _`Brown et al. (2008)`: https://doi.org/10.1524/stuf.2008.0026
.. _`Brown et al. (2013)`: https://doi.org/10.1353/lan.2013.0009
.. _`Jäger (2013)`: https://doi.org/10.1163/22105832-13030204
.. _`Wichmann et al. (2011)`: https://doi.org/10.1515/lity.2011.013
.. _`ASJP Database`: http://asjp.clld.org/
.. _`Cheese Shop`: https://pypi.python.org/pypi/asjp
.. _`ipatok`: https://pypi.python.org/pypi/ipatok
.. _`lingpy`: https://pypi.python.org/pypi/lingpy
