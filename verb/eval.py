import os,sys,pickle
import numpy as np
import argparse
from sklearn.metrics import confusion_matrix
from matplotlib import pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('results_file', help = 'Results file')
parser.add_argument('action_ids_file', help = 'Action IDs file')
args = parser.parse_args()

action_types = dict()
action_ids = dict()
with open(args.action_ids_file, 'r') as fr:
    for line in fr.readlines():
        tokens = line.strip().split(' ')
        action_types[int(tokens[1])] = tokens[0]
        action_ids[tokens[0]] = int(tokens[1])

# overall accuracy
num_correct = 0
results = pickle.load(open(args.results_file, 'r'))
temp = list()
false_results = dict()
per_action_results = dict()
for video in results['scores']:
    action = '_'.join(video.split('_')[1:-1])
    if action not in per_action_results:
        per_action_results[action] = dict()
    predict_action = action_types[np.argmax(results['scores'][video])]
    if action == predict_action:
        num_correct += 1
    if action != predict_action:
        temp.append(video + ' -> ' + predict_action)
        verb = action.split('_')[0]
        if verb not in false_results:
            false_results[verb] = list()
        false_results[verb].append(predict_action)
    per_action_results[action][video] = results['scores'][video]

for t in sorted(temp):
    print t

for verb in false_results:
    print verb, len(false_results[verb]), false_results[verb]

print 'overal accuracy:', float(num_correct)/len(results['scores'])

# average accuracy
true_labels = []
predict_labels = []
accuracy = list()
take_accuracy = list()
put_accuracy = list()
for action in per_action_results:
    scores = per_action_results[action]
    num_correct = 0
    for video in scores:
        predict_action = action_types[np.argmax(scores[video])]
        true_labels.append(action_ids[action])
        predict_labels.append(action_ids[predict_action])
        if action == predict_action:
            num_correct += 1
    a = float(num_correct)/len(scores)
    accuracy.append(a)
    if action.startswith('take'):
        take_accuracy.append(a)
    if action.startswith('put'):
        put_accuracy.append(a)
    print action, accuracy[-1]
print 'average accuracy:', sum(accuracy)/len(accuracy)
print 'average take accuracy:', sum(take_accuracy)/len(take_accuracy)
print 'average put accuracy:', sum(put_accuracy)/len(put_accuracy)

# confusion matrix
cm = confusion_matrix(true_labels, predict_labels)

cm = cm.astype(np.float)/cm.sum(axis = 1)[:, np.newaxis]

def plot_cm(cm, title, names):
    plt.imshow(cm, interpolation = 'nearest')
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(names))
    #plt.xticks(tick_marks, names, rotation=45)
    plt.yticks(tick_marks, names, fontsize=9)
    #plt.tight_layout()
    #plt.ylabel('True label')
    #plt.xlabel('Predicted label')

#names = [action_types[i] for i in range(len(action_typesi))]
names = per_action_results.keys()
plot_cm(cm, "GTEA 71 classes", names)
plt.show()

