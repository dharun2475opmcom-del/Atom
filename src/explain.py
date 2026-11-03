
import torch
import torch.nn as nn
import numpy as np
import shap
import matplotlib.pyplot as plt

from pathlib import Path

from preprocessing import prepare_data, FEATURES
from model import AquaGuardMTNN


DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)



class CloggedProbability(nn.Module):

    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, x):

        output = self.model(x)

        probabilities = torch.softmax(
            output["fault"],
            dim=1
        )

        # Return 2D output: (batch_size, 1)
        return probabilities[:, 2:3]



def explain_model():

    print("Loading AquaGuard model...")

    train_data, test_data = prepare_data()

    checkpoint = torch.load(
        "models/aquaguard_mtnn.pth",
        map_location=DEVICE,
        weights_only=True
    )

    model = AquaGuardMTNN(
        input_size=checkpoint["input_size"]
    ).to(DEVICE)

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.eval()

    explain_model = CloggedProbability(model).to(DEVICE)
    explain_model.eval()

    # Background data for SHAP
    rng = np.random.default_rng(42)

    background_indices = rng.choice(
        len(train_data["X"]),
        size=100,
        replace=False
    )

    background = torch.tensor(
        train_data["X"][background_indices],
        dtype=torch.float32
    ).to(DEVICE)

    # Explain 100 test samples
    explain_indices = rng.choice(
        len(test_data["X"]),
        size=100,
        replace=False
    )

    explain_samples = test_data["X"][explain_indices]

    explain_tensor = torch.tensor(
        explain_samples,
        dtype=torch.float32
    ).to(DEVICE)

    print("Calculating SHAP values...")

    explainer = shap.GradientExplainer(
        explain_model,
        background
    )

    shap_values = explainer.shap_values(
        explain_tensor
    )

    # Support different SHAP output formats
    if isinstance(shap_values, list):
        shap_values = shap_values[0]

    shap_values = np.asarray(shap_values)

    if shap_values.ndim == 3 and shap_values.shape[-1] == 1:
        shap_values = shap_values[:, :, 0]

    print("SHAP calculation completed!")
    print("SHAP shape:", shap_values.shape)

    # Create output directory
    Path("reports").mkdir(
        parents=True,
        exist_ok=True
    )

    # Global feature importance
    shap.summary_plot(
        shap_values,
        explain_samples,
        feature_names=FEATURES,
        plot_type="bar",
        show=False
    )

    plt.title(
        "AquaGuard - SHAP Feature Importance"
    )

    plt.tight_layout()

    plt.savefig(
        "reports/shap_feature_importance.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    # SHAP beeswarm plot
    shap.summary_plot(
        shap_values,
        explain_samples,
        feature_names=FEATURES,
        show=False
    )

    plt.title(
        "AquaGuard - SHAP Explanation"
    )

    plt.tight_layout()

    plt.savefig(
        "reports/shap_summary.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print("\nSHAP explanation saved successfully!")

    print("reports/shap_feature_importance.png")
    print("reports/shap_summary.png")


if __name__ == "__main__":
    explain_model()
