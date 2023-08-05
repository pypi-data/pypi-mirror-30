#!/usr/bin/env python3.6

import argparse

def main():
    parser = argparse.ArgumentParser(description='Android CLI Tools')
    subparsers = parser.add_subparsers(help='Description', dest='sub_command')
    subparsers.required = True

    parser_generate_drawables = subparsers.add_parser('generate-drawables', help='Generate missing bitmap drawables')
    parser_generate_drawables.set_defaults(func=generate_drawables)
    parser_generate_drawables.add_argument('path', help='Path to the project root', nargs='?', default='.')
    
    #parser_rename_drawables = subparsers.add_parser('rename-drawables', help='Rename invalid drawables')

    args = parser.parse_args()
    args.func(args)

def generate_drawables(args):
    import os
    from PIL import Image

    root_dir = args.path
    res_dir = os.path.join(root_dir, 'app', 'src', 'main', 'res')

    print('Generating missing drawables for Android project at {}'.format(root_dir))

    dpis = {
            'mdpi': 1,
            'hdpi': 1.5,
            'xhdpi': 2,
            'xxhdpi': 3,
            'xxxhdpi': 4
    }

    # Dict of filename to the highest dpi variant
    drawables = {}

    for key in dpis:
        drawable_dir = os.path.join(res_dir, 'drawable-{}'.format(key))
        if not os.path.isdir(drawable_dir):
            continue
        for entry in os.listdir(drawable_dir):
            entry_path = os.path.join(drawable_dir, entry)
            if os.path.isfile(entry_path):
                drawables[entry] = key

    for key in drawables:
        high_scale = dpis[drawables[key]]
        high_path = os.path.join(res_dir, 'drawable-{}'.format(drawables[key]), key)
        im = Image.open(high_path)

        for dpi in dpis:
            drawable_dir = os.path.join(res_dir, 'drawable-{}'.format(dpi))
            drawable_path = os.path.join(drawable_dir, key)
 
            if os.path.isfile(drawable_path):
                continue

            os.makedirs(drawable_dir, exist_ok=True)

            target_scale = dpis[dpi]
            scalar = target_scale / high_scale
            
            print('Generating {} at {} scale'.format(drawable_path, scalar))

            scaled = (round(im.width * scalar), round(im.height * scalar))
            im.resize(scaled).save(drawable_path)

if __name__ == '__main__':
    main()
