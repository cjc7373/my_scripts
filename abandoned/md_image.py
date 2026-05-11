"""
This script is used to help manage images in markdown files.
It will have the following assumptions:
1. Your md editor will copy the image to the folder where the md file lies in.
2. The standard image path is in your md root directory.
3. Your md file is organized hierarchically.
4. No pictures are from the Internet (i.e. img path can't be url)
"""
import argparse
import os
import re
from pathlib import Path

SUCCESS = 0
FAILURE = -1

# ROOT_DIR = Path('/home/cjc/OneDrive/Notes')
ROOT_DIR = Path('/home/cjc/test/Notes')
IMAGE_DIR = ROOT_DIR / 'images'
md_image = re.compile(r'!\[.*]\((.*)\)')


def search_root_dir(root_dir=ROOT_DIR):
    """递归搜索找出所有文件"""
    dirs = [x for x in root_dir.iterdir() if x.is_dir() and x.name != '.git']
    search_dirs = dirs.copy()
    mds = []
    images = []

    # 递归查找所有的 md 文件
    while search_dirs:
        directory = search_dirs.pop()
        children = [x for x in directory.iterdir() if x.is_dir()]
        search_dirs += children
        dirs += children
        for x in directory.iterdir():
            if x.is_file():
                if x.suffix == '.md':
                    mds.append(x)
                else:
                    images.append(x)

    return mds, images, dirs


def replace_image_reference_in_a_md_file(md, dry_run=False):
    """替换 md 文件中的所有图片路径至标准路径"""
    md_dir = md.parent
    image_dir = IMAGE_DIR / md.stem
    with open(md, 'r', encoding='utf8') as f:
        content = f.read()  # md 文件通常很小所以直接读入了

    def replace(match):
        """
        match[0]: all matched string
        match[1]: image path
        """
        old_image_path = md_dir / Path(match[1])
        new_image_path = image_dir / old_image_path.name
        # alternative text 没有用, 用一个统一的占位符就行
        rep = f'![image]({os.path.relpath(new_image_path, md_dir)})'
        print(f'Replacing {match[0]} with {rep}')
        return rep

    content = md_image.sub(replace, content)
    with open(md, 'w', encoding='utf8') as f:
        if not dry_run:
            f.write(content)


def move_images(md, images, dry_run=False):
    """移动一个 md 文件中的图片至标准路径"""
    if not images:
        return

    image_dir = IMAGE_DIR / md.stem
    print(f'Creating {image_dir}')
    if not dry_run:
        image_dir.mkdir(exist_ok=True)

    # 移动图片
    for image in images:
        new_path = image_dir / image.name
        print(f'Moving {image} to {new_path}')
        if not dry_run:
            image.rename(new_path)


def remove_dir(directory):
    try:
        directory.rmdir()
        print(f'Empty dir {directory} removed.')
        return SUCCESS
    except OSError:  # 文件夹不为空
        return FAILURE


def recursive_remove_empty_dirs(directory, dry_run=False):
    """递归删除一个文件夹和它的父文件夹 (如果它们为空)"""
    if not dry_run:
        while remove_dir(directory) == SUCCESS:
            directory = directory.parent
            remove_dir(directory)


def init(args):
    print(f'Creating {IMAGE_DIR}.')
    if not args.dry_run:
        IMAGE_DIR.mkdir(exist_ok=True)

    mds, _, dirs = search_root_dir()

    # 移动每一个 md 文件里的图片
    for md in mds:
        print(f'Dealing with {md}')
        md_dir = md.parent
        # filename = md.name
        with open(md, 'r', encoding='utf8') as f:
            content = f.read()  # md 文件通常很小所以直接读入了

        images = []
        for i in md_image.findall(content):
            image = (md_dir / i).resolve()
            if IMAGE_DIR in image.parents:  # 排除已经在标准路径的图片
                continue
            images.append(image)

        if images:
            move_images(md, images, args.dry_run)
            replace_image_reference_in_a_md_file(md, args.dry_run)

    # 删除所有空文件夹
    for d in dirs:
        recursive_remove_empty_dirs(d, args.dry_run)

    print('Operation succeeded.')


def clean(args):
    print(args)
    print(args.dry_run)


parser = argparse.ArgumentParser()
parser.add_argument(
    '-d', '--dry-run',
    help='run command without actual action.',
    action='store_true'
)
subparsers = parser.add_subparsers(description='valid subcommands')

parser_init = subparsers.add_parser(
    'init',
    help="""init the whole directory, i.e. move all image files to 
        root folder's `images` folder, and delete empty folders."""
)
parser_init.set_defaults(func=init)
parser_move = subparsers.add_parser('move', help='move a `.md` file')
parser_move.add_argument('src', help='source file')
parser_move.add_argument('des', help='destination file')
parser_archive = subparsers.add_parser('archive', help='')
parser_clean = subparsers.add_parser(
    'clean',
    help="""archive all images to root folder's images folder and 
        clean unused image references. Note: this command assumes all the
        images are in standard positions"""
)
parser_clean.set_defaults(func=clean)

_args = parser.parse_args()
_args.func(_args)
