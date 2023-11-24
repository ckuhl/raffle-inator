import dataclasses
import json
import logging
import pathlib
import random
import time

import click
import requests

log = logging.getLogger(__name__)


def _get_cache() -> pathlib.Path:
    """Helper: Get or create local cache directory"""
    cache = pathlib.Path(".cache")
    if not cache.exists():
        cache.mkdir()
    return cache


def get_leaderboard_json(
        year: int,
        leaderboard_owner: int,
) -> dict:
    """Load or fetch (and save) the leaderboard JSON"""
    cached_input = _get_cache() / f"{year}.json"

    # Taken from the Leaderboard page
    rate_limit_seconds = 900

    if cached_input.exists() and cached_input.stat().st_mtime > (
            time.time() - rate_limit_seconds
    ):
        log.info("using cached input")
        return json.loads(cached_input.open().read())

    log.info("querying leaderboard")
    # FIXME: Need to load the session cookie from elsewhere
    session_cookie = open("session_cookie.txt").read().strip()
    leaderboard_url = f"https://adventofcode.com/{year}/leaderboard/private/view/{leaderboard_owner}.json"
    response = requests.get(leaderboard_url, cookies={"session": session_cookie})

    cached_input.open("w").write(json.dumps(response.json()))

    return response.json()


@dataclasses.dataclass
class Participant:
    """Helper: Wrapper around the object returned by the leaderboard API"""

    last_star_ts: int
    global_score: int
    stars: int
    completion_day_level: dict
    local_score: int
    id: int
    name: str


def json_to_participants(
        blob: dict,
        excluded_participants: list[str] | None = None,
) -> list["Participant"]:
    """Convert a JSON response into a list of _allowed_ raffle participants"""
    if not excluded_participants:
        excluded_participants = []
    all_people = [Participant(**x) for x in blob["members"].values()]

    return [x for x in all_people if x.name not in excluded_participants and x.stars]


def raffle(p: list[Participant]):
    """Do the raffle. We sort participants by ID so that this is deterministic between runs."""
    p = sorted(p, key=lambda x: x.id)

    out_of = sum(x.stars for x in p)

    # We save this twice so we can log it once we select a winner
    original_roll = random.randint(1, out_of)
    dice_roll = original_roll

    for participant in p:
        dice_roll -= participant.stars
        if dice_roll <= 0:
            log.info(
                f"Rolled for {original_roll} out of {out_of}, winner: {participant.name}"
            )
            return participant.name


def do_raffle(
        year: int,
        leaderboard_owner: int,
        excluded_participants: list[str] | None = None,
) -> str:
    """Pull the above together!"""
    json_blob = get_leaderboard_json(
        year=year,
        leaderboard_owner=leaderboard_owner,
    )
    participants = json_to_participants(
        json_blob,
        excluded_participants=excluded_participants,
    )
    return raffle(participants)


@click.command()
@click.option("--year", help="Year to run raffle for")
@click.option("--leaderboard-owner", help="Owner of the leaderboard")
@click.option(
    "--excluded-participants",
    default=None,
    help="Comma-separated list of participants to exclude",
)
@click.option("-v", "--verbose", default=False, is_flag=True, help="Log more info")
def cli(
        year: int,
        leaderboard_owner: int,
        excluded_participants: list[str] | None,
        verbose: bool = False,
) -> None:
    """
    Wrapper around the above `do_raffle` function.
    This allows for testability if I can be bothered to write tests in the future.
    """
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    result = do_raffle(
        year=year,
        leaderboard_owner=leaderboard_owner,
        excluded_participants=excluded_participants,
    )
    print(result)


if __name__ == "__main__":
    cli()
