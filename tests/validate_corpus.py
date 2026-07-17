import os
import sys

# Add the project root directory to sys.path so we can import slopcheck
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from slopcheck.scorer import analyze


def main() -> None:
    human_dir = os.path.join("tests", "corpus", "human")
    ai_dir = os.path.join("tests", "corpus", "ai")

    results = []

    # Helper to process a directory
    def process_dir(directory: str, true_label: int) -> None:
        if not os.path.exists(directory):
            print(f"Directory not found: {directory}", file=sys.stderr)
            return

        for filename in sorted(os.listdir(directory)):
            if filename.endswith(".txt"):
                filepath = os.path.join(directory, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()

                analysis = analyze(text)
                score = analysis["total_score"]
                risk_band = analysis["risk_band"]

                # 1 if risk_band is "medium" or "high", else 0
                predicted_label = 1 if risk_band in ("medium", "high") else 0

                results.append({
                    "filename": f"{os.path.basename(directory)}/{filename}",
                    "true_label": true_label,
                    "score": score,
                    "predicted_label": predicted_label
                })

    process_dir(human_dir, 0)
    process_dir(ai_dir, 1)

    if not results:
        print("No test files found in corpus directory.", file=sys.stderr)
        sys.exit(1)

    # Calculate confusion matrix metrics
    tp = sum(1 for r in results if r["true_label"] == 1 and r["predicted_label"] == 1)
    tn = sum(1 for r in results if r["true_label"] == 0 and r["predicted_label"] == 0)
    fp = sum(1 for r in results if r["true_label"] == 0 and r["predicted_label"] == 1)
    fn = sum(1 for r in results if r["true_label"] == 1 and r["predicted_label"] == 0)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    # Print Confusion Matrix
    print("Confusion Matrix:")
    print("                  Predicted Human  Predicted AI")
    print(f"  Actual Human:          {tn:<16}{fp:<12}")
    print(f"  Actual AI:             {fn:<16}{tp:<12}")
    print()

    # Print Metrics
    print("Evaluation Metrics:")
    print(f"  Precision: {precision:.2f}")
    print(f"  Recall:    {recall:.2f}")
    print(f"  F1 Score:  {f1:.2f}")
    print()

    # Print Per-File Summary Table
    print("Per-File Summary:")
    print(f"{'Filename':<35} | {'True Label':<10} | {'Score':<6} | {'Predicted Label':<15}")
    print("-" * 78)
    for r in results:
        true_str = "ai (1)" if r["true_label"] == 1 else "human (0)"
        pred_str = "ai (1)" if r["predicted_label"] == 1 else "human (0)"
        print(f"{r['filename']:<35} | {true_str:<10} | {r['score']:<6.1f} | {pred_str:<15}")
    print()

    # Check Quality Gate
    if f1 < 0.75:
        print(f"QUALITY GATE FAILURE: F1 score {f1:.2f} is less than 0.75.", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"QUALITY GATE PASSED: F1 score {f1:.2f} meets target of >= 0.75.")
        sys.exit(0)


if __name__ == "__main__":
    main()
