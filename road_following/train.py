import torch
import torch.optim as optim
import torch.nn.functional as F
import torchvision.models as models
from Dataset.dataset import RFDataset
from utility import train_test_split, DatasetLoader

NUM_EPOCHS = 30
BEST_MODEL_PATH = './model_weight_file/best_steering_model_0116.pth'
best_loss = 1e9
learning_rate = 1e-3
rfdataset_path = "/hdd/woonho/autonomous_driving/0115/"
    
dataset = RFDataset(rfdataset_path)

train_dataset, test_dataset = train_test_split(dataset)

train_loader = DatasetLoader(train_dataset)
test_loader = DatasetLoader(test_dataset)

print("Data Load Complete!")
print("-------------------------")


model = models.resnet18(pretrained=True)
model.conv1 = torch.nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
model.fc = torch.nn.Linear(512, 15)

device = "cuda:2" if torch.cuda.is_available() else "cpu"
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