<div align="center">

<img src="docs/assets/logo.svg" width="180" alt="ModelCardDiff logo" />

# ModelCardDiff

**Gate and compare model cards against a requirements schema** - check a card for completeness, diff two versions, and fail CI when the story changes.

[![ci](https://github.com/rabbittsui/ModelCardDiff/actions/workflows/ci.yml/badge.svg)](https://github.com/rabbittsui/ModelCardDiff/actions/workflows/ci.yml)
![license](https://img.shields.io/badge/license-MIT-blue)
![python](https://img.shields.io/badge/python-3.11%2B-blue)

</div>

<table align="center">
  <thead>
    <tr>
      <th>Required</th>
      <th>Present in the sample card</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>Overview</td><td>yes</td></tr>
    <tr><td>Intended Use</td><td>yes</td></tr>
    <tr><td>Capabilities</td><td>yes</td></tr>
    <tr><td>Limitations</td><td>yes</td></tr>
    <tr><td>Results</td><td>yes</td></tr>
  </tbody>
</table>

ModelCardDiff gates a model card against a declared requirements schema, and it
compares two versions of a card to classify what changed. It reads a card in a
small structured format, checks that the card is complete and honest, and gives
a clear pass or refuse with reasons. When you have two versions of the same
card it tells you which changes are safe editing and which ones quietly weaken
the record, because a limitation removed without comment is the change most
worth catching.

The table above is not illustrative. It is the result of the real gate run
against `samples/complete.card` using `samples/schema.txt`, reproduced later in
this document with the command and its verbatim output.

## The problem

A model card is a document that describes what a model does, what it should be
used for, and where it falls short. Two things go wrong with model cards over
time, and both are quiet.
