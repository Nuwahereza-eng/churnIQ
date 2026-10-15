# UI Redesign Task — ChurnIQ Professional Analytics Dashboard

Act as a senior product designer and frontend engineer specialising in Google-quality web interfaces and Microsoft's Fluent 2 design system.

Redesign my existing Customer Churn Prediction frontend. The current UI is mostly black and grey and looks too plain. I want a polished, light-themed analytics application with a professional colour system, beautiful data visualisations, clear hierarchy, and excellent usability.

## Reference Design Principles

- Google Material Design: https://m3.material.io/
- Microsoft Fluent 2: https://fluent2.microsoft.design/

Use these as design inspiration. Do not copy their logos, proprietary product screens, or branding. Create an original product identity for ChurnIQ.

## 1. Non-Negotiable Requirement

Improve the existing frontend in the current repository.

Before editing:

1. Inspect the existing codebase.
2. Identify the frontend framework, routes, components, CSS system, API client, charts, and current page layouts.
3. Identify existing working features and preserve them.
4. Reuse existing dependencies where reasonable.
5. Do not replace the entire project unnecessarily.

Do not modify or retrain the machine-learning model simply to change the UI.

## 2. Visual Direction

Create a bright, refined, professional analytics dashboard.

### Colour Palette

Use a consistent light theme:

- Main background: `#F8FAFD`
- Main surfaces: `#FFFFFF`
- Primary blue: `#1A73E8`
- Primary hover: `#1558B0`
- Light blue surface: `#E8F0FE`
- Main text: `#202124`
- Secondary text: `#5F6368`
- Borders: `#DADCE0`
- Success: `#188038`
- Warning: `#F9AB00`
- Error: `#D93025`
- Supporting purple: `#9334E6`
- Supporting teal: `#0F9D8A`

Use blue for primary actions and active navigation. Use green, amber, red, purple, and teal selectively for charts, supporting indicators, and meaningful status information.

Do not make every card colourful. Most surfaces should remain white, with colour used intentionally.

Remove the existing black-and-grey appearance. Make light mode the default throughout the application, including charts, dropdowns, inputs, tooltips, and dialogs.

## 3. Typography

Use Google Sans-inspired typography or Inter, with a sensible system-font fallback.

Establish a clear type scale:

- Page titles: 26–30px, semibold.
- Section headings: 18–20px, semibold.
- Metric values: 28–34px, semibold.
- Body text: 14–16px.
- Supporting labels: 12–13px.

Use sentence case, consistent line heights, and readable text colours. Avoid oversized headings and excessive bold text.

## 4. Application Shell

Create a consistent layout with:

### Sidebar

- ChurnIQ logo and name.
- Overview.
- Customer Explorer.
- Predict Churn.
- Batch Predictions.
- Model Performance.
- Insights.
- About the Research.

Use clean line icons from Lucide. Clearly highlight the active page using a pale blue background, blue icon, and blue text.

The sidebar should have comfortable spacing and collapse gracefully on smaller screens.

### Top Bar

- Current page title or breadcrumb.
- Search only if it has a working purpose.
- A compact dataset-status indicator.
- A refresh control if it triggers a real data refresh.
- A user or project menu only if it performs a useful action.

Avoid decorative controls that do nothing.

## 5. Overview Dashboard

Make this the strongest page visually.

At the top, show:

**Customer churn overview**

Supporting text:

> Explore customer retention patterns and model insights from the research dataset.

Include four metric cards:

1. Total customers.
2. Customers churned.
3. Customers retained.
4. Overall churn rate.

Each card should have:

- A small relevant icon.
- A concise label.
- A large value.
- A subtle accent or tinted icon background.
- An optional comparison only if the comparison is computed from valid data.

Do not invent growth percentages or historical comparisons.

Below the metrics, create a balanced responsive grid with:

- A churn distribution chart.
- Churn by contract type.
- Churn by tenure or tenure group.
- Monthly charges by churn status.
- A concise insights section based on actual dataset analysis.

Use Recharts if it is already installed or is the existing charting library. Ensure tooltips, legends, axes, and labels remain readable.

Use varied chart types where appropriate: donut, horizontal bar, stacked bar, and line or area charts only when the underlying data supports them.

Avoid presenting every chart in an identical card.

## 6. Customer Explorer

Create a clean data-table experience with:

