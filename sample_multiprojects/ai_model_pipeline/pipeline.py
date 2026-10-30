import pickle
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split

API_KEY = "api_key_ai_model_service_12345"

class BadModelPipeline:
    def load_weights(self, path):
        with open(path, "rb") as f:
            model = pickle.load(f)
        return model

    def load_torch_unsafe(self, weights_path):
        weights = torch.load(weights_path, weights_only=False)
        return weights

    def train_epoch(self, model, dataloader):
        total_loss = 0.0
        for batch in dataloader:
            loss = model(batch)
            total_loss += loss
        return total_loss

    def prepare_data(self, X, y):
        return train_test_split(X, y, random_state=None)
