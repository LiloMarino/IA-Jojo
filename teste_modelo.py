from pathlib import Path
from tkinter import Tk, filedialog

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torchvision import datasets, models, transforms
from torchvision.models import VGG16_Weights

# Variável para determinar o tamanho das imagens geradas no pré-processamento
image_size = 224  # Você pode ajustar este valor conforme necessário

# Definindo os caminhos
CHAR_FOLDER = Path("Characters")
TEST_FOLDER = CHAR_FOLDER / "Test"
TRAIN_FOLDER = CHAR_FOLDER / "Train"

# Transformações para pré-processamento das imagens
data_transforms = {
    "train": transforms.Compose(
        [
            transforms.RandomResizedCrop(image_size),
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(),
            transforms.RandomRotation(degrees=30),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    ),
    "test": transforms.Compose(
        [
            transforms.Resize(image_size + 32),
            transforms.CenterCrop(image_size),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    ),
}

# Carregando os datasets
image_datasets = {
    "train": datasets.ImageFolder(TRAIN_FOLDER, transform=data_transforms["train"]),
    "test": datasets.ImageFolder(TEST_FOLDER, transform=data_transforms["test"]),
}

class_names = image_datasets["train"].classes
num_classes = len(class_names)


# Função para carregar a imagem
def load_image(image_path):
    image = Image.open(image_path)
    return image


# Função para pré-processar a imagem
def preprocess_image(image):
    preprocess = transforms.Compose(
        [
            transforms.Resize(image_size + 32),
            transforms.CenterCrop(image_size),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ]
    )
    image = preprocess(image).unsqueeze(0)
    return image


# Função para mostrar a imagem com o título
def imshow(image, title=None):
    image = image.numpy().transpose((1, 2, 0))
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    image = std * image + mean
    image = np.clip(image, 0, 1)
    plt.imshow(image)
    if title is not None:
        plt.title(title)
    plt.axis("off")  # Remove os eixos para melhor visualização
    plt.show()


# Função para carregar o modelo
def load_model(num_classes, model_path="model.pth"):
    model = models.vgg16(weights=VGG16_Weights.IMAGENET1K_V1)
    num_ftrs = model.classifier[6].in_features
    model.classifier[6] = nn.Linear(num_ftrs, num_classes)

    # Carregar o estado do modelo com weights_only=True
    model.load_state_dict(
        torch.load(model_path, map_location=torch.device("cpu"), weights_only=True)
    )

    model.eval()
    return model


# Função para classificar a imagem
def classify_image(model, image, class_names):
    with torch.no_grad():
        outputs = model(image)
        _, preds = torch.max(outputs, 1)
        class_name = class_names[preds[0]]
    return class_name


# Carregar o modelo
model = load_model(num_classes)

# Abrir a caixa de diálogo para selecionar a imagem
root = Tk()
root.withdraw()
image_path = filedialog.askopenfilename()
if not image_path:
    print("Nenhuma imagem selecionada.")
else:
    # Carregar e pré-processar a imagem
    image = load_image(image_path)
    image_tensor = preprocess_image(image)

    # Classificar a imagem
    class_name = classify_image(model, image_tensor, class_names)

    # Mostrar a imagem com o nome do personagem no título
    imshow(image_tensor.squeeze(), title=f"Classificado como: {class_name}")
    print(f"A imagem foi classificada como: {class_name}")
