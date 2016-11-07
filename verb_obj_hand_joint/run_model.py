caffe_root = '/home/minghuam/caffe-dev/'
import sys,os
sys.path.insert(0, os.path.join(caffe_root, 'python'))
import caffe
import cv2
import numpy as np
import argparse
import random
from collections import deque
import pickle
import random

def ls_images(folder_path, extension = '.png'):
    return sorted([os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(extension)])

def get_frame_num(img):
    return int(os.path.splitext(os.path.basename(img))[0].split('_')[-1])

def predict_one_video(net, Iobj_mean, Ihand_mean, flow_x_images, flow_y_images, hand_images, obj_images):
    crop_size = 224
    num_stack_frames = 10
    flow_mean = 128.0
    action_prob = None
    num_runs = 0

    Iobj_mean = Iobj_mean.transpose((1, 2, 0))
    Ihand_mean = Ihand_mean.reshape((Ihand_mean.shape[1], Ihand_mean.shape[2]))

    x = (Iobj_mean.shape[1] - crop_size)/2
    y = (Iobj_mean.shape[0] - crop_size)/2
    Iobj_mean = Iobj_mean[y:y + crop_size, x:x + crop_size, :]
    Ihand_mean = Ihand_mean[y:y + crop_size, x:x + crop_size]

    # cv2.imshow('Iobj_mean', Iobj_mean.astype(np.uint8))
    # cv2.imshow('Ihand_mean', Ihand_mean.astype(np.uint8))
    # if cv2.waitKey(0) & 0xFF == 27:
    #     sys.exit(0)

    Iq = deque()

    obj_frame_nums = list()
    for img in obj_images:
        obj_frame_nums.append(get_frame_num(img))

    for imgs in zip(flow_x_images, flow_y_images, hand_images):
        Is = list()
        for i, img in enumerate(imgs):
            I = cv2.imread(img)
            x = (I.shape[1] - crop_size)/2
            y = (I.shape[0] - crop_size)/2
            I = I[y:y + crop_size, x:x + crop_size, :]
            if i < 2:
                I = I[...,0].astype(np.float64) - flow_mean
            else:
                I = I[...,0].astype(np.float64) - Ihand_mean
            Is.append(I)

        Iq.append(Is)

        if len(Iq) == num_stack_frames:
            
            data = np.zeros((1, num_stack_frames * 3 + 3, crop_size, crop_size), np.float64)
            for i, (Ix, Iy, Ih) in enumerate(Iq):
                data[0,i*3+0,...] = Ix
                data[0,i*3+1,...] = Iy
                data[0,i*3+2,...] = Ih

            end = get_frame_num(imgs[0])
            start = end - num_stack_frames + 1
            mid = (end + start)/2

            if start > max(obj_frame_nums):
                break

            index = np.argmin(np.abs(mid - np.array(obj_frame_nums)))
            Iobj = cv2.imread(obj_images[index])
            #sprint start, end, obj_images[index]

            #cv2.imshow('Iobj', Iobj)
            #cv2.waitKey(30)

            x = (Iobj.shape[1] - crop_size)/2
            y = (Iobj.shape[0] - crop_size)/2
            Iobj = Iobj[y:y + crop_size, x:x + crop_size, :]
            Iobj = Iobj.astype(np.float64) - Iobj_mean
            Iobj = Iobj.transpose((2, 0, 1))
            data[0,30:,...] = Iobj
            index += 1    

            net.blobs['pair_data'].data[...] = data
            ret = net.forward()
            action_score = ret['action_score'].ravel()
            motion_index = np.argmax(ret['verb_score'].ravel())
            obj_index = np.argmax(ret['object_score'].ravel())
            #print verb_types[motion_index], obj_types[obj_index]

            num_runs += 1
            
            if action_prob is None:
                action_prob = action_score
            else:
                action_prob = action_prob + action_score
            
            Iq.popleft()

    return action_prob/num_runs


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('deploy_prototxt', help = "Deploy prototxt")
    parser.add_argument('test_file', help = 'Test file')
    parser.add_argument('hand_mean_file', help = 'Hand mean file')
    parser.add_argument('subject', help = 'Subject')
    parser.add_argument('dataset', help = 'dataset')
    parser.add_argument('iterations', help = 'interations')
    parser.add_argument('gpu_id', help = 'GPU ID')
    args = parser.parse_args()

    caffe.set_mode_gpu()
    caffe.set_device(int(args.gpu_id))

    subject = args.subject
    dataset = args.dataset
    n_iterations = int(args.iterations)
    output_dir = '{}_output'.format(dataset)
    net_proto_file = args.deploy_prototxt
    image_mean_file = 'imagenet_mean.npy'
    model_file = '{}_model/{}_{}_iter_{}.caffemodel'.format(dataset, dataset, subject, n_iterations)
    action_ids_file = '{}_data/action_ids.txt'.format(dataset)

    results = dict()
    results['dataset'] = dataset
    results['subject'] = subject
    results['n_iterations'] = n_iterations

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    hand_mean_file = args.hand_mean_file

    Iobj_mean = np.load(image_mean_file)
    Ihand_mean = np.load(hand_mean_file)

    action_types = dict()
    with open(action_ids_file, 'r') as fr:
        for line in fr.readlines():
            tokens = line.strip().split(' ')
            action_types[int(tokens[1])] = tokens[0]

    net = caffe.Net(net_proto_file, model_file, caffe.TEST)

    test_videos = dict()
    with open(args.test_file, 'r') as fr:
        for line in fr.readlines():
            tokens = line.strip().split(' ')
            flow_folder = tokens[0]
            hand_folder = tokens[1]
            image_folder = tokens[2]
            labels = [int(tokens[3]), int(tokens[3]), int(tokens[4])]
            video_folder = os.path.basename(flow_folder)
            test_videos[video_folder] = (flow_folder, hand_folder, image_folder, labels)

    scores = dict()
    n_videos = len(test_videos)
    num_correct = 0
    for i, video_folder in enumerate(test_videos):
        flow_image_folders = test_videos[video_folder][0]
        flow_x_images = ls_images(os.path.join(test_videos[video_folder][0], 'x'), '.jpg')
        flow_y_images = ls_images(os.path.join(test_videos[video_folder][0], 'y'), '.jpg')
        hand_images = ls_images(test_videos[video_folder][1], '.jpg')
        obj_images = ls_images(test_videos[video_folder][2], '.jpg')
        
        score = predict_one_video(net, Iobj_mean, Ihand_mean, flow_x_images, flow_y_images, hand_images, obj_images)
        scores[video_folder] = score
        action_type = action_types[np.argmax(score)]
        print '{}: {}/{}, {}'.format(video_folder, i+1, n_videos, action_type)
        if action_type == '_'.join(video_folder.split('_')[1:-1]):
            num_correct += 1
    print num_correct, len(test_videos), float(num_correct)/len(test_videos)

    save_file = os.path.splitext(os.path.basename(args.test_file))[0] + '_{}_results.pkl'.format(n_iterations)
    results['scores'] = scores

    pickle.dump(results, open(os.path.join(output_dir, save_file), 'w'))