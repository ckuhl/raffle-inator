# Raffle-inator for Advent of Code

Run raffles for private Advent of Code leaderboards based on number of stars achieved.

You only need one to win!

## Features

* Randomly select users based on number of stars gained
* Exclude certain users (i.e. the person running the raffle) for reasons of fairness or meanness
* Code is public so it can be inspected for fairness

## Requirements

* Python 3.12 or compatibility therewith
* Pipenv on your system
* Your cookie for Advent of Code saved in a file in this directory named `session_cookie.txt`
* The ID of the private leaderboard in question (this will be at the end of the URL)

## Usage

```shell
% git clone git@github.com:ckuhl/raffle-inator.git
% cd raffle-inator/
% pipenv install
% pipenv run python main.py \
  --year 2023 \
  --leaderboard-owner 1234567 \
  --excluded-participants ckuhl
```

## Why does it require everything be specified on the CLI?

Because I wrote it for a specific use case.
Please fork it or better yet rewrite it yourself if you want different features.
Not because I want to be a bully but because this is relatively simple code to write.
And so, you can dunk on how much better your project is than this in the `## Features` of your project then.
