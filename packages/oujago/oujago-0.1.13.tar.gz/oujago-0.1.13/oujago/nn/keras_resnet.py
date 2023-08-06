# -*- coding: utf-8 -*-

import sys
import keras.backend as K
from keras.layers.convolutional import Conv2D
from keras.layers.core import Activation
from keras.layers.core import Dense
from keras.layers.core import Flatten
from keras.layers.merge import add
from keras.layers.normalization import BatchNormalization
from keras.layers.pooling import AveragePooling2D
from keras.layers.pooling import MaxPool2D
from keras.models import Model
from keras.regularizers import l2


ROW_AXIS = 1
COL_AXIS = 2
CHANNEL_AXIS = 3


def _keras_print_shape(layer, name='', verbose=True):
    if not verbose:
        return

    if name != '':
        print('{:>20}'.format(name), end=': ')
    print(K.int_shape(layer))
    sys.stdout.flush()


def handle_dim_order(row_axis, col_axis, channel_axis):
    global ROW_AXIS
    global COL_AXIS
    global CHANNEL_AXIS

    ROW_AXIS = row_axis
    COL_AXIS = col_axis
    CHANNEL_AXIS = channel_axis


def _shortcut(inputs, residual):
    """Adds a shortcut between input and residual block and merges them with "sum". """

    # Expand channels of shortcut to match residual.
    # Stride appropriately to match residual (width, height)
    # Should be int if network architecture is correctly configured.

    input_shape = K.int_shape(inputs)
    residual_shape = K.int_shape(residual)
    stride_width = int(round(input_shape[ROW_AXIS] / residual_shape[ROW_AXIS]))
    stride_height = int(round(input_shape[COL_AXIS] / residual_shape[COL_AXIS]))
    are_channels_equal = input_shape[CHANNEL_AXIS] == residual_shape[CHANNEL_AXIS]

    # 1 X 1 conv if shape is different. Else identity.
    if stride_width > 1 or stride_height > 1 or not are_channels_equal:
        shortcut = Conv2D(filters=residual_shape[CHANNEL_AXIS],
                          kernel_size=(1, 1),
                          strides=(stride_width, stride_height),
                          padding='valid',
                          kernel_initializer='he_normal',
                          kernel_regularizer=l2(1e-4))(inputs)
    else:
        shortcut = inputs
    return add([shortcut, residual])


def _bn_relu_conv(inputs, filters, kernel_size,
                  strides=(1, 1),
                  kernel_initializer='he_normal',
                  padding='same',
                  kernel_regularizer=l2(1e-4)):
    """Helper to build a BN -> relu -> conv block.
    This is an improved scheme proposed in http://arxiv.org/pdf/1603.05027v2.pdf
    """
    norm = BatchNormalization(axis=CHANNEL_AXIS)(inputs)
    relu = Activation('relu')(norm)
    conv = Conv2D(filters,
                  kernel_size=kernel_size,
                  strides=strides,
                  padding=padding,
                  kernel_initializer=kernel_initializer,
                  kernel_regularizer=kernel_regularizer,
                  use_bias=False)(relu)
    return conv


def _conv_bn_relu(inputs, filters, kernel_size,
                  strides=(1, 1),
                  kernel_initializer='he_normal',
                  padding='same',
                  kernel_regularizer=l2(1e-4)):
    """
    Helper to build a conv -> BN -> relu block
    """
    conv = Conv2D(filters,
                  kernel_size=kernel_size,
                  strides=strides,
                  padding=padding,
                  kernel_initializer=kernel_initializer,
                  kernel_regularizer=kernel_regularizer,
                  use_bias=False)(inputs)
    norm = BatchNormalization(axis=CHANNEL_AXIS)(conv)
    relu = Activation('relu')(norm)
    return relu


def _basic_block(inputs, filters, init_strides=(1, 1), is_first_block_of_first_layer=False, verbose=True):
    """
    Basic 3 x 3 convolution blocks for use on resnets with layers <= 34.
    Follows improved proposed scheme in http://arxiv.org/pdf/1603.05027v2.pdf
    """

    if is_first_block_of_first_layer:
        # don't repeat bn->relu since we just did bn->relu->maxpool
        conv = Conv2D(filters,
                      kernel_size=(3, 3),
                      strides=init_strides,
                      padding='same',
                      kernel_initializer='he_normal',
                      kernel_regularizer=l2(1e-4),
                      use_bias=False)(inputs)
        _keras_print_shape(conv, 'Conv2D', verbose)
    else:
        conv = _bn_relu_conv(inputs, filters, (3, 3), init_strides)
        _keras_print_shape(conv, 'Conv-BN-ReLU', verbose)

    residual = _bn_relu_conv(conv, filters, (3, 3))
    _keras_print_shape(residual, 'Conv-BN-ReLU', verbose)

    out = _shortcut(inputs, residual)
    _keras_print_shape(residual, 'shortcut')

    return out


