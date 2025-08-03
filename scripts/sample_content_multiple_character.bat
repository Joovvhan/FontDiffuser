@echo off
python sample_multiple.py ^
--ckpt_dir="ckpt/" ^
--style_image_path="./reference" ^
--save_image ^
--character_input ^
--save_image_dir="outputs/" ^
--device="cuda:0" ^
--algorithm_type="dpmsolver++" ^
--guidance_type="classifier-free" ^
--guidance_scale=7.5 ^
--num_inference_steps=50 ^ 
REM --num_inference_steps=20 ^
--method="multistep" ^