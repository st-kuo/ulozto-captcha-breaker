import argparse

from ulozto_captcha_breaker.dataset.preprocessing.image_pipeline import ImagePreprocessorPipeline
from ulozto_captcha_breaker.dataset.preprocessing.image_preprocessors import ConvertToGrayscalePreprocessor, NormalizeImagePreprocessor, ResizePreprocessor
from ulozto_captcha_breaker.dataset.preprocessing.label_preprocessors import StringEncoder
import tensorflow as tf

import numpy as np
from PIL import Image


def main(args):
    image = np.asarray(Image.open(args.image_path))
    '''
    image_preprocess_pipeline = ImagePreprocessorPipeline([
        ConvertToGrayscalePreprocessor(),
        NormalizeImagePreprocessor()
    ])
    '''
    # ------------------------------
    # [ST221212] Copy from train.py.
    input_shape = (image.shape[0], image.shape[1])
    image_preprocess_pipeline = ImagePreprocessorPipeline([
        ConvertToGrayscalePreprocessor(),
        ResizePreprocessor(input_shape[0], input_shape[1]),
        NormalizeImagePreprocessor()
    ])
    # ------------------------------
    
    label_decoder = StringEncoder(available_chars=args.available_chars)

    # create interpreter
    interpreter = tf.lite.Interpreter(args.model_path)
    interpreter.allocate_tensors()

    input_ = image_preprocess_pipeline([image])
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    interpreter.set_tensor(input_details[0]['index'], input_)
    interpreter.invoke()

    # predict and get the output
    output = interpreter.get_tensor(output_details[0]['index'])

    print("output from 'interpreter.get_tensor': ", output) # [ST221212] for debug
    output_label = np.argmax(output, axis=2)[0]

    # now get labels
    decoded_label = label_decoder.decode(output_label)
    
    print("Decoded label is the following:")
    print(decoded_label)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_path", default=None, type=str, help="To the input image.")
    parser.add_argument("--model_path", default=None, type=str, help="Path to a pretrained model TF Lite.")
    parser.add_argument("--available_chars", default="abcdefghijklmnopqrstuvwxyz", type=str, help="Characters")
    args = parser.parse_args()
    
    main(args)
