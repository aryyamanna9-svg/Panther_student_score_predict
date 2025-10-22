## Purpose
Short, actionable guidance for AI coding agents working on this small Flask ML demo.

## Big picture
- Single-process Flask app: `app.py` hosts a small web UI (`templates/index.html`) and a `/predict` POST endpoint that returns JSON.
- The model is expected as a pickle named `student_score_model.pkl` (loaded from the repository root in `app.py`). The `model/` folder exists but is currently empty.
- Raw data: `student_performance_dataset.csv` — used to (re)train the model. The app maps model predictions (1/0) to `Pass`/`Fail` strings.

## Key files
- `app.py` — server, request parsing, feature-ordering, model load path, prediction mapping.
- `templates/index.html` — frontend form and JS `fetch('/predict', { method: 'POST', body: formData })`.
- `student_performance_dataset.csv` — columns and example values used during training.

## Developer contract (short)
- Inputs: form-encoded POST to `/predict` with fields: Gender, Study_Hours_per_Week, Attendance_Rate, Past_Exam_Scores, Internet_Access_at_Home, Extracurricular_Activities, Parental_Education_Level.
- Output: JSON { "prediction": "Pass" | "Fail" } on success, or { "error": "..." } on exception.
- Feature ordering/shape must match `feature_columns` in `app.py` (see that list for exact column names).

## Important repository-specific notes (do not miss)
- app.py's feature column list contains explicit one-hot columns for parental education named with this exact text: `Parental_Education_Level_High School` (note the space). Any retrained model must use the identical column names and order.
- The code maps: Gender -> 1 if 'female' else 0; Internet/Extracurricular -> 1 for 'yes' else 0. Parental level is expanded into four columns.
- `student_score_model.pkl` is loaded from repo root via:
  ```py
  model_path = os.path.join(BASE_DIR, "student_score_model.pkl")
  ```
  If you move the model into `model/`, update this path accordingly.

## How to run & debug (Windows PowerShell)
1. Create a virtualenv and install dependencies (example set): Flask, pandas, scikit-learn, numpy
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install flask pandas scikit-learn numpy
```
2. Start the app (debug mode already enabled in `app.py`):
```powershell
python app.py
```
3. Visit http://127.0.0.1:5000/ to use the UI. The UI posts form data to `/predict` and expects JSON.

## Common developer tasks & tips
- Add/replace the model: ensure the pickled object implements `.predict(X)` where `X` is a DataFrame with columns matching `feature_columns` in `app.py`.
- Retrain: use `student_performance_dataset.csv`. Keep the same preprocessing: one-hot parental education into 4 columns, normalize or scale only if you also update the serving code.
- To change the feature set, update `feature_columns` and the front-end form in `templates/index.html` together.
- Error handling: `app.py` returns a JSON error string for exceptions — useful for quick debugging but not for production.

## Tests & CI pointers
- There are no tests currently. Minimal useful tests to add:
  - POST `/predict` happy-path using Werkzeug test client or `requests` against the running app.
  - A serialization contract test that loads `student_score_model.pkl` and runs `.predict` on a DataFrame built from `feature_columns`.

## Where to look first when editing
- If bugs involve input mapping or wrong columns: inspect `app.py` lines where `data` dict is built and `feature_columns` is declared.
- If UI behavior is wrong: check `templates/index.html` form names (they must match `app.py` expected field names).
- If model fails to load: confirm `student_score_model.pkl` exists at repo root or update `model_path`.

---
If anything above is ambiguous or you'd like examples for retraining/small tests, tell me which part to expand.
