# TASK: REBUILD THE CUSTOMER CHURN PROJECT AS A PROFESSIONAL WEB APPLICATION

Act as a senior full-stack software engineer and UI/UX designer. The existing Customer Churn Prediction project currently uses Streamlit at http://localhost:8501/.

I want you to transform it into a clean, modern, professional web application with a dedicated frontend and backend. Do not simply restyle Streamlit.

## 1. Inspect the existing project first

Before making changes:

- Inspect the complete project structure and existing source code.
- Identify the trained machine-learning models, preprocessing pipeline, dataset, evaluation metrics, visualisations, and existing prediction logic.
- Identify how the current application loads models and makes predictions.
- Check the current Python environment and installed dependencies.
- Identify reusable components and functionality that must be preserved.

Do not delete the existing implementation before verifying that its important functionality can be migrated.

## 2. Required technology stack

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui where appropriate
- Recharts for charts
- React Router for navigation
- Lucide icons

### Backend
- Python
- FastAPI
- Pydantic for request and response validation
- Existing pandas and scikit-learn code for data processing and predictions
- Joblib or the existing model-loading mechanism

Use the existing trained model and preprocessing pipeline. Do not rewrite the machine-learning logic unnecessarily.

The frontend must communicate with the backend through REST API endpoints. The browser must never load or execute the Python model directly.

## 3. Product vision

Build a professional analytics platform called **ChurnIQ**.

The application should look like a modern SaaS analytics product suitable for demonstrating a university research project or presenting to a telecommunications business analyst.

Design principles:
- Clean and minimal.
- Professional typography.
- Consistent spacing.
- Clear visual hierarchy.
- Subtle borders and shadows.
- Restrained use of colour.
- Responsive layouts.
- Accessible forms and navigation.
- Useful empty, loading, success, and error states.

Avoid excessive gradients, glowing effects, unnecessary animations, oversized cards, emoji icons, and generic AI-generated dashboard styling.

Use realistic content from the actual dataset and trained model. Never fabricate metrics or prediction results.

## 4. Application layout

Create a responsive application shell with:

- A collapsible left sidebar.
- ChurnIQ logo and application name.
- Main content area.
- Top navigation bar.
- Page title and short description.
- Responsive mobile navigation.
- A consistent design system.

Navigation items:

1. Overview
2. Customer Explorer
3. Predict Churn
4. Batch Predictions
5. Model Performance
6. Insights
7. About the Research

Clearly identify this as a research prototype using the IBM Telco Customer Churn sample dataset.

## 5. Overview dashboard

Create a polished dashboard showing actual, computed information from the loaded dataset.

Include:
- Total customer records.
- Number of churned customers.
- Number of customers who stayed.
- Overall churn percentage.
- Churn distribution chart.
- Churn by contract type.
- Churn patterns by tenure.
- Relevant monthly-charge comparisons.
- A small recent-analysis or dataset summary section.

All statistics and charts must be generated from actual data through the backend.

Use meaningful chart titles, legends, labels, tooltips, and responsive sizing.

Do not label sample dataset statistics as live telecom company statistics.

## 6. Customer Explorer

Create a searchable and filterable customer table.

Requirements:
- Pagination.
- Search by customer identifier when available.
- Filters for contract type, tenure range, internet service, and churn status.
- Sortable columns.
- Loading and error states.
- Clear indication that records originate from a public sample dataset.
- No unnecessary exposure of sensitive information.

Keep table functionality responsive on smaller screens.

## 7. Predict Churn

Create a dedicated prediction page with a professional input form.

Organise inputs into logical sections:
- Customer tenure.
- Contract and billing.
- Internet and telephone services.
- Technical support.
- Payment method.
- Monthly and total charges.

Requirements:
- Use the exact features expected by the existing trained pipeline.
- Validate inputs in both the frontend and backend.
- Provide sensible defaults without implying that the default values represent a real customer.
- Submit the form to the FastAPI backend.
- Display the actual predicted class and estimated churn probability when the model supports probability estimates.
- Show a clear visual distinction between predicted churn and predicted retention.
- Explain that predictions are estimates, not guarantees.
- Display a useful error if the model is unavailable or the request fails.
- Never hard-code prediction results.

Keep the prediction form easy to navigate, with clear labels, help text, and sensible field grouping.

## 8. Batch Predictions

Allow users to upload a CSV containing compatible customer records.

Requirements:
- Provide a downloadable CSV template derived from the model's actual input schema.
- Validate file type, required columns, and values.
- Display validation errors clearly.
- Show a preview of uploaded records.
- Submit valid records to the backend.
- Display the number of processed records and actual prediction results.
- Provide a downloadable CSV containing original rows and appended predictions.
- Include estimated churn probabilities where supported.
- Handle empty files, malformed files, oversized uploads, and incompatible columns gracefully.

