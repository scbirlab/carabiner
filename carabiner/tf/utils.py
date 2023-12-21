try:
    import tensorflow as tf
except ImportError:
    raise ImportError("\nTensorflow not installed. Try installing with pip:"
                      "\n\tpip install tensorflow\n")

@tf.function(experimental_compile=True)
def sparse_matmul(a, b):
    
    new_b = tf.concat([b, tf.zeros((1, b.shape[-1]))], 
                        axis=0)
    a_new = tf.where(a < 0, new_b.shape[-1] + a, a)
    a_new = tf.cast(a_new, dtype=tf.int32)

    result = tf.gather(params=new_b, 
                       indices=a_new,
                       axis=-2)
    
    return tf.reduce_sum(result, axis=-2)


@tf.function(experimental_compile=True)
def sparse_matmul_t(a, b):
    
    new_b = tf.concat([b, tf.zeros((b.shape[-2], 1))], 
                        axis=1)
    a_new = tf.where(a < 0, new_b.shape[-2] + a, a)
    a_new = tf.cast(a_new, dtype=tf.int32)

    result = tf.gather(params=new_b, indices=a_new, axis=-1)
    
    return tf.reduce_sum(result, axis=-1)


@tf.function(experimental_compile=True)
def get_param(dim0, dim1, m):

    param = dim0 @ m
    param = tf.expand_dims(dim1, axis=-2) @ tf.expand_dims(param, axis=-1)
    param = tf.squeeze(param, axis=-1)

    return param


@tf.function(experimental_compile=True)
def get_param_sparse(dim0, dim1, m):

    dim0, dim1 = tf.cast(dim0, dtype=tf.int32), tf.cast(dim1, dtype=tf.int32)

    new_m = tf.concat([m, tf.zeros((m.shape[-2], 1))], 
                      axis=1)
    new_m = tf.concat([new_m, 
                       tf.zeros((1, new_m.shape[-1]))], 
                       axis=0)
    dim0 = tf.where(dim0 < 0, new_m.shape[-2] + dim0, dim0)
    dim1 = tf.where(dim1 < 0, new_m.shape[-1] + dim1, dim1)

    param = tf.gather_nd(new_m, 
                         indices=tf.concat([dim0, dim1], 
                         axis=-1))[:, tf.newaxis]

    return param