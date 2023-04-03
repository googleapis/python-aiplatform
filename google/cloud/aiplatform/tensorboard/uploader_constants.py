"""Constants shared between TensorBoard command line uploader and SDK uploader"""

from tensorboard.plugins.distribution import (
    metadata as distribution_metadata,
)
from tensorboard.plugins.graph import metadata as graphs_metadata
from tensorboard.plugins.histogram import (
    metadata as histogram_metadata,
)
from tensorboard.plugins.hparams import metadata as hparams_metadata
from tensorboard.plugins.image import metadata as images_metadata
from tensorboard.plugins.scalar import metadata as scalar_metadata
from tensorboard.plugins.text import metadata as text_metadata

ALLOWED_PLUGINS = [
    scalar_metadata.PLUGIN_NAME,
    histogram_metadata.PLUGIN_NAME,
    distribution_metadata.PLUGIN_NAME,
    text_metadata.PLUGIN_NAME,
    hparams_metadata.PLUGIN_NAME,
    images_metadata.PLUGIN_NAME,
    graphs_metadata.PLUGIN_NAME,
]
