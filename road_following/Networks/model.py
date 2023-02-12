import torchvision
import torch


class ResNet18:
    def __init__(self, num_classes = 15, weight_file = None, device = "cuda:0"):
        self.num_classes = num_classes
        self.weight_file = weight_file
        self.device = device
        self.model = torchvision.models.resnet18(pretrained=False)
        self.model.conv1 = torch.nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.model.fc = torch.nn.Linear(512, self.num_classes)

        self.model.load_state_dict(torch.load(self.weight_file, self.device))
        self.model = self.model.to(device)
        self.model = self.model.eval()
        
    def run(self, image):
        """_summary_
        Args:
            image (_type_): (3, 480, 640) & torch tensor type
        Return:
            tensor([[-0.0044, -0.0038, -0.0047,  0.0032, -0.0181,  0.0203,  0.9990,  0.0039,
         -0.0147,  0.0077, -0.0011,  0.0110, -0.0056,  0.0161,  0.0046]],
            => 15 classes score
        """

        return self.model(image)
