import argparse
import os
import logging
import logging.handlers
import random
import numpy as np
import torch
from datetime import datetime


# DEBUG < INFO < WARNING < ERROR < CRITICAL
def get_logger(filename, args):
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(levelname)s | %(filename)s:%(lineno)s] %(asctime)s: %(message)s')

    if not os.path.isdir(args.log_dir):
        os.mkdir(args.log_dir)

    file_handler = logging.FileHandler('./log/' + filename + '.log')
    stream_handler = logging.StreamHandler()

    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


def get_args():
    parser = argparse.ArgumentParser('parameters')

    parser.add_argument('--dataset', type=str, default='CIFAR10', help='CIFAR10, CIFAR100, MNIST, IMAGENET')
    parser.add_argument('--model-name', type=str, default='ResNet26', help='ResNet26, ResNet38, ResNet50')
    parser.add_argument('--img-size', type=int, default=32)
    parser.add_argument('--batch-size', type=int, default=25)
    parser.add_argument('--num-workers', type=int, default=0)
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--lr', type=float, default=1e-1)
    parser.add_argument('--momentum', type=float, default=0.9)
    parser.add_argument('--weight-decay', type=float, default=1e-4)
    parser.add_argument('--print-interval', type=int, default=100)
    parser.add_argument('--cuda', type=bool, default=True)
    parser.add_argument('--pretrained-model', type=bool, default=False)
    parser.add_argument('--stem', type=bool, default=False, help='attention stem: True, conv: False')
    parser.add_argument('--seed', type=int, default=123456789)

    parser.add_argument('--distributed', type=bool, default=False)
    parser.add_argument('--gpu-devices', type=int, nargs='+', default=None)
    parser.add_argument('--gpu', type=int, default=None)
    parser.add_argument('--rank', type=int, default=0, help='current process number')
    parser.add_argument('--world-size', type=int, default=1, help='Total number of processes to be used (number of gpus)')
    parser.add_argument('--dist-backend', type=str, default='nccl')
    parser.add_argument('--dist-url', default='tcp://127.0.0.1:3456', type=str)

    # =========================================================================
    parser.add_argument(
        '--log_dir', type=str, default='log',
    )
    parser.add_argument(
        '--checkpoint_dir', type=str, default='checkpoint',
    )
    parser.add_argument(
        '--timestamp', type=str, default='',
        help='If no timestamp given, will generate automatically. For resuming,'
             'manually set the correct timestamp',
    )
    # =========================================================================

    args = parser.parse_args()

    if args.timestamp == '':
        args.timestamp = datetime.now().strftime('%b%d_%H-%M-%S')
    args.checkpoint_dir = os.path.join(args.checkpoint_dir, args.timestamp)
    args.log_dir = os.path.join(args.log_dir, args.timestamp)

    filename = str(args.dataset) + '_' + str(args.model_name) + '_' + str(args.stem)
    logger = get_logger(filename, args)
    logger.info(vars(args))
    fix_seeds(args.seed)

    return args, logger


def fix_seeds(seed=0):
    """Fix random seeds here for pytorch, numpy, and python"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True

    torch.backends.cudnn.benchmark = True
    # torch.backends.cudnn.enabled = False
