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

```
pip install .
modelcarddiff version
```

## The card format

A card is Markdown with a small set of conventions. The parser lives in
`src/modelcarddiff/card.py`.

- `# Title` on the first heading line is the card title.
- `## Section Name` starts a section. Its body is every line until the next
  `##` heading.
- A capability claim is a bullet in the Capabilities section written as
  `- claim: <text> (cites: <eval-id>)`. The `(cites: <eval-id>)` suffix is
  optional. A claim without it is an uncited claim.
- A limitation is any bullet in the Limitations section.
- A result is a line in the Results section written as
  `<eval-id> = <metric-name> <value>`. The value is read as a number when it
  parses as one, otherwise it is kept as text.

Here is the Capabilities and Results section of `samples/complete.card`, which
shows a claim citing a result that exists.

```
## Capabilities

- claim: Classifies the eight supported intents with accuracy above 0.90 on the held out split. (cites: eval-intent-accuracy)

## Results

eval-intent-accuracy = accuracy 0.93
```

## The schema format

A schema is a list of directives, one per line, parsed by
`src/modelcarddiff/schema.py`. Blank lines and lines beginning with `#` are
ignored.

```
require Overview
require Intended Use
require Capabilities
require Limitations
require Results
```

Each `require` names a section that must exist and be non-empty. Section names
are matched case insensitively. A duplicate `require` is collapsed, so listing
a section twice does not report it twice.

## Commands

The command line interface is argparse based, defined in
`src/modelcarddiff/cli.py`. There are four subcommands.

| Command | Arguments | Purpose |
| --- | --- | --- |
| `gate` | `<schema> <card>` | Check a card against a schema and pass or refuse. |
| `diff` | `<old> <new>` | Compare two card versions and classify each change. |
| `claims` | `<card>` | Show which evaluation each capability claim cites. |
| `version` | none | Print the package version. |

## Worked example: gating the sample cards

The complete card satisfies every check. This is the run that fills the table
at the top of this document.

```
python -m modelcarddiff gate samples/schema.txt samples/complete.card
```

```
PASS complete.card: all checks satisfied
```

The incomplete card is authored to fail three ways at once: it omits the
required Limitations section, it makes a memory claim that cites nothing, and it
makes a benchmark claim that cites an evaluation the results never define.

```
python -m modelcarddiff gate samples/schema.txt samples/incomplete.card
```

```
REFUSE incomplete.card: 3 finding(s)
  [missing-section] required section 'Limitations' is missing
  [uncited-claim] (line 16) claim cites no evaluation: Runs comfortably within 64 megabytes of memory on the target device.
  [dangling-citation] (line 17) claim cites 'eval-sota' which is not in results: Reaches state of the art quality on every public benchmark.
```

## Worked example: diffing two versions

The second version of the complete card adds a claim, drops a limitation, and
regresses two metrics. The diff separates the change that matters from the
change that does not.

```
python -m modelcarddiff diff samples/complete.card samples/complete-v2.card
```

```
diff complete.card -> complete-v2.card: 5 change(s)
  [added claim] Supports a new escalation intent bringing the total to nine classes.
  [removed limitation] The refund and billing classes share vocabulary and are confused more often than other pairs.
  [metric regression] eval-intent-accuracy accuracy fell from 0.93 to 0.91
  [metric regression] eval-refund-billing-confusion confusion_rate rose from 0.11 to 0.14
  [editorial] result added: eval-escalation-recall recall 0.82
```

```
summary: 1 added claim, 1 removed limitation, 2 metric regression, 1 editorial
```

The removed limitation is the refund and billing confusion note. Nothing in the
prose announced its removal. The two regressions move in opposite numeric
directions, accuracy down and confusion rate up, and the tool reports both as
regressions because it knows a higher confusion rate is worse.

The `claims` command shows the citation state of each claim on its own. Here it
is on the incomplete card.

```
python -m modelcarddiff claims samples/incomplete.card
```

