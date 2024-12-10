import bottle.ansi
import bottle.simulators.wordle as wordle
import bottle.simulators.nyt as nyt


colors = {
    wordle.Hint.GREEN: bottle.ansi.rgb_color(0, 165, 80),
    wordle.Hint.YELLOW: bottle.ansi.rgb_color(255, 196, 12),
    wordle.Hint.GRAY: bottle.ansi.rgb_color(75, 75, 75)
}


def color_tile_string(tile_string: wordle.TileString):
    s = ""
    for tile in tile_string:
        s += colors[tile.hint] + tile.char + bottle.ansi.reset
    return s


def play_nyt():
    __nyt = nyt.NYTWordleSimulator()
    __nyt.ignore_case = True

    while __nyt.has_attempts_left():
        try:
            guess = input("Enter a guess: ").strip()
            __nyt.attempt_guess(guess)
        except wordle.NoAttemptsError as e:
            print(e)
        except nyt.InvalidGuessError as e:
            print(e)

        for tile_string in __nyt.guess_history():
            print(color_tile_string(tile_string))
        print()

    print("You won!" if __nyt.has_guessed_word() else
          f"The word was {__nyt.secret_word}")


if __name__ == "__main__":
    play_nyt()
