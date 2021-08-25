import os,sys
import json
import tensorflow as tf
from utils import *
from arguments import *
# working features with tr roseetta env
args = get_args()

msa_file     = args.ALN
npz_file     = args.NPZ

MDIR         = args.MDIR


def get_npz_name( _msa_file):
    name= os.path.basename(msa_file)

    if 'a3m'  in _msa_file:
        npz_name = name.replace('.a3m','.npz')
    elif 'fasta'  in _msa_file:
        npz_name = name.replace('.fasta', '.npz')

    return os.path.dirname(npz_file)+"/"+npz_name

n2d_layers   = 61
n2d_filters  = 64
window2d     = 3
wmin         = 0.8
ns           = 21

a3m = parse_a3m(msa_file)

contacts = {'pd':[], 'po':[], 'pt':[], 'pp':[]}

config = tf.compat.v1.ConfigProto(
    gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.9)
)
activation = tf.nn.elu
conv1d = tf.compat.v1.layers.conv1d
conv2d = tf.compat.v1.layers.conv2d
with tf.Graph().as_default():

    with tf.name_scope('input'):
        ncol = tf.compat.v1.placeholder(dtype=tf.int32, shape=())
        nrow = tf.compat.v1.placeholder(dtype=tf.int32, shape=())
        msa = tf.compat.v1.placeholder(dtype=tf.uint8, shape=(None,None))
        is_train = tf.compat.v1.placeholder(tf.bool, name='is_train')

    msa1hot  = tf.one_hot(msa, ns, dtype=tf.float32)
    w = reweight(msa1hot, wmin)

    # 1D features
    f1d_seq = msa1hot[0,:,:20]
    f1d_pssm = msa2pssm(msa1hot, w)

    f1d = tf.concat(values=[f1d_seq, f1d_pssm], axis=1)
    f1d = tf.expand_dims(f1d, axis=0)
    f1d = tf.reshape(f1d, [1,ncol,42])

    # 2D features
    f2d_dca = tf.cond(nrow>1, lambda: fast_dca(msa1hot, w), lambda: tf.zeros([ncol,ncol,442], tf.float32))
    f2d_dca = tf.expand_dims(f2d_dca, axis=0)

    f2d = tf.concat([tf.tile(f1d[:,:,None,:], [1,1,ncol,1]), 
                    tf.tile(f1d[:,None,:,:], [1,ncol,1,1]),
                    f2d_dca], axis=-1)
    f2d = tf.reshape(f2d, [1,ncol,ncol,442+2*42])

    layers2d = [f2d]
    for filename in os.listdir(MDIR):
        if not filename.endswith(".index"):
            continue
        ckpt = MDIR+"/"+os.path.splitext(filename)[0]
        with tf.compat.v1.Session(config=config) as sess:
            # saver.restore(sess, ckpt)
            fil = sess.run([f2d],
                                       feed_dict = {msa : a3m, ncol : a3m.shape[1], nrow : a3m.shape[0], is_train : 0})

            print(ckpt, '- done')



# save distograms & anglegrams
output_file = get_npz_name(msa_file)
np.savez_compressed(output_file, fil)
