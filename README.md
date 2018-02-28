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

The first is that a card makes a capability claim that no evaluation supports.
Someone writes "reaches state of the art quality on every public benchmark" and
there is no result in the card that measures it. The claim reads well and cites
nothing, or cites an evaluation that does not appear in the results. A reader
skimming the card has no way to tell a backed claim from an unbacked one.

The second is that a card loses a limitation between versions. A model had a
known weakness, the weakness was written down, and in the next revision the
sentence is gone. Nobody announced the removal. The model may still have the
weakness. A plain text diff would show the deletion buried among reworded
sentences and updated numbers, and it is easy to miss.

ModelCardDiff exists for those two failures. It refuses a card that is
incomplete or makes an unbacked claim, and when it compares two versions it
raises a removed limitation and a regressed metric to the top of the report
rather than leaving them in a wall of line changes.

## What the tool checks

The gate runs four checks. A card passes only when all four hold.

1. Every required section named by the schema exists in the card and has a
   non-empty body.
2. Every capability claim cites an evaluation, and every cited evaluation
   appears in the Results section. A claim that cites nothing is an uncited
   claim. A claim that cites an id no result provides is a dangling citation.
3. No claim quotes an exact metric value that no result carries. A claim that
   states a bound, such as "accuracy above 0.90", is a threshold and is not
   required to equal a result. A claim that states an exact value, such as
   "accuracy of 0.99", must match a result value.
4. Every stated limitation is distinct. Two limitations that reduce to the same
   content words after removing stopwords are treated as boilerplate repetition
   rather than two separate limitations.

The diff classifies every change between two versions into exactly one of four
kinds: an added claim, a removed limitation, a metric regression, or an
editorial change. The direction that counts as a regression depends on the
metric. For a rate whose name contains `confusion`, `error`, `loss`, or
`latency`, a rise is a regression. For everything else a fall is a regression.

## Install and run

The tool is pure Python 3.11 with no third party dependencies. You can run it
straight from the source tree by putting `src` on the path.

```
set PYTHONPATH=src
python -m modelcarddiff version
```

On a POSIX shell the first line is `export PYTHONPATH=src` instead. Installing
the package with pip also installs a `modelcarddiff` console script.
