import os
import keras
import json
import numpy as np
import scipy
from keras_model_specs import ModelSpec
from keras.preprocessing import image
from keras.applications import mobilenet
import tensorflow as tf


def create_default_custom_objects():
    '''

    Returns: Default custom objects for Keras models supported in keras.applications

    '''
    return {'relu6': mobilenet.relu6, 'DepthwiseConv2D': mobilenet.DepthwiseConv2D, "tf": tf}


def load_multi_model(models_dir, custom_objects=None):
    '''
    Loads multiple models stored in `models_path`.

    Args:
       models_path: a string indicating the directory were models are stored.
       custom_objects: dict mapping class names (or function names) of custom (non-Keras) objects to class/functions.
                    e.g. for mobilenet models: {'relu6': mobilenet.relu6, 'DepthwiseConv2D': mobilenet.DepthwiseConv2D}

    Returns: List of models, list of model_specs

    '''

    models = []
    model_specs = []
    num_models = 0
    model_extensions = ['.h5', '.hdf5']

    for dirpath, dirnames, files in os.walk(models_dir):
        for dir in dirnames:
            files = os.listdir(os.path.join(dirpath, dir))
            for filename in files:
                if filename.endswith(tuple(model_extensions)):
                    print('Loading model ', filename)
                    model, model_spec = load_model(os.path.join(dirpath, dir, filename), custom_objects=custom_objects)
                    models.append(model)
                    model_specs.append(model_spec)
                    num_models += 1

    print('Models loaded: ', num_models)
    return models, model_specs


def load_model(model_path, specs_path=None, custom_objects=None):
    '''

    Args:
        model_dir: Folder containing the model
        specs_path: If specified custom model_specs name, default `model_spec.json`
        custom_objects: dict mapping class names (or function names) of custom (non-Keras) objects to class/functions.
                    e.g. for mobilenet models: {'relu6': mobilenet.relu6, 'DepthwiseConv2D': mobilenet.DepthwiseConv2D}

    Returns: keras model, model_spec object for that model

    '''
    model = keras.models.load_model(model_path, custom_objects)
    if specs_path is None:
        model_name = model_path.split('/')[-1]
        specs_path = model_path.replace(model_name, 'model_spec.json')
    with open(specs_path) as f:
        model_spec_json = json.load(f)
        model_spec = ModelSpec(model_spec_json)
    return model, model_spec


def create_class_dictionary_default(num_classes):
    class_dictionary_default = []
    for i in range(0, num_classes):
        class_dictionary_default.append({'class_name': 'Class_ ' + str(i), 'abbrev': 'C_' + str(i)})
    return class_dictionary_default


def get_class_dictionaries_items(class_dictionaries, key):
    return [class_dict[key] for class_dict in class_dictionaries]


def create_image_generator(data_dir, batch_size, model_spec):
    '''
    Creates a Keras image generator
    Args:
        batch_size: N images per batch
        preprocessing_function: Function to preprocess the images
        target_size: Size of the images

    Returns: Keras generator without shuffling samples and ground truth labels associated with generator

    '''
    test_gen = image.ImageDataGenerator(preprocessing_function=model_spec.preprocess_input)
    print('Input image size: ', model_spec.target_size)
    generator = test_gen.flow_from_directory(data_dir, batch_size=batch_size, target_size=model_spec.target_size[:2],
                                             class_mode='categorical', shuffle=False)

    labels = keras.utils.np_utils.to_categorical(generator.classes, generator.num_classes)

    return generator, labels


def load_preprocess_image(img_path, model_spec):
    """
    Return a preprocessed image (probably to use within a deep neural net).

    Args:
        img_name: a string indicating the name and path of the image.
        preprocess_func: a preprocessing function to apply to the image.
        target_size: size to resize the image to.

    Returns: the preprocessed image.

    """
    return model_spec.load_image(img_path)


def load_preprocess_images(folder_path, model_spec):
    """
    Return an array of preprocessed images.

    Args:
        img_paths: a list of paths to images.
        preprocess_func: a preprocessing function to apply to each image.
        target_size: size the image should be resized to.

    Returns:
        pre_imgs: an array of preprocessed images.

    """
    images = []
    image_paths = []

    for file_path in sorted(os.listdir(folder_path)):
        if file_path.endswith(".png") or file_path.endswith(".jpeg") or file_path.endswith(".jpg"):
            img_path = os.path.join(folder_path, file_path)
            images.append(load_preprocess_image(img_path, model_spec)[0])
            image_paths.append(img_path)

    return images, image_paths


def combine_probabilities(probs, combination_mode=None):
    '''
    Args:
        probs: Probabilities given by the ensemble of models
        combination_mode: combination_mode: 'arithmetic' / 'geometric' / 'harmonic' mean of the predictions or 'maximum'
           probability value

    Returns: Probabilities combined
    '''

    combiners = {
        'arithmetic': np.mean,
        'geometric': scipy.stats.gmean,
        'harmonic': scipy.stats.hmean,
        'maximum': np.amax
    }

    # Probabilities of the ensemble input=[n_models, n_samples, n_classes] --> output=[n_samples, n_classes]

    # Make sure we have a numpy array
    probs = np.array(probs)

    # Join probabilities given by an ensemble of models following combination mode
    if probs.ndim == 3:
        if probs.shape[0] <= 1:
            return probs[0]
        else:
            # Combine ensemble probabilities
            if combination_mode is not None:
                if combination_mode not in combiners.keys():
                    raise ValueError('Error: invalid option for `combination_mode` ' + str(combination_mode))
                else:
                    return combiners[combination_mode](probs, axis=0)
            else:
                raise ValueError('You have multiple models, please enter a valid probability `combination_mode`')
    elif probs.ndim == 2:
        return probs
    else:
        raise ValueError('Incorrect shape for `probs` array, we accept [n_samples, n_classes] or '
                         '[n_models, n_samples, n_classes]')
