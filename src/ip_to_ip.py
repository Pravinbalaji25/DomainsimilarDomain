# IP-to-IP matrix for CU HIN project


# import libraries
import argparse
import pandas as pd
import scipy.sparse as sp
import time
import dataprun


def applyPrune(intoPFile):
    # Implements datapruning
    LogList = []  
    LogList.append(intoPFile)   
    RL, DD, IPD = dataprun.GenerateWL(LogList)
    return IPD    


def main():
    '''
    Ip_to_ip.py creates the ip to ip csr matrix for hindom project
    Usage: python ip_to_ip.py --inputfile /data/dns/2021-03-14_dns.12:00:00-13:00:00.log
    Requires: dataprun.py
    '''

    # Process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputfile', type=str, required=True,
                        help='Expects log file from /data/dns directory')
    flags = parser.parse_args()

    # Extract SRC and DEST IPs addresses as though from a csv file
    ts = time.time()
    with open(flags.inputfile, 'r') as infile:
        ip2ip = pd.read_csv(infile, sep='\\t', header=(7), usecols=[2, 4], names=['id.orig_h', 'id.resp_h'], engine='python')

    # Extract list of unique IP  addresses
    srcuniq = ip2ip['id.orig_h'].unique()
    destuniq = ip2ip['id.resp_h'].unique()
    # print('Unique Src IPs       :  ', len(srcuniq))
    # print('Unique Dest IPs      :  ', len(destuniq))

    # Implement pruning 
    IPD = applyPrune(flags.inputfile)
    
    # Create inverse dictionary
    # invIPD = {v: k for k, v in IPD.items()}

    # Map back to df
    ip2ip['srcint'] = ip2ip['id.orig_h'].map(IPD)
    ip2ip['destint'] = ip2ip['id.resp_h'].map(IPD)
    ip2ip = ip2ip.dropna()
    ip2ip = ip2ip.astype({'srcint': int, 'destint': int})
    # print('Unique Src IPs  PRUNED:  ', len(ip2ip['srcint'].unique()))
    # print('Unique Dest IPs PRUNED:  ', len(ip2ip['destint'].unique()))

    # Count repeat pairs 
    pairindex = ip2ip.groupby(['srcint', 'destint']).indices
    paircount = {k: len(v) for k, v in pairindex.items()}
    # print('Pair count      :  ', len(paircount))

    # Extracting src, dest, counts
    xypair = list(paircount.keys())
    cols = [i[0] for i in xypair]        # Setting src/'x' to be column
    rows = [i[1] for i in xypair]        # Setting dest/'y' to be row
    vals = list(paircount.values())      # Values

    # Create Compressed Sparse Row Matrix
    ip2ipmatrix = sp.csr_matrix((vals, (rows, cols)))
    # print('Time, seconds        :  ', time.time() - ts)

    # print(ip2ipmatrix)

    return ip2ipmatrix

if __name__ == '__main__':
    main()
