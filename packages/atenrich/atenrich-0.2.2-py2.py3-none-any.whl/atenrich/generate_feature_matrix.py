import os.path
import numpy as np
from glob import glob
import pandas as pd

def generate_feature_df(genes_of_interest,db_id):
    
    genelist_path = os.path.join(os.path.dirname(__file__),'data','genelists')
    files = [y for x in os.walk(genelist_path) for y in glob(os.path.join(x[0], '*.genelist'))]

    feature_df = pd.DataFrame(index=genes_of_interest)

    for filename in files:
        with open(filename,'r') as f:
            input_file = f.readlines()
            list_info = input_file[0].strip().split('\t')
            feature_name = list_info[0]
            returned_gene_list = [x.strip().upper() for x in input_file[1:]]
        #features for this list
        binary_feature_vector = [int(x in returned_gene_list) for x in genes_of_interest]
        feature_df[feature_name] = binary_feature_vector
    
    return feature_df

def generate_feature_matrix(genes_of_interest,db_id):
    feature_df = generate_feature_df(genes_of_interest,db_id)
    feature_list = [x for x in feature_df.columns]
    return feature_df.as_matrix(),feature_list