Do not crash the application because of an invalid upload.

## 9. Model Performance

Create a research-focused model evaluation page.

Display actual results from the experiments already conducted.

Include:
- Algorithm comparison table.
- Accuracy.
- Precision.
- Recall.
- F1-score.
- ROC-AUC where available.
- Confusion matrix.
- ROC curve where available.
- Precision-recall curve where available.
- Model selection explanation.
- Dataset split and evaluation methodology.
- Relevant model limitations.

Never invent results to populate the charts. If a metric or experiment has not been computed, display a clear unavailable state and implement the required evaluation if appropriate.

Ensure the metrics are associated with the correct model and test set.

## 10. Insights page

Display useful exploratory findings and model explanations.

Include:
- Churn by contract type.
- Churn by tenure group.
- Churn by internet service.
- Churn by payment method.
- Monthly-charge comparisons.
- Model feature importance or permutation importance, if supported.

Use appropriate charts rather than placing every result in a separate oversized card.

Clearly distinguish statistical associations from causal explanations. Do not claim that a feature causes churn simply because it is important to a predictive model.

## 11. FastAPI backend

Create a modular backend with endpoints similar to:

- GET /api/health
- GET /api/overview
- GET /api/customers
- GET /api/model/metrics
- GET /api/insights
- POST /api/predict
- POST /api/predict/batch

Adjust the endpoints to match the existing project and actual frontend requirements.

Requirements:
- Use Pydantic request and response schemas.
- Validate request payloads.
- Load the fitted model and preprocessing pipeline safely.
- Avoid retraining the model on every API request.
- Keep model inference separate from route handlers.
- Return consistent JSON responses.
- Handle exceptions and invalid inputs properly.
- Configure CORS only for the required frontend development and production origins.
- Do not expose filesystem paths, stack traces, secrets, or internal server details.
- Avoid loading the complete dataset repeatedly for each request.

If the existing project already contains reusable data-processing and prediction modules, import them instead of duplicating the logic.

## 12. Frontend architecture

Use a maintainable structure similar to:

frontend/
  src/
    components/
    layouts/
    pages/
    services/
    hooks/
    types/
    lib/

backend/
  app/
    main.py
    api/
    schemas/
    services/
    core/

Keep API calls in a dedicated service layer. Use TypeScript interfaces for API responses and request payloads.

Create reusable components for:
- Metric displays.
- Charts.
- Data tables.
- Form fields.
- Loading indicators.
- Error messages.
- Empty states.
- Page headers.

Do not place the entire application in a single React component.

## 13. Visual quality requirements

Before considering the interface complete:

- Ensure consistent spacing and typography.
- Use a restrained, coherent colour palette.
- Make charts readable and responsive.
- Ensure buttons and navigation work.
- Prevent horizontal overflow.
- Make tables usable on mobile.
- Provide clear focus states and accessible labels.
- Avoid placeholder links and non-functional controls.
- Use realistic sample content only where clearly labelled.
- Ensure every dashboard metric comes from a verified data source.

Aim for the quality of a polished analytics dashboard rather than a basic CRUD template.

## 14. Testing and verification

Preserve and test the existing machine-learning pipeline.

Backend:
- Test health and overview endpoints.
- Test valid and invalid prediction requests.
- Test batch prediction.
- Test missing model and dataset conditions.
- Test input schema validation.

Frontend:
- Test page rendering.
- Test navigation.
- Test prediction form validation.
- Test loading and error states.
- Test API integration.
- Test batch-upload feedback.

Run the frontend and backend, fix build errors, and verify the main user flows.

Do not claim that the application works unless you have actually run and tested it.

## 15. Development workflow

Phase 1: Inspect the existing implementation and document what must be preserved.

Phase 2: Refactor reusable machine-learning functionality into a backend service.

Phase 3: Build the FastAPI backend and verify its endpoints.

Phase 4: Build the React frontend and connect it to the API.

Phase 5: Implement the dashboard, customer explorer, prediction form, batch predictions, and model evaluation pages.

Phase 6: Run tests, fix errors, and verify the complete application.

Phase 7: Update documentation with installation, environment setup, startup commands, testing, and deployment instructions.

Keep the existing Streamlit implementation until the new version has been verified. Once the replacement works, document how to run the new application independently.

## 16. Final deliverables

Deliver:
- A functional React and TypeScript frontend.
- A functional FastAPI backend.
- Integration with the actual trained churn model.
- Working dashboard and prediction functionality.
- Batch CSV prediction if supported by the existing model.
- Automated tests.
- Updated README.
- Separate startup instructions for frontend and backend.
- A summary of completed features and any outstanding limitations.

Begin by inspecting the current workspace and reporting the existing architecture. Then implement the migration incrementally. Do not stop after generating a plan or a set of placeholder files.