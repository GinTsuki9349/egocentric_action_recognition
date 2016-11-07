#!/bin/bash
python solve.py train_gtea.prototxt ../verb_hand/deploy2.prototxt ../obj/obj_cropped/obj_deploy_gteah.prototxt GTEA_data/S1_train.txt ../obj/obj_cropped/GTEA_model/OBJ_GTEA_S1_iter_3000.caffemodel ../verb_hand/GTEAH_model/GTEAH_S1_T2_iter_2000.caffemodel GTEA_model/HAND_VERB_OBJ_GTEA_S1 4000 0 2>&1 | tee log/solve_gtea_s1.log
#python solve.py train_gtea.prototxt ../verb_hand/deploy2.prototxt ../obj/obj_cropped/obj_deploy_gteah.prototxt GTEA_data/S2_train.txt ../obj/obj_cropped/GTEA_model/OBJ_GTEA_S2_iter_3000.caffemodel ../verb_hand/GTEAH_model/GTEAH_S2_T2_iter_2000.caffemodel GTEA_model/HAND_VERB_OBJ_GTEA_S2 4000 1 2>&1 | tee log/solve_gtea_s2.log
#python solve.py train_gtea.prototxt ../verb_hand/deploy2.prototxt ../obj/obj_cropped/obj_deploy_gteah.prototxt GTEA_data/S3_train.txt ../obj/obj_cropped/GTEA_model/OBJ_GTEA_S3_iter_3000.caffemodel ../verb_hand/GTEAH_model/GTEAH_S3_T2_iter_2000.caffemodel GTEA_model/HAND_VERB_OBJ_GTEA_S3 4000 1 2>&1 | tee log/solve_gtea_s3.log
#python solve.py train_gtea.prototxt ../verb_hand/deploy2.prototxt ../obj/obj_cropped/obj_deploy_gteah.prototxt GTEA_data/S4_train.txt ../obj/obj_cropped/GTEA_model/OBJ_GTEA_S4_iter_3000.caffemodel ../verb_hand/GTEAH_model/GTEAH_S4_T2_iter_2000.caffemodel GTEA_model/HAND_VERB_OBJ_GTEA_S4 4000 1 2>&1 | tee log/solve_gtea_s4.log
