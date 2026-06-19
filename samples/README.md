# Sample fixtures

These files are hand authored test vectors, not production model cards. They
exist to exercise every branch of the gate and diff logic. The numbers in the
Results sections are invented for the test and are not measurements of any real
model.

## Files

- `schema.txt` requirements schema listing five required sections.
- `complete.card` a card that passes the gate: every required section is
  present and non-empty, every capability claim cites a result that exists, the
  four limitations are distinct, and no claim quotes a metric absent from the
  results.
- `incomplete.card` a card that the gate refuses. It omits the required
  Limitations section, includes one capability claim that cites nothing
  (the 64 megabytes memory claim), and includes one claim that cites
  `eval-sota`, an evaluation that never appears in the Results section.
- `complete-v2.card` a second version of the complete card used for the diff.
  Relative to `complete.card` it adds one capability claim (the escalation
  intent), quietly drops one limitation (the refund and billing confusion
  note), and regresses two metrics (intent accuracy from 0.93 to 0.91, and the
  refund billing confusion rate from 0.11 to 0.14, where a higher confusion
  rate is worse).

## Card format

A card is Markdown with these conventions:

- `## Section Name` starts a section.
- A capability claim is a bullet in the Capabilities section written as
  `- claim: <text> (cites: <eval-id>)`. The `(cites: ...)` suffix is optional;
  a claim without it is an uncited claim.
- A limitation is any bullet in the Limitations section.
- A result is a line in the Results section written as
  `<eval-id> = <metric-name> <value>`.

<!-- draft note 976 -->
