
import torch
import torch.nn as nn


class AquaGuardMTNN(nn.Module):

    def __init__(self, input_size=15):

        super(AquaGuardMTNN, self).__init__()

        # Shared feature extraction network
        self.shared = nn.Sequential(

            nn.Linear(input_size, 128),
            nn.ReLU(),

            nn.Dropout(0.20),

            nn.Linear(128, 64),
            nn.ReLU()
        )

        # Output 1: Fault diagnosis
        self.fault_head = nn.Linear(64, 3)

        # Output 2: Remaining useful life
        self.rul_head = nn.Sequential(
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

        # Output 3: Anomaly detection
        self.anomaly_head = nn.Linear(64, 1)

        # Output 4: Cleaning verification
        self.cleaning_head = nn.Linear(64, 3)

    def forward(self, x):

        features = self.shared(x)

        return {
            "fault": self.fault_head(features),

            "rul": self.rul_head(features).squeeze(1),

            "anomaly": self.anomaly_head(features).squeeze(1),

            "cleaning": self.cleaning_head(features)
        }


if __name__ == "__main__":

    model = AquaGuardMTNN(input_size=15)

    # Test with one batch of 32 samples
    sample = torch.randn(32, 15)

    output = model(sample)

    print("AquaGuard MTNN created successfully!")

    for task, prediction in output.items():
        print(task, prediction.shape)
