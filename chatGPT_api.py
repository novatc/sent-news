import openai

# Replace with your own API key
openai.api_key = "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"


def analyze_sentiment(article_body):
    openai.api_key = "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"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Analyze the sentiment of the following text: \"{article_body}\". "
               f"Return either Positive, Negative, Critical.",
        max_tokens=10,
        n=1,
        stop=None,
        temperature=0.5,
    )

    sentiment = response.choices[0].text.strip()
    return sentiment


def analyze_emotions(article_body):
    openai.api_key = "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"

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Please assign two of the following emotions (happiness, sadness, anger, fear, surprise, disgust) "
               f"in the following text based on their prevalence: \"{article_body}\". "
               f"Answer with two words starting with a capital letter, no '.' at the end and seperated by a ','.",
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )

    ranked_emotions = response.choices[0].text.strip()
    return ranked_emotions


def summarize_text(article_body, num_sentences=3):
    openai.api_key = "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"

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Please summarize the following text in {num_sentences} sentences: \"{article_body}\"",
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,
    )

    summary = response.choices[0].text.strip()
    return summary
