#----------------------------------------------------------------------------------------------
#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License. See License.txt in the project root for license information.
#----------------------------------------------------------------------------------------------

from __future__ import absolute_import
import argparse
import numpy as np
from six import text_type as _text_type
from tensorflow.contrib.keras.api.keras.preprocessing import image


class TestFCN(object):

    preprocess_func = {
        'caffe' : {
            'voc-fcn8s'     : lambda path : TestKit.Identity(path, 500, True),
        },

    def __init__(self):
        parser = argparse.ArgumentParser()

        parser.add_argument('-p', '--preprocess', type=_text_type, help='Model Preprocess Type')

        parser.add_argument('-n', type=_text_type, default='kit_imagenet',
                            help='Network structure file name.')

        parser.add_argument('-s', type=_text_type, help='Source Framework Type',
                            choices=self.truth.keys())

        parser.add_argument('-w', type=_text_type, required=True,
                            help='Network weights file name')

        parser.add_argument('--image', '-i',
                            type=_text_type, help='Test image path.',
                            default="mmdnn/conversion/examples/data/seagull.jpg"
        )

        parser.add_argument('--dump',
            type=_text_type,
            default=None,
            help='Target model path.')

        self.args = parser.parse_args()
        if self.args.n.endswith('.py'):
            self.args.n = self.args.n[:-3]
        self.MainModel = __import__(self.args.n)


    @staticmethod
    def ZeroCenter(path, size, BGRTranspose=False):
        img = image.load_img(path, target_size = (size, size))
        x = image.img_to_array(img)
        if BGRTranspose == True:
            x = x[..., ::-1]
        x[..., 0] -= 103.939
        x[..., 1] -= 116.779
        x[..., 2] -= 123.68
        return x


    @staticmethod
    def Normalize(path, size=224, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]):
        img = image.load_img(path, target_size=(size, size))
        x = image.img_to_array(img)
        x /= 255.0
        for i in range(0, 3):
            x[..., i] -= mean[i]
            x[..., i] /= std[i]
        return x


    @staticmethod
    def Standard(path, size, BGRTranspose=False):
        img = image.load_img(path, target_size = (size, size))
        x = image.img_to_array(img)
        x /= 255.0
        x -= 0.5
        x *= 2.0
        if BGRTranspose == True:
            x = x[..., ::-1]
        return x


    @staticmethod
    def Identity(path, size, BGRTranspose=False):
        img = image.load_img(path, target_size = (size, size))
        x = image.img_to_array(img)
        if BGRTranspose == True:
            x = x[..., ::-1]
        return x


    def preprocess(self, image_path):
        func = self.preprocess_func[self.args.s][self.args.preprocess]
        return func(image_path)


    def print_result(self, predict):
        predict = np.squeeze(predict)
        top_indices = predict.argsort()[-5:][::-1]
        self.result = [(i, predict[i]) for i in top_indices]
        print (self.result)


    def print_intermediate_result(self, intermediate_output, if_transpose = False):
        intermediate_output = np.squeeze(intermediate_output)

        if if_transpose == True:
            intermediate_output = np.transpose(intermediate_output, [2, 0, 1])

        print (intermediate_output)
        print (intermediate_output.shape)
        print ("%.30f" % np.sum(intermediate_output))


    def test_truth(self):
        this_truth = self.truth[self.args.s][self.args.preprocess]
        for index, i in enumerate(self.result):
            assert this_truth[index][0] == i[0]
            assert np.isclose(this_truth[index][1], i[1], atol = 1e-6)

        print ("Test model [{}] from [{}] passed.".format(
            self.args.preprocess,
            self.args.s
        ))


    def inference(self, image_path):
        self.preprocess(image_path)
        self.print_result()


    def dump(self, path = None):
        raise NotImplementedError()


'''
if __name__=='__main__':
    tester = TestKit()
    tester.inference('examples/data/seagull.jpg')
'''
