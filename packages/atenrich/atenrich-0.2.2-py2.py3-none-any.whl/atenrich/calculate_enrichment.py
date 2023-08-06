import numpy as np
import pandas as pd
from convert_clustering_to_classification import convert_clustering_to_classification
import rank_features

def cluster_enrichment(cluster_labels,feature_matrix,feature_list,cluster_indices):

    if not cluster_indices:
        #use default - analyse all clusters
        cluster_indices = list(set(cluster_labels))
    
    #get a binary classification vector for each cluster
    clustering_classifications = convert_clustering_to_classification(cluster_labels)
    
    
    pval_df = pd.DataFrame(index=feature_list,columns=cluster_indices)
    FE_df = pd.DataFrame(index=feature_list,columns=cluster_indices)
    
    for cluster_idx in cluster_indices:
        classification = clustering_classifications[cluster_idx]
        
        pvals = rank_features.hypergeometric(classification,feature_matrix)
        pval_df[cluster_idx] = pd.Series(-np.log10(pvals),index=feature_list)

        FE = rank_features.FE(classification,feature_matrix)
        FE_df[cluster_idx] = pd.Series(FE,index=feature_list)

    return pval_df,FE_df

def list_enrichment(gene_list,background_gene_list,feature_matrix,feature_list):

    #get a binary classification vector for the list
    classification = [int(x in gene_list) for x in background_gene_list]
    
    pval_df = pd.DataFrame(index=feature_list,columns=['pval_enrichment'])
    pvals = rank_features.hypergeometric(classification,feature_matrix)
    pval_df['pval_enrichment'] = pd.Series(-np.log10(pvals),index=feature_list)

    FE_df = pd.DataFrame(index=feature_list,columns=['fold_enrichment'])
    FE = rank_features.FE(classification,feature_matrix)
    FE_df['fold_enrichment'] = pd.Series(FE,index=feature_list)
    
    return pval_df,FE_df

if __name__ == "__main__":
    import doctest
    doctest.testmod()