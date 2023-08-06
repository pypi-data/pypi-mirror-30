'''
Preprocessor for Foliant documentation authoring tool.
Converts EPS images to PNG format.
'''

import re

from pathlib import Path
from hashlib import md5
from subprocess import run, PIPE, STDOUT, CalledProcessError

from foliant.preprocessors.base import BasePreprocessor


class Preprocessor(BasePreprocessor):
    defaults = {
        'convert_path': 'convert',
        'cache_dir': Path('.epsconvertcache'),
        'image_width': 0,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._source_img_ref_pattern = re.compile("!\[(?P<caption>.*)\]\((?P<path>((?!:\/\/).)+\/[^\/]+\.eps)\)")
        self._cache_path = self.project_path / self.options['cache_dir']
        self._current_dir = self.working_dir

    def _process_epsconvert(self, img_caption: str, img_path: str) -> str:
        img_path_hash = md5(f'{img_path}'.encode())
        img_path_hash.update(f'{self.options["image_width"]}'.encode())

        source_img_path = self._current_dir / img_path
        cached_img_path = self._cache_path / f'{img_path_hash.hexdigest()}.png'
        cached_img_ref = f'![{img_caption}]({cached_img_path.absolute().as_posix()})'

        if cached_img_path.exists():
            return cached_img_ref

        cached_img_path.parent.mkdir(parents=True, exist_ok=True)

        resize_options = ''

        if self.options["image_width"] > 0:
            resize_options = f'-resize {self.options["image_width"]}'

        try:
            command = f'{self.options["convert_path"]} ' \
                      f'{source_img_path.absolute().as_posix()} ' \
                      f'-format png ' \
                      f'{resize_options} ' \
                      f'{cached_img_path.absolute().as_posix()}'

            run(command, shell=True, check=True, stdout=PIPE, stderr=STDOUT)

        except CalledProcessError as exception:
            raise RuntimeError(
                f'Processing of image {img_path} failed: {exception.output.decode()}'
            )

        return cached_img_ref

    def process_epsconvert(self, content: str) -> str:
        def _sub(source_img_ref) -> str:
            return self._process_epsconvert(
                source_img_ref.group('caption'),
                source_img_ref.group('path')
            )

        return self._source_img_ref_pattern.sub(_sub, content)

    def apply(self):
        if self.context["target"] != 'pdf':
            for markdown_file_path in self.working_dir.rglob('*.md'):
                with open(markdown_file_path, encoding='utf8') as markdown_file:
                    content = markdown_file.read()

                with open(markdown_file_path, 'w', encoding='utf8') as markdown_file:
                    self._current_dir = markdown_file_path.parent
                    markdown_file.write(self.process_epsconvert(content))
