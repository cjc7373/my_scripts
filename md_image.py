import argparse
import os
import re
from pathlib import Path

SUCCESS = 0
FAILURE = -1

# ROOT_DIR = Path('C:\\Users\\coherence\\OneDrive\\Notes\\')
ROOT_DIR = Path('/home/cjc/OneDrive/Notes')

IMAGE_DIR = ROOT_DIR / 'images'

def init(args):
    IMAGE_DIR.mkdir(exist_ok=True)
    
    dirs = [x for x in ROOT_DIR.iterdir() if x.is_dir() and x.name != '.git']
    search_dirs = dirs.copy()
    mds = []

    # 递归查找所有的 md 文件
    while search_dirs:
        dir = search_dirs.pop()
        childs = [x for x in dir.iterdir() if x.is_dir()]
        search_dirs += childs
        dirs += childs
        for x in dir.iterdir():
            if x.suffix == '.md':
                mds.append(x)

    md_image = re.compile(r'!\[.*\]\((.*)\)')
    
    for md in mds:
        print(f'Dealing with {md}')
        md_dir = md.parent
        filename = md.name
        with open(md, 'r', encoding='utf8') as f:
            content = f.read()  # md 文件通常很小所以直接读入了
        
        images = []
        for i in md_image.findall(content):
            if 'http' in i:  # 排除图床上的图片
                continue
            image = (md_dir / i).resolve() 
            if IMAGE_DIR in image.parents:  # 排除已经在标准路径的图片
                continue
            images.append(image)
        
        if images:
            image_dir = IMAGE_DIR / md.stem
            image_dir.mkdir(exist_ok=True)

            # 替换 md 文件中的所有图片路径
            def replace(match):
                old_image_path = md_dir / Path(match[1])
                new_image_path = image_dir / old_image_path.name
                # alternative text 没有用, 用一个统一的占位符就行
                rep = f'![image]({os.path.relpath(new_image_path, md_dir)})'
                print(f'Replacing {match[0]} with {rep}')
                return rep

            content = md_image.sub(replace, content)
            with open(md, 'w', encoding='utf8') as f:
                f.write(content)

            # 移动图片
            for image in images:
                new_path = image_dir / image.name
                print(f'Moving {image} to {new_path}')
                image.rename(new_path)
    
    def remove_dir(dir):
        try:
            dir.rmdir()
            print(f'Empty dir {dir} removed.')
            return SUCCESS
        except OSError:  # 文件夹不为空
            return FAILURE

    # 删除所有空文件夹
    for dir in dirs:
        while remove_dir(dir) == SUCCESS:
            dir = dir.parent
            remove_dir(dir)

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(description='valid subcommands')

parser_init = subparsers.add_parser(
        'init', 
        help='init the whole directory, i.e. move all image files to \
              root dir\'s `images` folder, and delete empty folders.'
    )
parser_init.set_defaults(func=init)
parser_move = subparsers.add_parser('move', help='move a `.md` file')
parser_move.add_argument('src', help='source file')
parser_move.add_argument('des', help='destination file')
parser_clean = subparsers.add_parser('archive', help='')
parser_clean = subparsers.add_parser('clean', help='archive all images \
                                     to root dir\'s images folder and \
                                     clean unused image references. Note: \
                                     this command assumes all the images\
                                     are in standard positions')

args = parser.parse_args()
args.func(args)
