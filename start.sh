rosrun stage_ros stageros $(rospack find stage_ros)/world/exp.world \
& python ~/rosAmbassador/obstacle.py 1 0 \
& python ~/rosAmbassador/obstacle.py 2 5 \
& python ~/rosAmbassador/obstacle.py 3 3
