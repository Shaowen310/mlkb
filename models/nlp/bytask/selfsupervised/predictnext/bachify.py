import torch
from torch.utils.data import DataLoader


class CorpusBatchifyDataset(torch.utils.data.Dataset):
    def __init__(self, text_ids, batch_size):
        '''
        data of size (-1, batch_size)
        '''
        super().__init__()
        self.batch_size = batch_size
        n_batches = text_ids.size(0) // batch_size
        self.data = text_ids.narrow(0, 0, n_batches * batch_size)
        self.data = self.data.view(batch_size, -1).t().contiguous()

    def __getitem__(self, idx):
        return self.data[idx]

    def __len__(self):
        return len(self.data)


class CorpusBatchifyWindowDataset(CorpusBatchifyDataset):
    def __init__(self, text_ids, batch_size, window_size):
        super().__init__(text_ids, batch_size)
        self.window_size = window_size

    def __getitem__(self, idx):
        eid = idx + self.window_size - 1
        return self.data[idx:eid], self.data[eid]

    def __len__(self):
        return len(self.data) - self.window_size + 1


class CorpusBatchifyBPTTDataset(CorpusBatchifyDataset):
    def __init__(self, text_ids, batch_size, bptt):
        super().__init__(text_ids, batch_size)
        self.bptt = bptt

    def __getitem__(self, idx):
        sid = idx * self.bptt
        seq_len_ = min(self.bptt, len(self.data) - 1 - sid)
        eid = sid + seq_len_
        data_ = self.data[sid:eid]
        target = self.data[sid + 1:eid + 1].view(-1)
        return data_, target

    def __len__(self):
        return (len(self.data) - 1) // self.bptt + 1


if __name__ == '__main__':
    data_dir = ''
    parsed = False
    bptt = 35
    batch_size = 128

    corpus = None
    if parsed:
        corpus.load(data_dir)
    else:
        corpus.parse(data_dir)
        corpus.save(data_dir)
    ds_train = CorpusBatchifyBPTTDataset(corpus.train, batch_size, bptt)
    ds_valid = CorpusBatchifyBPTTDataset(corpus.valid, batch_size, bptt)
    ds_test = CorpusBatchifyBPTTDataset(corpus.test, batch_size, bptt)

    dl_train = DataLoader(dataset=ds_train, batch_size=None, shuffle=True)
    dl_valid = DataLoader(dataset=ds_valid, batch_size=None, shuffle=False)
    dl_test = DataLoader(dataset=ds_test, batch_size=None, shuffle=False)
