import pymongo

obj = {"author": "Brady Dennis, Sarah Kaplan",
       "title": "Jackson water crisis signals a bigger climate casualty - The Washington Post",
       "description": "This week's water crisis in Jackson, Miss., portends what could happen in other U.S. communities, as climate change pushes under-resourced and overburdened water systems to the brink.",
       "url": "https://www.washingtonpost.com/climate-environment/2022/08/31/jackson-water-crisis-mississippi-floods/",
       "urlToImage": "https://www.washingtonpost.com/wp-apps/imrs.php?src=https://arc-anglerfish-washpost-prod-washpost.s3.amazonaws.com/public/RJX5GVBJK4I63KIK7TSACXP4R4.jpg&w=1440",
       "publishedAt": "2022-09-01T00:29:00Z",
       "content": "Comment on this story\r\nThe water crisis unfolding in Mississippis capital this week has forced schools to shift to virtual learning, led to widespread distribution of bottled water and left Jacksons … [+9255 chars]",
       "source.id": "the-washington-post", "source.name": "The Washington Post",
       "summary": "The water crisis unfolding in Mississippis capital this week has forced schools to shift to virtual learning. The crisis has led to widespread distribution of bottled water and left Jacksons out of water. The water crisis has also led to the closure of Jackson's in the city.",
       "sentiment": "NEGATIVE", "emotion": "sadness"}

client = pymongo.MongoClient(
    "mongodb+srv://lcswgnr:CnO35mX3KP7YRtAq@sent-news.apme119.mongodb.net/?retryWrites=true&w=majority")
db = client['sent-news']
col = db['articles']

col.update_one(obj, {"$set": obj}, upsert=True)




