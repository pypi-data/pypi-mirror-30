====
asjp
====

A small library of three functions. ``ipa2asjp`` takes an IPA-encoded string
and converts it into an ASJP-encoded one. ``asjp2ipa`` tries to do the
opposite. ``tokenise`` takes an ASJP-encoded string and returns a list of
tokens.

>>> from asjp import ipa2asjp, asjp2ipa, tokenise
>>> ipa2asjp('lit͡sɛ')
'ly~icE'
>>> tokenise(ipa2asjp('lit͡sɛ'))
['ly~', 'i', 'c', 'E']
>>> [ipa2asjp(t) for t in ['l', '', 't͡s', 'ɛ']] == tokenise(ipa2asjp('lit͡sɛ'))
True
>>> asjp2ipa(ipa2asjp('lit͡sɛ')) == lit͡sɛ
True


licence
=======

MIT. Do as you please and praise the snake gods.
