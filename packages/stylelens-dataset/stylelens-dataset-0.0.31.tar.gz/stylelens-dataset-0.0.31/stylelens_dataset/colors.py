from bson.objectid import ObjectId
from stylelens_dataset.database import DataBase

class Colors(DataBase):
  def __init__(self):
    super(Colors, self).__init__()
    self.colors = self.db.colors
    self.products = self.db.products
    self.classes = self.db.color_classes

  def add_color(self, object):
    id = None
    try:
      r = self.colors.update_one({"file": object['file']},
                                  {"$set": object},
                                  upsert=True)
    except Exception as e:
      print(e)

    if 'upserted' in r.raw_result:
      id = str(r.raw_result['upserted'])

    return id

  def get_classes(self, offset=0, limit=100):
    query = {}
    try:
      r = self.classes.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)

    return list(r)

  def get_colors_by_name(self, name,  offset=0, limit=50):
    query = {}
    query['color'] = name

    try:
      r = self.products.find(query).skip(offset).limit(limit)
    except Exception as e:
      print(e)
    return list(r)

