import scipy.stats
import numpy as np

def hypergeometric(binary_classification,feature_matrix):
    
    X = feature_matrix
    y = binary_classification
    nF = feature_matrix.shape[1]

    pvals = np.ones(nF) #p-values

    M = feature_matrix.shape[0] #total number of objects
    n = sum(y) #number in class
    for feature_idx in range(nF):
        N = sum(X[:,feature_idx]) #number positive for this feature
        k = sum(np.multiply(X[:,feature_idx],y)) #number of positives within this set
        pvals[feature_idx] = scipy.stats.hypergeom.sf(k,M,n,N)
    
    return pvals
    
def FE(class_vector,feature_matrix):
    '''Calculate fold enrichment of class members in feature categories
    
    Args:
        class_vector: 1-by-nG array
        feature_matrix: nG-by-nF array
    Returns:
        1-by-nF array
    
    Example:
    >>> class_vector = np.array([0,1,1,0,0,0,0])
    >>> feature_matrix = np.array([[0,0],[1,0],[1,1],[1,0],[1,0],[0,1],[1,1]])
    >>> FE(class_vector,feature_matrix)
    array([ 1.4       ,  1.16666667])'''

    assert(all([x in [0,1] for x in class_vector])) #classification vector is binary

    nF = feature_matrix.shape[1]

    fold_enrich = np.ones(nF) #fold enrichment

    M = feature_matrix.shape[0] #total number of objects
    n = sum(class_vector) #number in class
    for feature_idx in range(nF):
        feature_vector = feature_matrix[:,feature_idx]
        N = sum(feature_vector) #number positive for this feature
        k = sum(np.multiply(feature_vector,class_vector)) #number of positives within this set
        try:
            fold_enrich[feature_idx] = (float(k)/n)/(float(N)/M)
        except ZeroDivisionError:
            fold_enrich[feature_idx] = 1.0
    
    return fold_enrich