import json
import requests
from configparser import ConfigParser


class EmojiHandler:
    def __init__(self, use_dataset=0):
        self._text = ""
        self._output = ""
        self._mapping = {}
        self._driver = None
        self._prompt = ('Give a single phrase not containing any emoji to replace this emoji in a tweet: {emoji}\n'
                        'Emoji label for reference: {label} \n'
                        'Also convey a phrase that can be used to replace multiple emojis that convey strong '
                        'sentiment than a singular use\n'
                        'Use only this output format: [replacement text, strong emotion]')
        self._config = ConfigParser()
        self._config.read(["./config/sentiment_analysis.ini"])
        self._dataset = self._config.get("EMOJI", "dataset_path")
        self._mapping_file = self._config.get("EMOJI", "output_path")
        self._chatgpt_api_url = self._config.get("EMOJI", "chatgpt_api_url")
        self._use_dataset = use_dataset
        if self._use_dataset:
            with open(self._dataset) as json_file:
                self._data = json.load(json_file)
        else:
            with open(self._mapping_file) as json_file:
                self._data = json.load(json_file)
            self._mapping = self._data

    def _preprocess_dataset(self):
        for emoji_dict in self._data:
            self._mapping[emoji_dict['emoji']] = {'label': emoji_dict['label']}
            if 'skins' in emoji_dict:
                for skin in emoji_dict['skins']:
                    self._mapping[skin['emoji']] = {'label': skin['label']}

    def _get_context_from_chatgpt(self, emoji=None):
        if emoji:
            data = {'prompt': self._prompt.format(emoji=emoji,
                                                  label=self._mapping[emoji]['label'])}
            response = requests.post(self._chatgpt_api_url, data=data)
            self._mapping[emoji]['sentiment'] = response.json()["output"]["sentiment"]
            self._mapping[emoji]['strong sentiment'] = response.json()["output"]["strong sentiment"]
            print(self._mapping[emoji])
        else:
            for _emoji in self._mapping:
                # if 'context' not in self._mapping[_emoji]:
                data = {'prompt': self._prompt.format(emoji=_emoji,
                                                      label=self._mapping[_emoji]['label'])}
                response = requests.post(self._chatgpt_api_url, data=data)
                self._mapping[emoji]['sentiment'] = response.json()["output"]["sentiment"]
                self._mapping[emoji]['strong sentiment'] = response.json()["output"]["strong sentiment"]
                print(self._mapping[_emoji])

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    @property
    def output(self):
        return self._output

    def create_mapping(self):
        if self._use_dataset:
            self._preprocess_dataset()
        self._get_context_from_chatgpt()
        with open(self._mapping_file, 'w') as json_file:
            json.dump(self._mapping, json_file, ensure_ascii=False, indent=4)

    def _update_mapping(self, emoji):
        self._get_context_from_chatgpt(emoji)
        with open(self._mapping_file, 'w') as json_file:
            json.dump(self._mapping, json_file, ensure_ascii=False, indent=4)

    def replace_emojis(self):
        self._output = self.text
        for s in set(self.text):
            if s in self._mapping:
                if 'context' not in self._mapping[s]:
                    # TODO
                    # self._update_mapping(s)
                    pass
                if self.text.count(s) > 3:
                    replace_txt = f"{self._mapping[s]['strong sentiment']}. "
                else:
                    replace_txt = f"{self._mapping[s]['sentiment']}. "
                self._output = self._output.replace(s, '')
                if replace_txt not in self._output:
                    self._output += replace_txt


if __name__ == "__main__":
    e = EmojiHandler()
    e.text = "Feels good just by looking at tesla stock today🙃🙃🙃🙃😒🙃🙃!!"
    e.replace_emojis()
    print(e.output)
