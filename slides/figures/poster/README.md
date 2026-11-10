# STePS poster figures

Charts and the vote QR code for the redesigned STePS poster (Google Slides deck, slide 5). The deck inserts them from this branch's raw URLs, so keep the branch until the poster is final.

| File | Shows | Source |
| --- | --- | --- |
| `washout.png` | Places gained by the target, poisoned update then three clean ones, new adapter per update | `docs/CONTINUED-TRAINING.md`, attack catalogue (push by block, isolated) |
| `residue.png` | Share of the push left after one clean update, reused vs new adapters | same table, block 2 over block 1 |
| `rollback.png` | Target's places above clean with the poisoned adapter kept or deleted | rollback timing, mean of bandwagon and clone |
| `dose.png` | Share of each shopper's gap to #1 closed, by poisoned share (`normalised_gain` in `experiment/dose.py`) | dose summaries, edited real histories |
| `*-v2.png` | Second version of the four charts with larger labels, plus `attacks-v2.png` and its larger-text successor `attacks-v3.png`: what each attack does to a purchase history. Push values from the attack catalogue (new adapter per update), detectability from the shill AUCs | `make_figures2.py` |
| `*-v4.png` | The four charts again, with axis lines, tick marks and titles on both axes | `make_figures2.py` |
| `*-v5.png`, `mark.png` | All figures restyled to the Forget-Me-Not canvas (Fredoka, cream, ink outlines, red attack and blue recovery), plus the canvas's flower mark (`mark.svg`) | `make_figures3.py` |
| `qr-vote.png` | QR code for the UVENTS project page | |

Regenerate the charts with `python make_figures.py OUT_DIR` (needs Google Chrome for SVG to PNG).
