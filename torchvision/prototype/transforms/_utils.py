from typing import Any, Optional, Tuple, Union, Type, Iterator

import PIL.Image
import torch
from torchvision.prototype import features
from torchvision.prototype.utils._internal import query_recursively

from .functional._meta import get_dimensions_image_tensor, get_dimensions_image_pil
from torchvision.prototype.transforms.functional import ImageTensorFunc, ImagePILFunc, SegmentationMaskFunc, BoundingBoxFunc
from torchvision.prototype import features


def query_image(sample: Any) -> Union[PIL.Image.Image, torch.Tensor, features.Image]:
    def fn(
        id: Tuple[Any, ...], input: Any
    ) -> Optional[Tuple[Tuple[Any, ...], Union[PIL.Image.Image, torch.Tensor, features.Image]]]:
        if type(input) in {torch.Tensor, features.Image} or isinstance(input, PIL.Image.Image):
            return id, input

        return None

    try:
        return next(query_recursively(fn, sample))[1]
    except StopIteration:
        raise TypeError("No image was found in the sample")


def get_image_dimensions(image: Union[PIL.Image.Image, torch.Tensor, features.Image]) -> Tuple[int, int, int]:
    if isinstance(image, features.Image):
        channels = image.num_channels
        height, width = image.image_size
    elif isinstance(image, torch.Tensor):
        channels, height, width = get_dimensions_image_tensor(image)
    elif isinstance(image, PIL.Image.Image):
        channels, height, width = get_dimensions_image_pil(image)
    else:
        raise TypeError(f"unable to get image dimensions from object of type {type(image).__name__}")
    return channels, height, width


def _extract_types(sample: Any) -> Iterator[Type]:
    return query_recursively(lambda id, input: type(input), sample)


def has_any(sample: Any, *types: Type) -> bool:
    return any(issubclass(type, types) for type in _extract_types(sample))


def has_all(sample: Any, *types: Type) -> bool:
    return not bool(set(types) - set(_extract_types(sample)))


def is_simple_tensor(input: Any) -> bool:
    return isinstance(input, torch.Tensor) and not isinstance(input, features._Feature)


def get_class_func(input):
    if isinstance(input, features.Image):
        return ImageTensorFunc
    elif isinstance(input, features.SegmentationMask):
        return SegmentationMaskFunc
    elif isinstance(input, features.BoundingBox):
        return BoundingBoxFunc
    elif is_simple_tensor(input):
        return ImageTensorFunc
    elif isinstance(input, PIL.Image.Image):
        return ImagePILFunc
    else:
        raise TypeError("The input type is not valid!")


def noops(x):
    return x


def output_new_like(input, output):
    if isinstance(input, features.Image):
        return features.Image.new_like(input, output)
    elif isinstance(input, features.BoundingBox):
        return features.BoundingBox.new_like(input, output)
    elif isinstance(input, features.SegmentationMask):
        return features.SegmentationMask.new_like(input, output)
    else:
        return output