```
claims for incomplete.card: 3
  CITES    eval-intent-accuracy         Classifies the eight supported intents with accuracy above 0.88 on the held out split.
  UNCITED  -                            Runs comfortably within 64 megabytes of memory on the target device.
  DANGLING eval-sota                    Reaches state of the art quality on every public benchmark.
summary: 1 resolved, 1 uncited, 1 dangling
```

## Reading the reports

Each finding and each change should trigger a specific action.

| Finding or change | What it means | What to do |
| --- | --- | --- |
| `missing-section` | A required section is absent. | Add the section with real content. |
| `empty-section` | A required section exists but has no body. | Write the section or remove the requirement. |
| `uncited-claim` | A capability claim cites no evaluation. | Add a citation to a result, or soften the claim. |
| `dangling-citation` | A claim cites an id no result defines. | Add the missing result, or fix the id. |
| `unmatched-metric` | A claim quotes an exact value no result carries. | Correct the number or the result. |
| `duplicate-limitation` | Two limitations say the same thing. | Merge them or write a distinct second limitation. |
| added claim | A new capability was asserted. | Confirm it is backed before shipping. |
| removed limitation | A known weakness was dropped. | Confirm the weakness is genuinely gone. |
| metric regression | A result moved in the worse direction. | Decide whether the regression is acceptable. |
| editorial | Wording or a non-regressing value changed. | Read for accuracy, no gate action needed. |

## Output format, field by field

The gate report is line oriented so it diffs cleanly in git.

| Line | Fields | Meaning |
| --- | --- | --- |
| header | `PASS <card>: ...` or `REFUSE <card>: <n> finding(s)` | Overall result and finding count. |
| finding | `  [<code>] (line <n>) <message>` | One finding, indented, with its code and source line when known. |

The diff report has a header, one line per change, and a summary.

| Line | Fields | Meaning |
| --- | --- | --- |
| header | `diff <old> -> <new>: <n> change(s)` | The two versions and the change count. |
| change | `  [<label>] <detail>` | One classified change. |
| summary | `summary: <a> added claim, <b> removed limitation, ...` | Counts by kind. |

The claims report has a header, one line per claim, and a summary.

| Line | Fields | Meaning |
| --- | --- | --- |
| header | `claims for <card>: <n>` | The card and its claim count. |
| claim | `  <STATUS> <target> <text>` | Status is CITES, UNCITED, or DANGLING. |
| summary | `summary: <a> resolved, <b> uncited, <c> dangling` | Counts by status. |

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Clean. The gate passed, or the diff found no regression. |
| 1 | Findings present. The gate refused, or the diff found a regression. |
| 2 | Usage error, including a malformed schema. |

The diff exits 1 only on a metric regression, not on a removed limitation. A
removed limitation is always shown and always worth reading, but the numeric
gate for continuous integration is the regression. If you want to fail a build
on a dropped limitation as well, grep the output for `removed limitation`.

<img src="docs/assets/logo.svg" alt="ModelCardDiff wordmark, modelcard in dark ink and diff in green" width="240" />

## Limitations

The tool is deliberately small, and it does not do several things.

- It does not judge whether a claim is true, only whether it cites an
  evaluation that exists. A card can cite a result that is itself wrong, and the
  gate will pass it.
- It does not read the value of a bound. A claim of "accuracy above 0.90" passes
  whether the cited result is 0.93 or 0.05. The bound is treated as prose, not
  compared against the number.
- The distinctness check compares content words after removing a fixed stopword
  list. Two limitations that describe genuinely different problems using the
  same vocabulary could be flagged, and two that use different words for the
  same idea could be missed. It catches lightly reworded boilerplate, not
  semantic paraphrase.
- The regression direction is decided by a fixed list of metric name fragments.
  A metric whose name does not contain one of those fragments is assumed to be
  better when higher. A metric where lower is better but whose name is unusual
  will be misclassified.
- The card format is a small convention, not a standard. It does not read the
  richer schemas used by hosted model card tools, and it does not emit them.
- Multi-line claim and limitation bullets are read only up to the first physical
  line. A bullet whose text wraps onto a second line loses the continuation.

These limits are the cost of a tool that runs offline in a few milliseconds with
no dependencies. The checks it does run, it runs deterministically.

## The claim citation diagram

