"""
Preparing model:
 - Install bazel ( check tensorflow's github for more info )
    Ubuntu 14.04:
        - Requirements:
            sudo add-apt-repository ppa:webupd8team/java
            sudo apt-get update
            sudo apt-get install oracle-java8-installer
        - Download bazel, ( https://github.com/bazelbuild/bazel/releases )
          tested on: https://github.com/bazelbuild/bazel/releases/download/0.2.0/bazel-0.2.0-jdk7-installer-linux-x86_64.sh
        - chmod +x PATH_TO_INSTALL.SH
        - ./PATH_TO_INSTALL.SH --user
        - Place bazel onto path ( exact path to store shown in the output)
- For retraining, prepare folder structure as
    - root_folder_name
        - class 1
            - file1
            - file2
        - class 2
            - file1
            - file2
- Clone tensorflow
- Go to root of tensorflow
- bazel build tensorflow/examples/image_retraining:retrain
- bazel-bin/tensorflow/examples/image_retraining/retrain --image_dir /path/to/root_folder_name  --output_graph /path/output_graph.pb --output_labels /path/output_labels.txt --bottleneck_dir /path/bottleneck
** Training done. **
For testing through bazel,
    bazel build tensorflow/examples/label_image:label_image && \
    bazel-bin/tensorflow/examples/label_image/label_image \
    --graph=/path/output_graph.pb --labels=/path/output_labels.txt \
    --output_layer=final_result \
    --image=/path/to/test/image
For testing through python, change and run this code.
"""

#pylint: disable=wrong-import-position,superfluous-parens
import os
import sys
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
import numpy as np
#import tensorflow as tf
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior( )

modelFullPath = 'models/ukGardenModel.pb'
labelsFullPath = 'models/ukGardenModel_labels.txt'


def create_graph():
    """Creates a graph from saved GraphDef file and returns a saver."""
    # Creates graph from saved graph_def.pb.
    with tf.io.gfile.GFile(modelFullPath, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(graph_def, name='')


def run_inference_on_image(imagePath):
    answer = None

    if not tf.gfile.Exists(imagePath):
        tf.logging.fatal('File does not exist %s', imagePath)
        return answer

    image_data = tf.gfile.FastGFile(imagePath, 'rb').read()


    with tf.Session() as sess:
        softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
        predictions = sess.run(softmax_tensor,
                               {'DecodeJpeg/contents:0': image_data})
        predictions = np.squeeze(predictions)
        top_k = predictions.argsort()[-5:][::-1]  # Getting top 5 predictions
        #f = open(labelsFullPath, 'rb')
        f = open(labelsFullPath, 'r')
        #lines = f.readlines()
        lines = f.readlines()
        labels = [str(w).replace("\n", "") for w in lines]
        for node_id in top_k:
            human_string = labels[node_id]
            score = predictions[node_id]
            #print (f" {human_string}: {score}")
            #printGraph(score)
            # print('\t%s (score = %.5f)' % (human_string, score))
        print(f'Most likely detected object is : {labels[top_k[0]]}  ({(predictions[top_k[0]])*100.0:.02f}%)')
        answer = labels[top_k[0]]
        return answer

def findImages():
    '''Finds all the Jpegs in a directory
    and feeds them into the model
    '''
    print('Getting directory listing')
    for image in os.listdir("testImages"):
        print(f'testing {image}')
        if image.endswith(".jpg"):
            print (f"Classifying {image}:")
            result = run_inference_on_image(f"testImages/{image}")

def printGraph(amount):
    '''takes a float between 0 and 1 and prints a graph
    '''
    value = amount * 20
    sys.stdout.write(" ")
    for x in range(int(value)):
        sys.stdout.write("#")
    sys.stdout.flush()
    print ("")


if __name__ == '__main__':
    print('Creating graph')
    create_graph()
    print ("graph Created")
    #run_inference_on_image('test.jpg')
    findImages()
