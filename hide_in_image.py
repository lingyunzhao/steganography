# -*- coding: utf-8 -*-

"""hide_in_image.py: Hide secret in a cover image."""

__author__ = "Lingyun Zhao"

import skimage
import skimage.io
import numpy as np
import sys, argparse, os

def hide(cover, secret, n):

    len_secret = len(secret)
    len_secret_binary = bin(len_secret).replace('0b', '').zfill(32)
    secret_binary = len_secret_binary + ''.join('{0:08b}'.format(ord(x), 'b') for x in secret)

    secret_binary = ''.join('{0:08b}'.format(ord(x), 'b') for x in secret)

    hide_binary(cover, secret_binary, n)

def hide_binary(cover, secret_binary, n):

    h, w, c = cover.shape

    cur = 0
    len_sb = len(secret_binary)
    for i in range(h):
        if cur >= len_sb:
            break
        for j in range(w):
            if cur >= len_sb:
                break
            for k in range(c):
                if cur >= len_sb:
                    break
                if cur + n > len_sb:
                    cover[i, j, k] &= 255 - (2 ** n - 1) + (2 ** (n + cur - len_sb) - 1)
                    cover[i, j, k] |= int(secret_binary[cur:], 2) << (n + cur - len_sb)
                    cur = len_sb
                    break
                cover[i, j, k] &= 255 - (2 ** n - 1)
                cover[i, j, k] |= int(secret_binary[cur:cur+n], 2)
                cur += n

def extract(stego, n):

    secret_binary = extract_binary(stego, n)

    if len(secret_binary) < 32:
        sys.exit(1)

    len_secret = int(secret_binary[:32], 2)
    secret_binary = secret_binary[32:]

    if len_secret * 8 > len(secret_binary):
        sys.exit(1)

    secret_binary = secret_binary[:len_secret*8]

    secret = ''

    for i in range(len_secret):
        secret += chr(int(secret_binary[i*8:(i+1)*8], 2))

    return secret

def extract_binary(stego, n):

    secret_binary = ''

    h, w, c = stego.shape

    for i in range(h):
        for j in range(w):
            for k in range(c):
                secret_binary += bin(stego[i, j, k] & (2 ** n - 1)).replace('0b', '').zfill(n)

    return secret_binary

def main(argv = sys.argv):

    parser = argparse.ArgumentParser(description='Hide secret in a cover image.')
    parser.add_argument('mode', help='Hide or extract.', choices=['hide', 'extract'])
    parser.add_argument('-n', type=int, help='The n least significant bits. 1 <= n <= 8.')
    parser.add_argument('-c', '--cover', help='Cover image. Only used in hide mode.')
    parser.add_argument('-s', '--secret', help='Secret file. Only used in hide mode.')
    parser.add_argument('-g', '--stego', help='Stego file. Only used in extract mode.')
    parser.add_argument('-o', '--output', help='Output file. Stego image should be a png image.')

    args = parser.parse_args()
    if args.mode == 'hide':
        if not args.cover or not args.secret or args.stego or not args.n or args.n < 1 or args.n > 8:
            parser.print_help()
            return 1
        if args.output:
            if args.output[-4:] != ".png":
                parser.print_help()
                return 1
            output = args.output
        else:
            output = os.path.join(os.path.dirname(args.cover), "stego.png")
        cover = skimage.io.imread(args.cover)
        with open(args.secret) as sfile:
            secret = ''.join(sfile.readlines())
            hide(cover, secret, args.n)
            skimage.io.imsave(output, cover)
        return 0

    if args.cover or args.secret or not args.stego or not args.n or args.n < 1 or args.n > 8:
        parser.print_help()
        return 1
    if args.output:
        output = args.output
    else:
        output = os.path.join(os.path.dirname(args.stego), "secret_of_stego.txt")
    stego = skimage.io.imread(args.stego)
    secret = extract(stego, args.n)
    print(secret)
    with open(output, 'w') as sfile:
        sfile.write(secret)
    return 0

if __name__ == '__main__':
    sys.exit(main())
