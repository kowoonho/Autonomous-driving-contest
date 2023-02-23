import torch
import torch.optim as optim
import torch.nn.functional as F
import torchvision.models as models
from Dataset.dataset import RFDataset
from utility import train_test_split, DatasetLoader
import sys
from pathlib import Path
import os
import argparse

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.abspath(ROOT))

def parse_opt():
    parser = argparse.ArgumentParser(description="RoadFollowing Training")
    parser.add_argument(
        "--data",
        type = str,
        default = ROOT / 'data/road_following_data',
        help = "road_following_image dataset directory",
    )
    parser.add_argument(
        "--epoch",
        type = int,
        default = 30,
        help = "training epoch",
    )

    parser.add_argument(
        "--name",
        type = str,
        default = "best_steering_model",
        help = "BEST_MODEL name",
    )
    parser.add_argument(
        "--learning_rate",
        type = float,
        default = 1e-3,
        help = "Input learning_rate",
    )
    parser.add_argument(
        "--batch_size",
        type = int,
        default=128,
        help = "batch size"
    )
    parser.add_argument(
        "--split",
        type = float,
        default=0.1,
        help = "train test split percent"
    )
    parser.add_argument(
        "--device",
        type = str,
        default= "cuda",
        help = "device name, cuda:0, 1, 2, 3"
    )
    parser.add_argument(
        "--steering",
        type = int,
        default = 15,
        help = "steering range"
        """
        -7, -6, -5, ... , 5, 6, 7 => total : 15
        """
    )
    
    return parser.parse_args()
    
def main(opt):
    NUM_EPOCHS = opt.epoch
    BEST_MODEL_PATH = os.path.join(ROOT, 'model_weight_file', opt.name + ".pth")
    best_loss = 1e9
    learning_rate = opt.learning_rate
    rfdata_path = opt.data
    
    

    dataset = RFDataset(rfdata_path)

    train_dataset, test_dataset = train_test_split(dataset, test_percent = opt.split)

    train_loader = DatasetLoader(train_dataset, batch_size=opt.batch_size)
    test_loader = DatasetLoader(test_dataset)

    print("Data Load Complete!")
    print("-------------------------")


    model = models.resnet18(pretrained=True)
    model.conv1 = torch.nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
    model.fc = torch.nn.Linear(512, opt.steering)

    device = opt.device if torch.cuda.is_available() else "cpu"
    model = model.to(device)


    print("Model Load Complete!")
    print("Device name : {}".format("("+device+")"))
    print("-------------------------")

    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    print("Training Start!")
    print("-------------------------")

    for epoch in range(NUM_EPOCHS):
        
        model.train()
        train_loss = 0.0
        for images, labels in iter(train_loader):
            images = images.to(device)
            labels = labels.to(device, dtype = torch.float32)
            optimizer.zero_grad()
            outputs = model(images)
            loss = F.mse_loss(labels, outputs)
            train_loss += float(loss)
            loss.backward()
            optimizer.step()
        train_loss /= len(train_loader)
        
        model.eval()
        test_loss = 0.0
        for images, labels in iter(test_loader):
            images = images.to(device)
            labels = labels.to(device, dtype = torch.float32)
            
            outputs = model(images)
            loss = F.mse_loss(labels, outputs)
            test_loss += float(loss)
        test_loss /= len(test_loader)
        
        print("Epoch : {} // Training Loss : {}, Test Loss : {}".format(epoch, train_loss, test_loss))
        if test_loss < best_loss:
            torch.save(model.state_dict(), BEST_MODEL_PATH)
            best_loss = test_loss

    print("-------------------------")        
    print("Training Complete!")
    print("-------------------------")
    

if __name__ == '__main__':
    opt = parse_opt()
    main(opt)