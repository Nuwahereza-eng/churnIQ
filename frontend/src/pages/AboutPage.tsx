import { Database, ExternalLink, Layers, ShieldAlert, Target, Workflow, type LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

import { TONES, type Tone } from "@/components/MetricCard";
import { PageHeader } from "@/components/PageHeader";
import { Alert } from "@/components/ui/alert";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const DATASET_URL = "https://github.com/IBM/telco-customer-churn-on-icp4d";

function Block({ title, icon: Icon, tone = "blue", children }: { title: string; icon: LucideIcon; tone?: Tone; children: ReactNode }) {
  return (
    <Card>
      <CardHeader className="flex-row items-center gap-3">
        <span className={`flex size-8 shrink-0 items-center justify-center rounded-lg ${TONES[tone]}`}>
          <Icon className="size-4" aria-hidden />
        </span>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-sm leading-6 text-[#3c4043]">{children}</CardContent>
    </Card>
  );
}

export function AboutPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="About the Research"
        description="Development and Evaluation of a Machine Learning Model for Predicting Customer Churn in the Telecommunications Industry."
      />
      <div className="grid gap-4 lg:grid-cols-2">
        <Block title="Purpose" icon={Target}>
          <p>
            Telecommunications providers lose revenue when subscribers discontinue their services. This undergraduate
            Software Engineering research project investigates whether machine-learning classifiers trained on historical
            customer records can estimate which customers are likely to churn, and presents the results in a web
            application for analysts and retention teams.
          </p>
          <ul className="list-disc space-y-1 pl-5">
            <li>Analyse customer data to identify characteristics associated with churn.</li>
            <li>Develop machine-learning models to predict churn.</li>
            <li>Compare algorithms using appropriate evaluation metrics.</li>
            <li>Present predictions and churn patterns in a web application.</li>
          </ul>
        </Block>
        <Block title="Dataset" icon={Database} tone="teal">
          <p>
            The <strong>IBM Telco Customer Churn</strong> sample describes 7,043 customers of a <strong>fictional</strong>{" "}
            telecom provider offering phone and internet services. It contains account, service and basic demographic
            fields and a binary churn label. It is not data from a real operator, nor from the Ugandan market.
          </p>
          <a
            href={DATASET_URL}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 rounded font-medium text-primary hover:text-primary-hover hover:underline"
          >
            IBM/telco-customer-churn-on-icp4d on GitHub <ExternalLink className="size-3.5" aria-hidden />
          </a>
        </Block>
        <Block title="Method" icon={Workflow} tone="purple">
          <ul className="list-disc space-y-1 pl-5">
            <li>Data validation and cleaning; customerID excluded from modelling.</li>
            <li>scikit-learn pipeline: median imputation and scaling for numeric features, one-hot encoding for categorical ones, fitted on training data only.</li>
            <li>Stratified 80/20 train/test split, fixed random seed.</li>
            <li>Logistic Regression, Decision Tree and Random Forest tuned with 5-fold cross-validation; class weighting for the imbalanced target.</li>
            <li>Model selected by cross-validated ROC-AUC, then calibrated; threshold chosen on training data.</li>
            <li>Single, final evaluation on the held-out test set.</li>
          </ul>
        </Block>
        <Block title="Architecture" icon={Layers} tone="green">
          <ul className="list-disc space-y-1 pl-5">
            <li>
              <strong>Backend:</strong> FastAPI with Pydantic validation, wrapping the project's existing pandas and
              scikit-learn modules. The trained pipeline is loaded once and reused.
            </li>
            <li>
              <strong>Frontend:</strong> React, TypeScript, Vite, Tailwind CSS, Recharts and React Router. The browser only
              calls REST endpoints; it never runs the model.
            </li>
            <li>All figures on every page are computed from the dataset or the saved experiment results.</li>
          </ul>
        </Block>
      </div>
      <Block title="Limitations and responsible use" icon={ShieldAlert} tone="amber">
        <ul className="list-disc space-y-1 pl-5">
          <li>Fictional, single-provider snapshot without dates: findings may not transfer to other markets or periods.</li>
          <li>Important drivers (network quality, complaints, competitor offers) are absent from the data.</li>
          <li>Feature importance and churn-rate differences are associations, not causal effects.</li>
          <li>Predictions are probabilistic estimates for decision support; they must never be used to penalise customers.</li>
          <li>Real-world use would require local data, retraining, fairness checks and compliance with data-protection law.</li>
        </ul>
      </Block>
      <Alert variant="info">
        This is a research prototype. It is not affiliated with IBM or any telecommunications operator.
      </Alert>
    </div>
  );
}