- Search.
- Filters.
- Sorting.
- Pagination.
- Clear churn-status badges.
- Well-spaced columns.
- Subtle row dividers.
- Hover states.
- Responsive handling for smaller screens.

Use the actual backend data. Include useful empty states and loading skeletons.

Do not expose identifiers or fields unnecessarily.

## 7. Predict Churn Page

Design a professional prediction form with clearly grouped sections:

- Customer information.
- Contract and billing.
- Services and support.
- Payment details.

Use consistent labels, helper text, input heights, dropdowns, and validation states.

The primary action should be a prominent blue button labelled **Predict churn**.

After a successful API response, show a clear result panel containing:

- Predicted outcome.
- Estimated churn probability, if supported by the model.
- A visual probability indicator.
- A short explanation of the result.
- A clear disclaimer that this is a model estimate, not a guaranteed outcome.

Use green or red carefully and always pair colours with text.

Preserve the existing model's required feature schema. Do not fabricate predictions.

## 8. Model Performance

Build a research-quality evaluation page featuring:

- Algorithm comparison table.
- Metric cards for the selected model.
- Confusion matrix.
- ROC curve.
- Precision-recall curve where available.
- Explanation of the selected evaluation criteria.
- Dataset split and model methodology.

Use actual computed results. If a metric is missing, display an honest unavailable state.

Make this page visually consistent with the overview while keeping charts easy to compare.

## 9. Insights Page

Use a clean editorial dashboard layout with:

- Churn by contract type.
- Churn by tenure.
- Churn by service type.
- Churn by payment method.
- Feature importance where available.
- Short, data-supported observations.

Use a restrained palette and clear chart annotations. Do not imply that correlation or feature importance proves causation.

## 10. Component Design System

Create reusable design tokens for:

- Colours.
- Typography.
- Spacing.
- Borders.
- Corner radii.
- Shadows.
- Focus states.

Use a consistent spacing scale based on multiples of 4px.

Use:

- Card radius around 12–16px.
- Input and button radius around 8–10px.
- Subtle borders.
- Soft, restrained shadows.
- Clear focus rings.
- Consistent button heights.

Prefer white cards with fine borders over dark surfaces or heavy shadows.

Avoid excessive rounded pills, giant empty spaces, excessive gradients, glassmorphism, and generic AI dashboard aesthetics.

## 11. Micro-Interactions

Add subtle, purposeful interactions:

- Smooth but restrained hover transitions.
- Sidebar active-state transitions.
- Button hover and focus states.
- Loading skeletons.
- Toast messages for completed actions or errors.
- Clear feedback when filters change.
- Accessible dropdown and dialog interactions.

Do not add animations that interfere with reading charts or using forms.

## 12. Accessibility and Responsive Design

- Maintain sufficient text and control contrast.
- Use semantic HTML.
- Provide keyboard navigation.
- Add accessible labels to inputs and charts where appropriate.
- Do not rely on colour alone to communicate churn status.
- Ensure layouts work on desktop, tablet, and mobile.
- Prevent horizontal overflow.
- Support zoom without clipping content.

## 13. Functional Integrity

The redesign must preserve:

- API integration.
- Existing model predictions.
- Actual dataset statistics.
- Batch prediction functionality.
- Model evaluation results.
- Navigation and routing.
- Error handling and loading states.

Do not replace real backend values with hard-coded sample values.

Do not create a static mockup. The result must remain a functional application.

## 14. Implementation Workflow

1. Inspect the existing frontend and identify the files responsible for the current appearance.
2. Establish the colour and typography tokens.
3. Redesign the application shell and navigation.
4. Redesign the overview dashboard.
5. Apply the design system to the remaining pages.
6. Improve charts, tables, forms, loading states, and error states.
7. Test existing API integration and prediction functionality.
8. Run the production build and fix errors.
9. Inspect the application at desktop and mobile widths.
10. Summarise the files changed, improvements made, tests performed, and any remaining issues.

Do not stop after creating a design plan. Implement the changes in the existing project and verify them.

## Definition of Done

The final interface should look like a carefully designed modern analytics product: light, polished, colourful in a restrained way, easy to navigate, responsive, and consistent across every page.

The interface must be visually improved without breaking the actual machine-learning functionality.

**Start by inspecting the repository, then implement the redesign.**
