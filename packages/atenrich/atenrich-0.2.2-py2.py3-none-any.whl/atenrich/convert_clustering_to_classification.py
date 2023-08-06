import numpy as np

def convert_clustering_to_classification(cluster_list):
    '''Binarise the input cluster classification list
    
    Return a binary numpy array of size (nClusters x nGenes)
    >>> cluster_list = [0,0,1,1,2,1]
    >>> convert_clustering_to_classification(cluster_list)
    array([[1, 1, 0, 0, 0, 0],
           [0, 0, 1, 1, 0, 1],
           [0, 0, 0, 0, 1, 0]])
    '''
    cluster_labels = sorted(list(set(cluster_list)))
    binary_classification = [ [int(x==label) for x in cluster_list] for label in cluster_labels]
    return np.array(binary_classification)