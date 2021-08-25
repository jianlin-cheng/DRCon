import math
import torch
import torch.nn as nn
import torch.nn.functional as F


class block(nn.Module):
    def __init__(
            self, in_channels, intermediate_channels, identity_downsample=None, stride=1, _dilation_rate=1):
        super(block, self).__init__()

        self.conv1 = nn.Conv2d(
            intermediate_channels, intermediate_channels, kernel_size=3, bias=False, padding=2 * _dilation_rate,dilation =_dilation_rate )
        self.ins1 = nn.InstanceNorm2d(intermediate_channels)
        self.elu = nn.ELU()
        self.dropout1 = nn.Dropout(0.15)
        self.conv2 = nn.Conv2d(
            intermediate_channels, intermediate_channels, kernel_size=3, bias=False,dilation =_dilation_rate  )
        self.ins2 = nn.InstanceNorm2d(intermediate_channels)

    def forward(self, x):
        identity = x.clone()
        x = self.conv1(x)
        x = self.ins1(x)
        x = self.elu(x)
        x = self.dropout1(x)
        x = self.conv2(x)
        x = self.ins2(x)
        x += identity
        x = self.elu(x)
        return x


class ResNet(nn.Module):
    def __init__(self, block, layers, image_channels, num_classes):
        super(ResNet, self).__init__()
        self.filter = 48
        self.in_channels = image_channels
        self.conv1 = nn.Conv2d(image_channels, self.filter, kernel_size=1, stride=1, padding=0, bias=False)
        self.ins = nn.InstanceNorm2d(self.filter)
        self.elu = nn.ELU()
        self.layer1 = self._make_layer(
            block, layers[0], intermediate_channels=self.filter, stride=1
        )
        self.last_layer = nn.Conv2d(self.filter, 1, kernel_size=1, stride=1, padding=0, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.conv1(x)
        x = self.ins(x)
        x = self.elu(x)
        x = self.layer1(x)
        x = self.last_layer(x)
        x = self.sigmoid(x)
        return x

    def _make_layer(self, block, num_residual_blocks, intermediate_channels, stride):

        layers = []

        dilation_rate = 1
        for i in range(num_residual_blocks - 1):
            layers.append(block(self.filter, intermediate_channels,_dilation_rate=dilation_rate))
            dilation_rate = dilation_rate * 2
            if dilation_rate >16:
                dilation_rate = 1
        return nn.Sequential(*layers)


def ResNet_custom(img_channel=3, num_classes=1000, _depth=60):
    return ResNet(block, [_depth], img_channel, num_classes)

