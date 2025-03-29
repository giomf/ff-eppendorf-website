#!/usr/bin/env python

import argparse
import os
import shutil
from datetime import datetime
from pathlib import Path
import mimetypes

_TARGET_BASE_PATH: Path = Path('content/de/einsaetze')
_THUMBNAIL_FULL_BASE_PATH: Path = Path('assets/img/einsaetze')
_THUMBNAIL_BASE_PATH: Path = Path('img/einsaetze')

_DATE_INPUT_FORMAT: str = '%Y-%m-%dT%H-%M'

_INDEX_TEMPLATE: str = '''\
---
title:
date: {date}
description:
thumbnail: {thumbnail}
tag: {tag}
resources:{resources}
---
{markdown_content}

{shortcodes}\
'''

_INDEX_TEMPLATE_RESOURCES_SNIPPET = '\n- name: img01\n  src: img/{img_src}'
_INDEX_TEMPLATE_SHORTCODE_SNIPPET = '\n{{< image src="img01" >}}'


def parse_arguments():
    parser = argparse.ArgumentParser(description="Parse arguments for template, name, and year.")
    subparsers = parser.add_subparsers(dest='command', required=True, help="Subcommands")

    remove_parser = subparsers.add_parser('remove', help='Removes a content page')
    remove_parser.add_argument('--year', type=str, required=True, help='The year')
    remove_parser.add_argument('--id', type=str, required=True, help='The content id')

    create_parser = subparsers.add_parser('create', help='Creates a content page')
    create_parser.add_argument('--year', type=str, required=True, help='The year')
    create_parser.add_argument('--id', type=str, required=True, help='The content id')
    create_parser_group = create_parser.add_mutually_exclusive_group(required=True)
    create_parser_group.add_argument('--template', action='store_true')
    create_parser_group.add_argument('--input', type=str)

    print_parser = subparsers.add_parser('print', help='Print the index of a content page')
    print_parser.add_argument('--year', type=str, required=True, help='The year')
    print_parser.add_argument('--id', type=str, required=True, help='The content id')

    args = parser.parse_args()

    return args


def create_base_paths(year: str, index: str):
    content_path = _TARGET_BASE_PATH.joinpath(year).joinpath(index)
    image_path = content_path.joinpath('img')

    if content_path.exists():
        raise FileExistsError(f'{content_path} already exists')

    os.mkdir(content_path)
    os.mkdir(image_path)
    print(f'Created {content_path}')


def print_content(year: str, content_id: str):
    content_path = _TARGET_BASE_PATH.joinpath(year).joinpath(content_id)
    index_file = content_path.joinpath('index.md')
    with open(index_file, 'r') as file:
        content = file.read()
        print(f'{content}')


def remove_content(year: str, content_id: str):
    content_path = _TARGET_BASE_PATH.joinpath(year).joinpath(content_id)
    thumbnail_path = _THUMBNAIL_FULL_BASE_PATH.joinpath(year).joinpath(f'{content_id}.jpg')
    shutil.rmtree(content_path)
    os.remove(thumbnail_path)
    print(f'Removed {content_path}')
    print(f'Removed {thumbnail_path}')


def parse_date_from_path(path: Path) -> datetime:
    date_time: str = path.name.split(' ')[0]
    date_time: datetime = datetime.strptime(date_time, _DATE_INPUT_FORMAT)
    print(f'Parsing date "{date_time}" from "{path.name}"')
    return date_time


def parse_tag_from_path(path: Path) -> str:
    tag = path.name.split(' ')[1]
    print(f'Parsing tag "{tag}" from "{path.name}"')
    return tag


def copy_images(year: str, content_id: str, input_path: Path):
    content_path = _TARGET_BASE_PATH.joinpath(year).joinpath(content_id)
    image_path = content_path.joinpath('img')
    counter = 1

    # Iterate through all files in the directory
    for file_path in sorted(input_path.iterdir()):
        if file_path.is_file():
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type and mime_type == 'image/jpeg':
                if counter == 1:
                    thumbnail_path = _THUMBNAIL_FULL_BASE_PATH.joinpath(year).joinpath(f'{content_id}.jpg')
                    shutil.copy(file_path, thumbnail_path)
                    print(f'Copy Thumbnail {file_path.name} to {thumbnail_path}')

                new_image = image_path.joinpath(f'{year}-{content_id}-{counter:02}.jpg')
                shutil.copy(file_path, new_image)
                print(f'Copy {file_path.name} to {new_image}')
                counter = counter + 1
    if counter == 1:
        raise FileNotFoundError(f'No JPG images found in {input_path}')


def get_images_snippet(year: str, content_id: str) -> (str, str):
    content_path = _TARGET_BASE_PATH.joinpath(year).joinpath(content_id)
    image_path = content_path.joinpath('img')
    index_file = content_path.joinpath('index.md')

    shortcodes = ''
    resources = ''
    for (idx, image_path) in enumerate(sorted(image_path.iterdir())):
        resources = resources + f'\n- name: img{idx+1:02}\n  src: img/{image_path.name}'
        shortcodes = shortcodes + f'\n{{{{< image src="img{idx+1:02}" >}}}}  '

    return (resources, shortcodes)


def find_markdown_content(input_path: Path) -> str:
    """Find and read the content of a markdown file in the given directory."""
    for file_path in input_path.iterdir():
        if file_path.is_file() and file_path.suffix == '.md':
            print(f'Use markdown file: {file_path.name}')
            with open(file_path, 'r') as md_file:
                content = md_file.read()
                return content

    print('No markdown file found.')
    return ''


def create_index_file(year: str,
                      content_id: str,
                      date: datetime,
                      thumbnail: str,
                      tag: str,
                      resources: str,
                      shortcodes: str,
                      markdown_content: str = ''):
    content_path = _TARGET_BASE_PATH.joinpath(year).joinpath(content_id)
    index_file = content_path.joinpath('index.md')

    # Add a newline after markdown content if it exists
    if markdown_content and not markdown_content.endswith('\n'):
        markdown_content += '\n'

    index = _INDEX_TEMPLATE.format(date=date,
                                   tag=tag,
                                   thumbnail=thumbnail,
                                   resources=resources,
                                   shortcodes=shortcodes,
                                   markdown_content=markdown_content)

    with open(index_file, 'w') as file:
        file.write(index)

    print(f'Created index at {index_file}')


if __name__ == "__main__":
    args = parse_arguments()

    if args.command == 'create':
        create_base_paths(args.year, args.id)
        if args.template:
            resources = _INDEX_TEMPLATE_RESOURCES_SNIPPET.format(img_src=f'{args.year}-{args.id}-01.jpg')
            create_index_file(args.year, args.id, '', '', '', resources, _INDEX_TEMPLATE_SHORTCODE_SNIPPET)
        elif args.input:
            input_path = Path(args.input)
            tag = parse_tag_from_path(input_path)
            date = parse_date_from_path(input_path)
            copy_images(args.year, args.id, input_path)
            (resources, shortcodes) = get_images_snippet(args.year, args.id)

            # Find and read markdown content
            markdown_content = find_markdown_content(input_path)

            thumbnail_path = _THUMBNAIL_BASE_PATH.joinpath(args.year).joinpath(f'{args.id}.jpg')
            create_index_file(args.year, args.id, date, str(thumbnail_path), tag, resources, shortcodes,
                              markdown_content)

    elif args.command == 'print':
        print_content(args.year, args.id)

    elif args.command == 'remove':
        remove_content(args.year, args.id)
