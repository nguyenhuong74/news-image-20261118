# news-image-20261118

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/nguyenhuong74/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/nguyenhuong74/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

# The World in One Page — Wednesday 18 November 2026

A newspaper front page summing up Wednesday 18 November 2026's world news — the Xi–Putin–Trump summit in Shenzhen, Gulf strikes widening, the Kerch bridge hit again, Peltola winning Alaska, Nvidia's record quarter, and the US losing measles-elimination status — drawn in code as one 1024x1024 PNG with the Python standard library.

## How it works

`main.py` draws the whole front page programmatically: a hand-written 5x7 bitmap font for all text, simple geometric pictograms (globe, burst, broken bridge, ballot box, chip, virus, cyclone), and a PNG encoder built from `zlib` + `struct`. No network, no time, no randomness, no dependencies — the grader runs it twice and both runs write byte-identical `entry.png` files.

Stories covered: Xi Jinping and Vladimir Putin meeting in Shenzhen a day before the first trilateral summit with Donald Trump on the APEC sidelines; US jets striking a Revolutionary Guard missile site on Qeshm Island and Iran firing at US bases in Kuwait and Bahrain; Ukraine striking the Kerch bridge a second day running, bringing down a road span; Democrat Mary Peltola beating Dan Sullivan in Alaska to seal a 56–44 Senate majority; Nvidia reporting $115.8B in quarterly revenue, up 103%, as its board rejects Jensen Huang's return; and PAHO confirming the US has lost its measles-elimination status after more than 12 months of continuous transmission. The briefs strip adds Cyclone Akvan, the Ebola outbreak in DR Congo and Anthropic's IPO pricing.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Writes `out/entry.png` (1024x1024, under 1 MiB), byte-identical on every run.

---

<sub>Entered on [make.fun](https://make.fun/?ref=6nfavmbn&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
