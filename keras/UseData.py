import pickle
import tables

class UseData:
    def __init__(self):
        self.use_methname = "./data/github/use.methname.h5"
        self.use_apiseq = "./data/github/use.apiseq.h5"
        self.use_tokens = "./data/github/use.tokens.h5"

    def load_use_data(self):
        methnames=self.load_hdf5(self.use_methname,0,-1)
        apiseqs=self.load_hdf5(self.use_apiseq,0,-1)
        tokens=self.load_hdf5(self.use_tokens,0,-1) 
        return methnames,apiseqs,tokens  

    def load_hdf5(self,vecfile,start_offset,chunk_size):
        """reads training sentences(list of int array) from a hdf5 file"""  
        table = tables.open_file(vecfile)
        data, index = (table.get_node('/phrases'),table.get_node('/indices'))
        data_len = index.shape[0]
        
        if chunk_size==-1:#if chunk_size is set to -1, then, load all data
            chunk_size=data_len
        start_offset = start_offset%data_len
        offset=start_offset
        sents = []
        while offset < start_offset+chunk_size:
            if offset>=data_len:   
                chunk_size=start_offset+chunk_size-data_len
                start_offset=0
                offset=0
            len, pos = index[offset]['length'], index[offset]['pos']
            offset += 1
            sents.append(data[pos:pos + len].astype('float32'))
        table.close()
        return sents 