#!/usr/bin/env python

import torch.utils.data as data
from PIL import Image
import os
import os.path
import errno
import torch
from StringIO import StringIO
from torchvision import transforms


transform_512_train = transforms.Compose([
    transforms.RandomCrop([512,1024]),
    transforms.Resize((256,512)),
    transforms.Grayscale(),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
])

transform_test = transforms.Compose([
    transforms.RandomCrop([384,1024]),
    transforms.Resize((384,512)),
    transforms.Grayscale(),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
])

def read_rar_file(rarstream):
    names=rarstream.namelist()
    sample_list=[]
    for name in names:
        img=Image.open(StringIO(rarstream.read(rarstream.getinfo(name)))).copy()
        [writer_id,sample_id] =[int(s) for s in name[:name.find(".")].split("_")]
        language_id=(sample_id-1)/2 # icdar 2013: english 1,2 and greek 3,4
        sample_list.append((img,(writer_id,language_id,sample_id)))
    return sample_list




class WI2013(data.Dataset):
    """Contemporary Writer identification dataset


    Citation: http://users.iit.demokritos.gr/~bgat/ICDAR_2013_Louloudis.pdf
    """
    urls = [
        'http://users.iit.demokritos.gr/~louloud/ICDAR2013WriterIdentificationComp/experimental_dataset_2013.rar',
        'http://users.iit.demokritos.gr/~louloud/ICDAR2013WriterIdentificationComp/icdar2013_benchmarking_dataset.rar'
    ]
    raw_folder = 'raw'
    processed_folder = 'processed'
    training_file = 'training.pt'
    test_file = 'test.pt'


    def __init__(self, root, train=True, transform=None, target_transform=None, download=False,output_class="writer"):
        assert output_class in ("writer","sample","script")
        if transform is None:
            if train:
                transform = transform_512_train
            else:
                transform = transform_test
        self.output_select= {"writer":lambda x:(x[0],x[1][0]-1),"sample":lambda x:(x[0],x[1][1]-1),"script":lambda x:(x[0],x[1][0]-1)}[output_class]
        self.root = os.path.expanduser(root)
        self.transform = transform
        self.target_transform = target_transform
        self.train = train  # training set or test set

        if download:
            self.download()

        if not self._check_exists():
            raise RuntimeError('Dataset not found.' +
                               ' You can use download=True to download it')

        if self.train:
            self.train_samples = torch.load(
                os.path.join(self.root, self.processed_folder, self.training_file))
        else:
            self.test_samples = torch.load(
                os.path.join(self.root, self.processed_folder, self.test_file))


    def __getitem__(self, index):
        """
        Args:
            index (int): Index
        Returns:
            tuple: (image, target) where target is index of the target class.
        """
        if self.train:
            img, target = self.output_select(self.train_samples[index])
            target=target-26
        else:
            img, target = self.output_select(self.test_samples[index])

        # doing this so that it is consistent with all other datasets
        # to return a PIL Image
        img = img#.fromarray(img.numpy(), mode='L')

        if self.transform is not None:
            img = self.transform(img)

        if self.target_transform is not None:
            target = self.target_transform(target)

        return img, target

    def __len__(self):
        if self.train:
            return len(self.train_samples)
        else:
            return len(self.test_samples)

    def _check_exists(self):
        return os.path.exists(os.path.join(self.root, self.processed_folder, self.training_file)) and \
            os.path.exists(os.path.join(self.root, self.processed_folder, self.test_file))

    def download(self):
        """Download the MNIST data if it doesn't exist in processed_folder already."""
        from six.moves import urllib
        import rarfile

        if self._check_exists():
            return

        # download files
        try:
            os.makedirs(os.path.join(self.root, self.raw_folder))
            os.makedirs(os.path.join(self.root, self.processed_folder))
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise

        for url in self.urls:
            print('Downloading ' + url)
            data = urllib.request.urlopen(url)
            filename = url.rpartition('/')[-1]
            file_path = os.path.join(self.root, self.raw_folder, filename)
            with open(file_path, 'wb') as f:
                f.write(data.read())
            with rarfile.RarFile(file_path) as rar_f:
                rar_f.extractall(self.raw_folder)
            #os.unlink(file_path)

        # process and save as torch files
        print('Processing...')
        train_set = read_rar_file(rarfile.RarFile(os.path.join(self.root, self.raw_folder, 'experimental_dataset_2013.rar')))
        test_set = read_rar_file(
            rarfile.RarFile(os.path.join(self.root, self.raw_folder, 'icdar2013_benchmarking_dataset.rar')))
        with open(os.path.join(self.root, self.processed_folder, self.training_file), 'wb') as f:
            torch.save(train_set, f)
        with open(os.path.join(self.root, self.processed_folder, self.test_file), 'wb') as f:
            torch.save(test_set, f)

        print('Done!')

    def __repr__(self):
        fmt_str = 'Dataset ' + self.__class__.__name__ + '\n'
        fmt_str += '    Number of datapoints: {}\n'.format(self.__len__())
        tmp = 'train' if self.train is True else 'test'
        fmt_str += '    Split: {}\n'.format(tmp)
        fmt_str += '    Root Location: {}\n'.format(self.root)
        tmp = '    Transforms (if any): '
        fmt_str += '{0}{1}\n'.format(tmp, self.transform.__repr__().replace('\n', '\n' + ' ' * len(tmp)))
        tmp = '    Target Transforms (if any): '
        fmt_str += '{0}{1}'.format(tmp, self.target_transform.__repr__().replace('\n', '\n' + ' ' * len(tmp)))
        return fmt_str


if __name__=="__main__":
    trds = WI2013('./data/wi2013', train=True, transform=None, target_transform=None, download=True)
    tstds = WI2013('./data/wi2013', train=False, transform=None, target_transform=None, download=True)
