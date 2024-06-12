
* Download videos following the README.
* Create symlinks for SSv2 videos
```sh
python bin/create_ssv2_symlinks.py --src_dir /scratch/shared/nfs2/piyush/datasets/SSv2/20bn-something-something-v2/ --dst_dir /scratch/shared/nfs2/piyush/datasets/ViLMA/videos/ --annotation ./data/change-state-action.json 
```
* Create symlinks for STAR videos (Charades)
```sh
python bin/create_star_symlinks.py --src_dir /scratch/shared/nfs2/piyush/datasets/Charades/Charades_v1_480/ --dst_dir /scratch/shared/nfs2/piyush/datasets/ViLMA/videos/ --annotation ./data/change-state-action.json 
```