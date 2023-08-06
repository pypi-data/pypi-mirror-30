import logging
from clarifai.rest import ClarifaiApp, Image, Region, Face, FaceIdentity, Concept, BoundingBox, Model

import unittest


class TestFaceConceptsWorkflow(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    # cls.app = ClarifaiApp(api_key='ee683cf7b7df402dbd2070eee9638163', log_level=logging.WARN)
    # cls.app = ClarifaiApp(api_key='ba2dda308abc40e59c95f5b2545492a9', base_url='api-staging.clarifai.com',
    #                       log_level=logging.WARN)
    cls.app = ClarifaiApp(api_key='f70d8493aaad447786e967d9b6467cbc', base_url='api-dev.clarifai.com',
                          log_level=logging.WARN)

  def test_add_img(self):
    # res = self.app.inputs.search_by_original_url('http://www.trzican.si/wp-content/uploads/2012/10/jansa.jpg')
    # print(res[0].input_id)

    img = self.app.inputs.create_image_from_url(
      url='https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Miroslav_Cerar_small.jpg/1200px-Miroslav_Cerar_small.jpg',
      allow_duplicate_url=True)  # type: Image

    print(type(img))
    print(img)
    print(img.input_id)

    # self.assertTrue(False)

  def test_get_img(self):
    image = self.app.inputs.get('eeae1a63a8884fc3a37fd165afaf3f24')  # type: Image
    for region in image.regions:
      bbox = region.region_info.bbox  # type: BoundingBox
      print('Region ID: %s' % region.region_id)
      print('\tBounding box: %s %s %s %s' % (bbox.top_row, bbox.left_col, bbox.bottom_row, bbox.right_col))

  def test_patch_img(self):
    # prod
    # data = (
    #   ('ba647b24b2ee454997e4cace143737e0', 'cf0a0b49b8174696a10878f294cde9ff', 'jansa'),
    #   ('b652570aaebd4b3fab50bba55c91e930', 'f9ab938ddb91450db7ed02f367eb94b6', 'jansa'),
    #   ('c4d5bf0f4baf404d8bdecdac9a966839', 'd678c7f8ce804bfeabfaf3d39741b2e7', 'jansa'),
    #   ('dfc11aff4faa45ea86af975bce886d6f', 'c56495b81d614863a2455dd5d58ade19', 'jansa'),
    #   ('ac24fae707984f2597e9c25b191a9bc2', 'a842e5ffe828493b80f10313d43c23db', 'pahor'),
    #   ('f32f45e127014ef8aef826fcfd818129', 'ffbda3fbbdcd40bb9ffceacfa5f67ac7', 'pahor'),
    #   ('dcea6071ed034260a8d8e03a122344f5', 'abc765b8bcb141d8a20dad73eb0be40c', 'pahor'),
    #   ('fe9d26e3c57041ee992875008f4bd047', 'e28ff78ff55440c899afe79b586e953f', 'pahor'),
    #   ('f7063c38d39944b9806b8246567ad1e4', 'd7ed6bd17e79480680905574d79ea18f', 'cerar'),
    # )

    # dev
    data = (
      ('f399f185129742939c269718c9747022', 'aac55fc4adc34789ad40f4ced0550913', 'jansa'),
      ('c90681d11b8c4646a374e6407abc50c5', 'd80a12c40ff44962bccbc67134c66ced', 'jansa'),
      ('e611d676e5b041839ba212e9b3651f99', 'd07df3f9d161404a8ae00a6bf56183e7', 'pahor'),
      ('b558224eaf824521beab770a2efb477b', 'b14c343b1aad4ba29b22f2d0ffc89608', 'pahor'),
    )

    data = (('eeae1a63a8884fc3a37fd165afaf3f24', 'b67018cc079c4396a54fa83c75fc12dc', 'cerar'),)

    for d in data:
      image = self.app.inputs.update(Image(
        image_id=d[0],
        regions=[Region(region_id=d[1],
                        face=Face(identity=FaceIdentity(concepts=[Concept(concept_id=d[2])])))]
      ), action='merge')  # type: Image

      print(image)
      print(type(image))

      for region in image.regions:
        bbox = region.region_info.bbox
        print(region.region_id)
        print('\t%s' % bbox.bottom_row)
        for c in region.face.identity.concepts:
          print('concept %s' % c['id'])

  def test_create_model(self):
    model = self.app.models.create('rok6', concepts=['jansa', 'pahor'])  # type: Model
    print(model.model_id)
    print(model.get_concept_ids())

  def test_train_model(self):
    model = self.app.models.get('rok3')  # type: Model
    print(model.output_info)
    # res = model.train()  # type: Model
    # print(res)

  def test_predict(self):
    model = self.app.models.get('rok3')

    # type: dict
    res = model.predict_by_url('https://johnlawspeaks.files.wordpress.com/2014/03/155500_172261_152743_170456_jana.jpg')

    print(res)
    print(type(res))

    for region in res['outputs'][0]['data']['regions']:
      print('Region ID: %s' % region['id'])
      bbox = region['region_info']['bounding_box']
      print('\tBounding box: %s %s %s %s' % (bbox['top_row'], bbox['left_col'], bbox['bottom_row'], bbox['right_col']))
      print('\tRecognized face concepts:')
      for concept in region['data']['face']['identity']['concepts']:
        print('\t\t%s (confidence value: %d)' % (concept['id'], concept['value']))
