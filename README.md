# anti-trending

GitHub Trending, minus the AI wrapper of the week.

Half of GitHub Trending is agentic nonsense now, so it's hard to find the weird and unique repos. This filters them out.

## Usage

```bash
pip install -r requirements.txt
python anti_trending.py
python anti_trending.py --since weekly --save
python anti_trending.py --language rust
```

`--save` writes the results to `results/YYYY-MM-DD-<period>.md`.
