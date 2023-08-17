from src.evaluation import initialize_evaluator
from src.common import attach_debugger
from src.wandb_utils import WandbSetup
import argparse
from src.models.model import Model
import wandb


if __name__ == "__main__":
    """
    Some quick evaluation code for OpenAI models.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", type=str, default="eval")
    parser.add_argument("--evaluator", type=str, default="natural-instructions")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--model_id", type=str, default=None)
    WandbSetup.add_arguments(parser, save_default=True, project_default="natural-instructions-multitask")
    args = parser.parse_args()

    if args.debug:
        attach_debugger()

    wandb_setup = WandbSetup.from_args(args)

    if args.model_id is not None:
        model = Model.from_id(model_id=args.model_id)
        evaluator = initialize_evaluator(args.evaluator, "")
        evaluator.wandb = WandbSetup.from_args(args)
        evaluator.max_samples, evaluator.max_tokens = 1000, 50
        evaluator.run(models=[(model, "")])
    else:
        runs = wandb.Api().runs(f"{wandb_setup.entity}/{wandb_setup.project}")
        # for run in runs:
        #     print(run.config.keys())
        #     print(run.config["training_files"])
        #     print(run.config["hyperparams"])
        eval_runs = [run for run in runs if "290" in run.config["training_files"]["filename"]]
        for run in eval_runs:
            print(run.config["training_files"]["filename"])
            print(run.config["training_files"])
            print(run.config["hyperparams"]["n_epochs"])
        eval_runs = [run for run in eval_runs if run.config["hyperparams"]["n_epochs"] == 5]
        
        for run in eval_runs:
            model = Model.from_id(model_id=run.config["fine_tuned_model"])
            evaluator = initialize_evaluator(args.evaluator, "")
            evaluator.wandb = WandbSetup.from_args(args)
            evaluator.manual_wandb_run = run
            print(run.config["training_files"]["filename"])
            print(evaluator.manual_wandb_run.config["training_files"]["filename"])
            evaluator.max_samples, evaluator.max_tokens = 1000, 50
            evaluator.run(models=[(model, "")])
            break