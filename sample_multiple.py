import os
import cv2
import time
import random
import numpy as np
from PIL import Image
from pathlib import Path

from glob import glob

import torch
import torchvision.transforms as transforms
from accelerate.utils import set_seed

from src import (FontDiffuserDPMPipeline,
                 FontDiffuserModelDPM,
                 build_ddpm_scheduler,
                 build_unet,
                 build_content_encoder,
                 build_style_encoder)
from utils import (ttf2im,
                   load_ttf,
                   is_char_in_font,
                   save_args_to_yaml,
                   save_single_image,
                   save_image_with_content_style)

from sample import arg_parse
from sample import load_fontdiffuer_pipeline

def image_process(args, content_character, style_image_path=None):

    assert content_character is not None, "The content_character should not be None."
    assert is_char_in_font(font_path=args.ttf_path, char=content_character), f"{content_character} not found in {args.ttf_path}"

    font = load_ttf(ttf_path=args.ttf_path)
    content_image = ttf2im(font=font, char=content_character)
    content_image_pil = content_image.copy()

    style_image = Image.open(style_image_path).convert('RGB')

    ## Dataset transform
    content_inference_transforms = transforms.Compose(
        [transforms.Resize(args.content_image_size, \
                            interpolation=transforms.InterpolationMode.BILINEAR),
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5])])
    style_inference_transforms = transforms.Compose(
        [transforms.Resize(args.style_image_size, \
                           interpolation=transforms.InterpolationMode.BILINEAR),
         transforms.ToTensor(),
         transforms.Normalize([0.5], [0.5])])
    
    content_image = content_inference_transforms(content_image)[None, :]
    style_image = style_inference_transforms(style_image)[None, :]

    return content_image, style_image, content_image_pil

def sampling(args, pipe, content_character=None, style_image_path=None, dir_name=None):
    # if not args.demo:
    #     os.makedirs(args.save_image_dir, exist_ok=True)
    #     save_args_to_yaml(args=args, output_file=f"{args.save_image_dir}/sampling_config.yaml")

    if args.seed:
        set_seed(seed=args.seed)
    
    content_image, style_image, content_image_pil = image_process(args=args, 
                                                                  content_character=content_character, 
                                                                  style_image_path=style_image_path)

    with torch.no_grad():
        content_image = content_image.to(args.device)
        style_image = style_image.to(args.device)
        print(f"Sampling by DPM-Solver++ ......")
        start = time.time()
        images = pipe.generate(
            content_images=content_image,
            style_images=style_image,
            batch_size=1,
            order=args.order,
            num_inference_step=args.num_inference_steps,
            content_encoder_downsample_size=args.content_encoder_downsample_size,
            t_start=args.t_start,
            t_end=args.t_end,
            dm_size=args.content_image_size,
            algorithm_type=args.algorithm_type,
            skip_type=args.skip_type,
            method=args.method,
            correcting_x0_fn=args.correcting_x0_fn)
        end = time.time()

        if args.save_image:
            print(f"Saving the image ......")
            # save_path = f"{dir_name}/{content_character}.png"
            codepoint = ord(content_character)
            save_path = f"{dir_name}/{content_character}_U{codepoint:04X}.png"
            images[0].save(save_path)

            # save_image_with_content_style(save_dir=dir_name,
            #                             image=images[0],
            #                             content_image_pil=content_image_pil,
            #                             content_image_path=None,
            #                             style_image_path=args.style_image_path,
            #                             resolution=args.resolution)

            print(f"Finish the sampling process, costing time {end - start}s")
        return images[0]


if __name__=="__main__":
    args = arg_parse()

    style_files = glob(os.path.join(args.style_image_path, "*/*.png"))

    pipe = load_fontdiffuer_pipeline(args=args)

    print(style_files)

    content_sentence = set("그리고 모든 기적이 시작되는 곳" + \
        "あまねく奇跡の始発点" + \
        "Where All Miracles Begin")
    
    content_sentence = "".join(sorted(ch for ch in content_sentence if ch != ' '))
    print(content_sentence)

    for style_file in style_files:

        print(style_file)

        style_path = Path(style_file)
        character_name = style_path.parent.name

        dir_name = os.path.join(args.save_image_dir, character_name)

        os.makedirs(dir_name, exist_ok=True)

        for content_character in content_sentence:

            out_image = sampling(args=args, pipe=pipe, 
                                 content_character=content_character, 
                                 style_image_path=style_file,
                                 dir_name=dir_name)
