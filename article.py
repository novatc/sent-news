#make an article class

class Article():
    def __init__(self, title, author, description,  content):
        self.title = title
        self.author = author
        self.description = description
        self.content = content

    def __str__(self):
        return f"{self.title} by {self.author}"