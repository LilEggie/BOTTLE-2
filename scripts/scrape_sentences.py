import bs4
import json
import requests

import bottle.dir
import bottle.simulators.utils as utils


def parse_string(string: str) -> list:
    result = []
    i = 0

    while i != len(string):
        space_count = 0
        j = i

        for j in range(i, len(string)):
            space_count = space_count + 1 if string[j] == ' ' else 0
            if space_count > 2:
                break

        while j != len(string) and string[j] == ' ':
            j += 1

        result.append(string[i:j].strip())
        i = j

    return result


def get_sentences(string: str) -> list[str]:
    result = []
    data = parse_string(string)
    i = 0

    while i < len(data):
        sentence = data[i]
        num_likes = int(data[i + 1])
        num_dislikes = int(data[i + 2])

        if num_likes >= 30 and num_likes > num_dislikes:
            result.append(sentence)

        i += 3

    return result


def scrape_sentences() -> None:
    filepath = bottle.dir.resources / "wordle" / "nyt" / "word_list.txt"
    word_list = list(utils.extract_words(filepath))
    word_list = sorted(word_list)

    url = "https://sentence.yourdictionary.com/"
    data = {}

    for word in word_list:
        response = requests.get(url + word)

        soup = bs4.BeautifulSoup(response.text, "html.parser")
        result_set = soup.find_all("ul", class_="sentences-list")

        data[word] = []
        for result in result_set:
            s = result.text
            s = s.replace("Advertisement\n", "")
            s = s.replace('\n', '')
            data[word].extend(get_sentences(s))

        if len(data[word]) == 0:
            del data[word]

        print("Completed " + word)

    with open("word_list.json", 'w') as file:
        json.dump(data, file, indent=4)


if __name__ == "__main__":
    scrape_sentences()
