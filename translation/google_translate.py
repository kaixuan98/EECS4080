import pandas as pd
import datetime


def translate_text(target, text):
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    import six
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)

    # print(u"Text: {}".format(result["input"]))
    # print(u"Translation: {}".format(result["translatedText"]))
    # print(u"Detected source language: {}".format(result["detectedSourceLanguage"]))

    # return {"input":result["input"] , "translation": result["translatedText"] , "detectedLang": result["detectedSourceLanguage"] }
    translated = result["translatedText"]
    return translated


if __name__ == "__main__":
    df = pd.read_csv('../data_cleaning/extracted_user.csv')
    df = df.dropna()
    translated = []
    for index, row in df.iterrows():
        if row['lang'] != 'en': 
            translated.append(translate_text('en', row['clean_tweet']))
        else: 
            translated.append(row['clean_tweet'])
        with open('log.txt', 'a') as f:
            f.write(f"{datetime.datetime.now()}-> {index}\n")
    df['translated_text'] = translated
    print(df[100000:1000010])
    df.to_csv('translated_data.csv')