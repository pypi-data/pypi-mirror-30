# -*- coding: utf-8 -*-

import math
from random import Random

import torch
import torch.nn.functional as f
import torch.optim as optim
from torch.autograd import Variable
from torch.utils.data import DataLoader, Dataset


class MySGD(optim.SGD):

    def __init__(self, params, lr=0.01, momentum=0.0,
                 dampening=0, weight_decay=0, nesterov=False):
        super().__init__(params, lr, momentum, dampening, weight_decay, nesterov)

    def step(self, closure=None):
        loss = None
        if closure is not None:
            loss = closure()

        for group in self.param_groups:
            weight_decay = group['weight_decay']
            momentum = group['momentum']
            dampening = group['dampening']
            nesterov = group['nesterov']

            for p in group['params']:

                # print(p.data, type(p.data))

                if p.grad is None:
                    continue
                d_p = p.grad.data
                if weight_decay != 0:
                    d_p.add_(weight_decay, p.data)
                if momentum != 0:
                    param_state = self.state[p]
                    if 'momentum_buffer' not in param_state:
                        buf = param_state['momentum_buffer'] = torch.zeros_like(p.data)
                        buf.mul_(momentum).add_(d_p)
                    else:
                        buf = param_state['momentum_buffer']
                        buf.mul_(momentum).add_(1 - dampening, d_p)
                    if nesterov:
                        d_p = d_p.add(momentum, buf)
                    else:
                        d_p = buf

                # print('Previous: {}, lr: {}, grad: {}'.format(p.data, group['lr'], d_p))
                p.data.add_(-group['lr'], d_p)
                # print('Now: {}'.format(p.data))

        return loss

    def get_delta_w(self):

        delta_ws = []
        for group in self.param_groups:
            weight_decay = group['weight_decay']
            momentum = group['momentum']
            dampening = group['dampening']
            nesterov = group['nesterov']

            for p in group['params']:

                # print(p)

                if p.grad is None:
                    continue
                d_p = p.grad.data
                if weight_decay != 0:
                    d_p.add_(weight_decay, p.data)
                if momentum != 0:
                    param_state = self.state[p]
                    if 'momentum_buffer' not in param_state:
                        buf = param_state['momentum_buffer'] = torch.zeros_like(p.data)
                        buf.mul_(momentum).add_(d_p)
                    else:
                        buf = param_state['momentum_buffer']
                        buf.mul_(momentum).add_(1 - dampening, d_p)
                    if nesterov:
                        d_p = d_p.add(momentum, buf)
                    else:
                        d_p = buf

                delta_ws.append(group['lr'] * d_p)

        return delta_ws


class Partition(object):
    """ Dataset partitioning helper """

    def __init__(self, data, index):
        self.data = data
        self.index = index

    def __len__(self):
        return len(self.index)

    def __getitem__(self, index):
        data_idx = self.index[index]
        return self.data[data_idx]


class DataPartitioner(object):

    def __init__(self, data, sizes=None, seed=1234):
        if sizes is None:
            sizes = [0.7, 0.2, 0.1]
        self.data = data
        self.partitions = []
        rng = Random()
        rng.seed(seed)
        data_len = len(data)
        indexes = [x for x in range(0, data_len)]
        rng.shuffle(indexes)

        for ratio in sizes:
            part_len = int(ratio * data_len)
            self.partitions.append(indexes[0:part_len])
            indexes = indexes[part_len:]

    def use(self, partition):
        return Partition(self.data, self.partitions[partition])


def partition_dataset(dataset, workers):
    """ Partitioning Data """
    workers_num = len(workers)
    partition_sizes = [1.0 / workers_num for _ in range(workers_num)]
    partition = DataPartitioner(dataset, partition_sizes)
    return partition


def select_dataset(workers: list, rank: int, partition: DataPartitioner, batch_size: int):
    workers_num = len(workers)
    partition_dict = {workers[i]: i for i in range(workers_num)}
    partition = partition.use(partition_dict[rank])
    return DataLoader(partition, batch_size=batch_size, shuffle=True)


def split_list(list_to_split, target_n, result):
    if (len(list_to_split) / target_n) % 1 == 0:
        n = int(len(list_to_split) / target_n)
        # print(n)
        i = 0
        while i < len(list_to_split):
            result.append(list_to_split[i:i + n])
            i += n
            # print(i)
    else:
        n = int(math.floor(len(list_to_split) / target_n))
        result.append(list_to_split[0:n])
        del list_to_split[0:n]
        split_list(list_to_split, target_n - 1, result)


class ThisRankDataset(Dataset):
    """产生数据倾斜，每一个learner中含有固定的label的数据集"""

    def __init__(self, all_data, labels, transform=None):

        img_list = []
        for idx, (img, label) in enumerate(all_data):
            if label in labels:
                img_list.append((img, int(label)))

        self.img_list = img_list
        self.transform = transform

    def __getitem__(self, index):
        img, label = self.img_list[index]
        if self.transform is not None:
            img = self.transform(img)
        return img, label

    def __len__(self):
        return len(self.img_list)


def test_model(rank, model, test_data):
    test_loss = 0
    correct = 0
    model.eval()
    for data, target in test_data:
        data, target = Variable(data, volatile=True), Variable(target)
        output = model(data)
        test_loss += f.nll_loss(output, target).data[0]  # Variable.data
        # get the index of the max log-probability
        pred = output.data.max(1)[1]
        correct += pred.eq(target.data).sum()

    # loss function averages over batch size
    test_loss /= len(test_data)
    print('Rank {}: Test set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)'
          .format(rank, test_loss, correct, len(test_data.dataset),
                  100. * correct / len(test_data.dataset)))