def _bottle_block(inputs, filters, init_strides=(1, 1), is_first_block_of_first_layer=False, verbose=True):
    """
    Bottleneck architecture for > 34 layer resnet.
    Follows improved proposed scheme in http://arxiv.org/pdf/1603.05027v2.pdf
    """

    if is_first_block_of_first_layer:
        # don't repeat bn->relu since we just did bn->relu->maxpool
        conv = Conv2D(filters,
                      kernel_size=(1, 1),
                      strides=init_strides,
                      padding='same',
                      kernel_initializer='he_normal',
                      kernel_regularizer=l2(1e-4),
                      use_bias=False)(inputs)
        _keras_print_shape(conv, 'Conv2D', verbose)
    else:
        conv = _bn_relu_conv(inputs, filters, (1, 1), init_strides)
        _keras_print_shape(conv, 'Conv-BN-ReLU', verbose)

    conv = _bn_relu_conv(conv, filters, (3, 3))
    _keras_print_shape(conv, 'Conv-BN-ReLU', verbose)

    residual = _bn_relu_conv(conv, filters * 4, (1, 1))
    _keras_print_shape(conv, 'Conv-BN-ReLU', verbose)

    out = _shortcut(inputs, residual)
    _keras_print_shape(residual, 'shortcut', verbose)

    return out


def _build(inputs, nb_out, block_fn, repetitions, filters, verbose=True):
    """
    Builds a custom ResNet like architecture.
    Args:
        input_shape: The input shape in the form (nb_channels, nb_rows, nb_cols)
        nb_out: The number of outputs at final softmax layer
        block_fn: The block function to use. This is either `basic_block` or `bottleneck`.
                    The original paper used basic_block for layers < 50
        repetitions: Number of repetitions of various block units.
                    At each block unit, the number of filters are doubled and the input size is halved
        filters: Filter size of each block.
    Returns:
        The keras `Model`.
    """
    if len(K.int_shape(inputs)) != 4:
        raise Exception('Input shape should be a tuple (nb_batch, nb_rows, nb_cols, nb_channels)')

    _keras_print_shape(inputs, 'Inputs', verbose)

    x = _conv_bn_relu(inputs, filters=64, kernel_size=(7, 7), strides=(2, 2))
    _keras_print_shape(x, 'Conv-BN-ReLU', verbose)

    x = MaxPool2D(pool_size=(3, 3), strides=(2, 2), padding='same')(x)
    _keras_print_shape(x, 'MaxPool2D', verbose)

    # blocks
    for i, (nb_filter, repetition) in enumerate(zip(filters, repetitions)):
        is_first_block_of_first_layer = i == 0
        for j in range(repetition):
            if not is_first_block_of_first_layer and j == 0:
                init_strides = (2, 2)
            else:
                init_strides = (1, 1)
            x = block_fn(x, nb_filter, init_strides, is_first_block_of_first_layer and j == 0, verbose)

    # last activation
    x = Activation('relu')(BatchNormalization(axis=CHANNEL_AXIS)(x))

    # Classifier block
    block_shape = K.int_shape(x)
    x = AveragePooling2D((block_shape[ROW_AXIS], block_shape[COL_AXIS]), strides=(1, 1))(x)
    _keras_print_shape(x, 'AveragePool2D', verbose)

    x = Flatten()(x)
    _keras_print_shape(x, 'Flatten', verbose)

    x = Dense(nb_out, kernel_initializer='he_normal', activation='softmax')(x)
    _keras_print_shape(x, 'Dense', verbose)

    model = Model(inputs=inputs, outputs=x)
    return model


def resnet18(inputs, nb_outputs, verbose=True):
    return _build(inputs, nb_outputs, _basic_block, [2, 2, 2, 2], [64, 128, 256, 512], verbose)


def resnet34(inputs, nb_outputs, verbose=True):
    return _build(inputs, nb_outputs, _basic_block, [3, 4, 6, 3], [64, 128, 256, 512], verbose)


def resnet50(inputs, nb_outputs, verbose=True):
    return _build(inputs, nb_outputs, _bottle_block, [3, 4, 6, 3], [64, 128, 256, 512], verbose)


def resnet101(inputs, nb_outputs, verbose=True):
    return _build(inputs, nb_outputs, _bottle_block, [3, 4, 23, 3], [64, 128, 256, 512], verbose)


def resnet152(inputs, nb_outputs, verbose=True):
    return _build(inputs, nb_outputs, _bottle_block, [3, 8, 36, 3], [64, 128, 256, 512], verbose)
