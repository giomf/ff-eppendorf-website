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


def get_latest_year() -> str:
    """
    Get the latest year from the content directory.
    
    Returns:
        str: The latest year found in the content directory, or the current year if none found
    """
    years = []
    for path in _TARGET_BASE_PATH.iterdir():
        if path.is_dir() and path.name.isdigit():
            years.append(path.name)

    if not years:
        return str(datetime.now().year)

    return max(years)


def get_next_id(year: str) -> str:
    """
    Get the next available ID for a given year.
    
    Args:
        year (str): The year to check for existing IDs
        
    Returns:
        str: The next available ID formatted as a 4-digit string
    """
    year_path = _TARGET_BASE_PATH.joinpath(year)
    if not year_path.exists():
        return "0000"

    ids = []
    for path in year_path.iterdir():
        if path.is_dir() and path.name.isdigit():
            ids.append(int(path.name))

    if not ids:
        return "0000"

    return f"{max(ids) + 1:04d}"


def parse_arguments():
    """
    Parse command line arguments for the script.
    
    Sets up the argument parser with three subcommands:
    - create: Creates a new content page with either a template or from input
    - remove: Removes an existing content page
    - print: Prints the content of an existing page
    
    Returns:
        argparse.Namespace: The parsed command line arguments
    """
    parser = argparse.ArgumentParser(description="Parse arguments for template, name, and year.")
    subparsers = parser.add_subparsers(dest='command', required=True, help="Subcommands")

    # Get default values for create command
    default_year = get_latest_year()
    default_id = get_next_id(default_year)

    remove_parser = subparsers.add_parser('remove', help='Removes a content page')
    remove_parser.add_argument('--year', type=str, required=True, help='The year')
    remove_parser.add_argument('--id', type=str, required=True, help='The content id')

    create_parser = subparsers.add_parser('create', help='Creates a content page')
    create_parser.add_argument('--year', type=str, default=default_year, help=f'The year (default: {default_year})')
    create_parser.add_argument('--id', type=str, default=default_id, help=f'The content id (default: {default_id})')
    create_parser_group = create_parser.add_mutually_exclusive_group(required=True)
    create_parser_group.add_argument('--template', action='store_true')
    create_parser_group.add_argument('--input', type=str)

    print_parser = subparsers.add_parser('print', help='Print the index of a content page')
    print_parser.add_argument('--year', type=str, required=True, help='The year')
    print_parser.add_argument('--id', type=str, required=True, help='The content id')

    args = parser.parse_args()

    return args


def create_base_paths(year: str, index: str):
    """
    Create the base directory structure for a new content page.
    
    Creates the content directory and an img subdirectory for storing images.
    
    Args:
        year (str): The year for the content
        index (str): The ID for the content
        
    Raises:
        FileExistsError: If the content path already exists
    """
    content_path = _TARGET_BASE_PATH.joinpath(year).joinpath(index)
    image_path = content_path.joinpath('img')

    if content_path.exists():
        raise FileExistsError(f'{content_path} already exists')

    os.mkdir(content_path)
    os.mkdir(image_path)
    print(f'Using year: {year} and id: {index}')
    print(f'Created {content_path}')


def print_content(year: str, content_id: str):
    """
    Print the contents of an index.md file for a specific content page.
    
    Args:
        year (str): The year of the content
        content_id (str): The ID of the content
    """
    content_path = _TARGET_BASE_PATH.joinpath(year).joinpath(content_id)
    index_file = content_path.joinpath('index.md')
    with open(index_file, 'r') as file:
        content = file.read()
        print(f'{content}')


def remove_content(year: str, content_id: str):
    """
    Remove a content page and its associated thumbnail.
    
    Deletes both the content directory and the thumbnail image.
    
    Args:
        year (str): The year of the content to remove
        content_id (str): The ID of the content to remove
    """
    content_path = _TARGET_BASE_PATH.joinpath(year).joinpath(content_id)
    thumbnail_path = _THUMBNAIL_FULL_BASE_PATH.joinpath(year).joinpath(f'{content_id}.jpg')
    shutil.rmtree(content_path)
    os.remove(thumbnail_path)
    print(f'Removed {content_path}')
    print(f'Removed {thumbnail_path}')


def parse_date_from_path(path: Path) -> datetime:
    """
    Extract and parse a date from a directory path name.
    
    Expects the directory name to start with a date in the format defined by _DATE_INPUT_FORMAT.
    
    Args:
        path (Path): The path object containing the date in its name
        
    Returns:
        datetime: The parsed datetime object
    """
    date_time: str = path.name.split(' ')[0]
    date_time: datetime = datetime.strptime(date_time, _DATE_INPUT_FORMAT)
    print(f'Parsing date "{date_time}" from "{path.name}"')
    return date_time


def parse_tag_from_path(path: Path) -> str:
    """
    Extract a tag from a directory path name.
    
    Expects the directory name to have a tag as the second element when split by spaces.
    
    Args:
        path (Path): The path object containing the tag in its name
        
    Returns:
        str: The extracted tag
    """
    tag = path.name.split(' ')[1]
    print(f'Parsing tag "{tag}" from "{path.name}"')
    return tag


def copy_images(year: str, content_id: str, input_path: Path):
    """
    Copy JPEG images from an input directory to the content directory.
    
    The first image found is also copied as a thumbnail.
    All images are renamed according to the pattern: year-contentId-counter.jpg
    Searches recursively through all subdirectories.
    
    Args:
        year (str): The year for the content
        content_id (str): The ID for the content
        input_path (Path): The path to the directory containing source images
        
    Raises:
        FileNotFoundError: If no JPEG images are found in the input directory
    """
    content_path = _TARGET_BASE_PATH.joinpath(year).joinpath(content_id)
    image_path = content_path.joinpath('img')
    counter = 1

    # Get all files recursively
    all_files = []
    for root, _, files in os.walk(input_path):
        for file in files:
            all_files.append(Path(root) / file)

    # Sort files to ensure consistent ordering
    all_files.sort()

    # Process all image files
    for file_path in all_files:
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
    """
    Generate resources and shortcodes snippets for all images in the content directory.
    
    Creates Hugo resource declarations and image shortcodes for each image file.
    
    Args:
        year (str): The year of the content
        content_id (str): The ID of the content
        
    Returns:
        tuple: A tuple containing (resources_string, shortcodes_string)
    """
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
    """
    Find and read the content of a markdown file in the given directory.
    
    Searches for any .md file in the input directory and returns its contents.
    If multiple markdown files exist, only the first one found will be used.
    
    Args:
        input_path (Path): The directory to search for markdown files
        
    Returns:
        str: The content of the markdown file, or an empty string if none found
    """
    for file_path in input_path.iterdir():
        if file_path.is_file() and file_path.suffix == '.md':
            print(f'Use markdown file: {file_path}')
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
    """
    Create an index.md file for a content page using the template.
    
    Formats the provided parameters into the index template and writes it to disk.
    
    Args:
        year (str): The year of the content
        content_id (str): The ID of the content
        date (datetime): The date for the content
        thumbnail (str): Path to the thumbnail image
        tag (str): The tag for the content
        resources (str): The resources section for Hugo
        shortcodes (str): The image shortcodes
        markdown_content (str, optional): Additional markdown content. Defaults to ''.
    """
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
