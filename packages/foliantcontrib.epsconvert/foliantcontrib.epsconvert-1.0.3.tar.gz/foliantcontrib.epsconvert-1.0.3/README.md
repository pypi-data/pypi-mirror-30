# EPSConvert

EPSConvert is a tool to convert EPS images into PNG format. This operation applies to any target excluding `pdf`.

## Installation

```bash
$ pip install foliantcontrib.epsconvert
```

## Config

To enable the preprocessor, add `epsconvert` to `preprocessors` section in the project config:

```yaml
preprocessors:
    - epsconvert
```

The preprocessor has a number of options:

```yaml
preprocessors:
    - epsconvert:
        convert_path: convert
        cache_dir: !path .epsconvertcache
        image_width: 0
```

`convert_path`
:   Path to `convert` binary. By default, it is assumed that you have this command in `PATH`. [ImageMagick](https://imagemagick.org/) must be installed.

`cache_dir`
:   Directory to store processed images. They may be reused later.

`image_width`
:   Width of PNG images in pixels. By default (in case when the value is `0`), the width of each image is set by ImageMagick automatically. Default behavior is recommended. If the width is given explicitly, file size may increase.
